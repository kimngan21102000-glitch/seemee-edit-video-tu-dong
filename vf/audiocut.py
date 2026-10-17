"""Cắt tiếng sạch (feedback lo-04: "dính mẩu tiếng thừa" ở điểm cắt): mốc giờ từng từ của bộ phiên âm lệch ±50 ms
so với tiếng thật, nên mép đoạn "đúng ranh giới từ" vẫn lọt nửa âm tiết. Đo năng lượng âm thanh thật quanh mép
đoạn và dời mép về chỗ lặng nhất gần đó."""
from __future__ import annotations

import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np

SR = 16000
FRAME_S = 0.01  # cửa sổ đo 10 ms
SNAP_WINDOW_S = 0.25  # tìm chỗ lặng trong ±250 ms quanh mép (KOL nói liền, ít khoảng ngắt)
SPEECH_DB = -26.0  # mép đoạn to hơn mức này (so với đỉnh file) = đang có giọng → dính tiếng; dưới = thở/tiếng nền


@lru_cache(maxsize=8)
def _pcm(src: str) -> np.ndarray:
    """Tiếng mono 16 kHz của cả file nguồn (cache: một nguồn dùng cho nhiều đoạn)."""
    proc = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                          capture_output=True)
    return np.frombuffer(proc.stdout, dtype="<i2").astype(np.float32) / 32768.0


def _rms_db(x: np.ndarray, ref: float) -> np.ndarray:
    n = int(SR * FRAME_S)
    k = len(x) // n
    if k == 0:
        return np.array([-120.0])
    frames = x[: k * n].reshape(k, n)
    rms = np.sqrt((frames ** 2).mean(axis=1)) + 1e-9
    return 20 * np.log10(rms / ref)


def edge_level_db(src: Path, t: float) -> float:
    """Mức tiếng (dB so với đỉnh 99% của file) trong 20 ms quanh điểm t."""
    x = _pcm(str(src))
    ref = float(np.percentile(np.abs(x), 99)) + 1e-9 if len(x) else 1.0
    a, b = max(0, int((t - 0.01) * SR)), int((t + 0.01) * SR)
    return float(_rms_db(x[a:b], ref).max()) if b > a else -120.0


INWARD_S = 0.06  # chỉ được dời mép vào trong đoạn tối đa 60 ms — không ăn mất chữ (lo-04: từng mất chữ "lại")


def snap(src: Path, t: float, window: float = SNAP_WINDOW_S, before: float | None = None,
         after: float | None = None) -> float:
    """Dời t về giữa cửa sổ 10 ms lặng nhất trong [t - before, t + after] (mặc định ±window), ưu tiên gần t."""
    x = _pcm(str(src))
    if not len(x):
        return t
    before = window if before is None else before
    after = window if after is None else after
    ref = float(np.percentile(np.abs(x), 99)) + 1e-9
    a = max(0, int((t - before) * SR))
    b = min(len(x), int((t + after) * SR))
    db = _rms_db(x[a:b], ref)
    # mức to nhất trong ±20 ms quanh mỗi vị trí: điểm cắt phải nằm hẳn trong khoảng lặng, không sát mép giọng
    pad = np.pad(db, 2, constant_values=db.max() if len(db) else 0)
    db = np.max(np.stack([pad[k:k + len(db)] for k in range(5)]), axis=0)
    centers = a / SR + (np.arange(len(db)) + 0.5) * FRAME_S
    score = db + 2.0 * np.abs(centers - t) / max(before, after)  # phạt nhẹ khi dời xa
    return round(float(centers[int(np.argmin(score))]), 3)


def lint_audio_edges(v, sources: dict[str, Path]) -> list[str]:
    """Mép đoạn rơi vào lúc đang có giọng (không nối liền đoạn kề) → báo dính tiếng."""
    notes = []
    pieces = v.pieces()
    for i, p in enumerate(pieces):
        src = sources.get(p.source)
        if src is None:
            continue
        joined_prev = i > 0 and pieces[i - 1].source == p.source and abs(pieces[i - 1].end - p.start) <= 0.05
        joined_next = i + 1 < len(pieces) and pieces[i + 1].source == p.source and abs(pieces[i + 1].start - p.end) <= 0.05
        for side, t, joined in (("đầu", p.start + p.mute_head, joined_prev), ("cuối", p.end - p.mute_tail, joined_next)):
            if joined:
                continue
            lv = edge_level_db(src, t)
            if lv > SPEECH_DB:
                notes.append(f"dính tiếng: đoạn {i} {side} {t:.2f} s đang có giọng ({lv:.0f} dB) — "
                             f"chạy `vf snap` hoặc dời mép về {snap(src, t):.2f} s")
    return notes


HOOK_MAX_S = 3.0
MUTE_MAX_S = 0.08  # nói liền, không có khoảng lặng: tắt tiếng tối đa 80 ms ở mép (không ăn chữ của đoạn)
MUTE_DIP_DB = 8.0  # chỗ hở giữa hai chữ phải nhỏ hơn mép ít nhất chừng này mới tính là ranh giới
SILENCE_RUN_S = 0.03  # khoảng lặng thật: ≥ 30 ms liền dưới SPEECH_DB


def _silence_edge(src: Path, t: float, before: float, after: float) -> float | None:
    """Tâm khoảng lặng thật (≥ 30 ms dưới SPEECH_DB) gần t nhất trong [t - before, t + after]; None nếu không có.
    Feedback lo-05: mốc phiên âm lệch tới ~0,2 s ("nữa" kêu tới 134,26 s, phiên âm ghi chữ sau bắt đầu 134,12 s) —
    chỉ cắt ở chỗ lặng đo được, không tin ranh giới chữ."""
    x = _pcm(str(src))
    if not len(x):
        return None
    if edge_level_db(src, t) <= SPEECH_DB:  # mép đã nằm trong chỗ lặng (vd đặt tay đúng điểm chuyển cảnh): giữ nguyên
        return round(t, 3)
    ref = float(np.percentile(np.abs(x), 99)) + 1e-9
    lo = max(0, int((t - before) * SR))
    hi = min(len(x), int((t + after) * SR))
    db = _rms_db(x[lo:hi], ref)
    quiet = db <= SPEECH_DB
    need = max(1, round(SILENCE_RUN_S / FRAME_S))
    best, k = None, 0
    while k < len(quiet):
        if quiet[k]:
            j = k
            while j < len(quiet) and quiet[j]:
                j += 1
            if j - k >= need:
                c = lo / SR + (k + j) / 2 * FRAME_S
                if best is None or abs(c - t) < abs(best - t):
                    best = c
            k = j
        else:
            k += 1
    return None if best is None else round(best, 3)


def _stray_mute(src: Path, t: float, inward: int) -> float:
    """Không có khoảng lặng (KOL nói liền): tìm chỗ hở rõ nhất đi VÀO trong đoạn ≤ 80 ms — phần từ mép tới đó là mẩu
    chữ kề lọt vào → độ dài cần tắt tiếng (giữ hình, "khoảng trống âm thanh" để người dùng tự sửa). 0 nếu không thấy."""
    lv = edge_level_db(src, t)
    if lv <= SPEECH_DB:
        return 0.0
    best_t, best = t, lv
    k = 1
    while k * FRAME_S <= MUTE_MAX_S + 1e-9:
        u = t + inward * k * FRAME_S
        lu = edge_level_db(src, u)
        if lu < best - 0.5:
            best_t, best = u, lu
        k += 1
    return round(abs(best_t - t), 3) if best <= lv - MUTE_DIP_DB else 0.0


def snap_variant(vd: dict, sources: dict[str, Path], words_by_source: dict | None = None) -> tuple[dict, list[str]]:
    """Dời mép mọi đoạn (hook + segments) về chỗ lặng gần nhất; đoạn nối liền đoạn kề thì giữ mép chung.
    Có phiên âm (`words_by_source`) thì mép không bao giờ nới qua ranh giới chữ kề; mép rơi vào chỗ nói liền thì
    tắt tiếng mẩu chữ thừa (`mute_head`/`mute_tail`, giữ hình) — feedback lo-05 "để khoảng trống âm thanh".
    Chữ/đồ hoạ/hiệu ứng được quy đổi theo giờ nguồn để không trôi khỏi lời nói."""
    pieces = [vd["hook"]] + vd["segments"]
    old = [(p["start"], p["end"]) for p in pieces]
    new = []
    changes = []
    for i, p in enumerate(pieces):
        src = sources.get(p["source"])
        a, b = p["start"], p["end"]
        jp = i > 0 and pieces[i - 1]["source"] == p["source"] and abs(old[i - 1][1] - a) <= 0.05
        jn = i + 1 < len(pieces) and pieces[i + 1]["source"] == p["source"] and abs(old[i + 1][0] - b) <= 0.05
        if words_by_source is not None:
            # có phiên âm: mép về khoảng lặng thật gần nhất trong ±0,25 s (cả hai phía — mốc chữ lệch tới 0,2 s)
            sa = None if (jp or src is None) else _silence_edge(src, a, SNAP_WINDOW_S, SNAP_WINDOW_S)
            sb = None if (jn or src is None) else _silence_edge(src, b, SNAP_WINDOW_S, SNAP_WINDOW_S)
            na, nb = (sa if sa is not None else a), (sb if sb is not None else b)
        else:
            # mép đầu: lùi sớm được 0,25 s, vào trong ≤ 60 ms; mép cuối: kéo dài được 0,25 s, vào trong ≤ 60 ms
            na = a if (jp or src is None) else snap(src, a, before=SNAP_WINDOW_S, after=INWARD_S)
            nb = b if (jn or src is None) else snap(src, b, before=INWARD_S, after=SNAP_WINDOW_S)
        if src is not None:  # nói liền không có chỗ lặng: dời không giúp gì thì giữ mép gốc (lint sẽ báo)
            if edge_level_db(src, na) >= edge_level_db(src, a) - 1:
                na = a
            if edge_level_db(src, nb) >= edge_level_db(src, b) - 1:
                nb = b
        if i == 0 and nb - na > HOOK_MAX_S:  # hook ≤ 3 s: giữ mép cuối (không mất chữ cuối), lùi mép đầu vào
            na2 = snap(src, nb - HOOK_MAX_S, before=0.0, after=0.2) if src is not None else nb - HOOK_MAX_S
            na = na2 if nb - na2 <= HOOK_MAX_S + 1e-6 else nb - HOOK_MAX_S
        open_edges = ([na] if not jp else []) + ([nb] if not jn else [])
        if i == 0 and src is not None and open_edges and max(edge_level_db(src, t) for t in open_edges) > SPEECH_DB:
            na, nb = a, b  # hook chọn tay: không tìm được chỗ lặng ở cả hai mép thì giữ nguyên (lint báo)
        if nb - na < 0.5:
            na, nb = a, b
        p.pop("mute_head", None)
        p.pop("mute_tail", None)
        if src is not None and words_by_source is not None:
            mh = 0.0 if jp else _stray_mute(src, na, +1)
            mt = 0.0 if jn else _stray_mute(src, nb, -1)
            if mh:
                p["mute_head"] = mh
                changes.append(f"đoạn {i}: tắt tiếng {mh:.2f} s đầu (mẩu chữ kề, nói liền)")
            if mt:
                p["mute_tail"] = mt
                changes.append(f"đoạn {i}: tắt tiếng {mt:.2f} s cuối (mẩu chữ kề, nói liền)")
        new.append((na, nb))
        if abs(na - a) > 0.005 or abs(nb - b) > 0.005:
            changes.append(f"đoạn {i}: {a:.2f}–{b:.2f} → {na:.2f}–{nb:.2f}")

    def offs(spans):
        out, acc = [], 0.0
        for a, b in spans:
            out.append(acc)
            acc += b - a
        return out

    oo, no = offs(old), offs(new)

    def remap(t: float) -> float:
        for i, ((a, b), (na, nb)) in enumerate(zip(old, new)):
            if t <= oo[i] + (b - a) + 1e-6 or i == len(old) - 1:
                src_t = a + (t - oo[i])
                return round(no[i] + min(max(src_t, na), nb) - na, 3)
        return t

    for i, p in enumerate(pieces):
        p["start"], p["end"] = new[i]
    for key in ("overlays", "graphics"):
        for it in vd.get(key, []):
            s, e = remap(it["start"]), remap(it["end"])
            it["start"], it["end"] = s, max(e, s + 0.1)
    for it in vd.get("effects", []):
        it["at"] = remap(it["at"])
    return vd, changes


def snap_file(edl_path: Path, sources: dict[str, Path], words_by_source: dict | None = None) -> list[str]:
    import json

    edl = json.loads(Path(edl_path).read_text(encoding="utf-8"))
    report = []
    for vd in edl.get("variants", []):
        _, ch = snap_variant(vd, sources, words_by_source)
        report += [f"{vd['id']} — {c}" for c in ch]
    Path(edl_path).write_text(json.dumps(edl, ensure_ascii=False, indent=1), encoding="utf-8")
    return report
