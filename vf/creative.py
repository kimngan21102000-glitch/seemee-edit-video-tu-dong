"""Luật dựng của skill v2 kiểm được bằng máy (giá trị trong library/brand/tokens.json):
- tự sửa: kéo dài thời gian giữ chữ cho đủ đọc;
- tự thêm: SFX theo sự kiện (tokens.auto_sfx), chuyển cảnh "paper" ở ranh giới chương (preset vox);
- ghi chú sáng tạo: hook, CTA, chương còn thiếu, cảnh protect, nhịp cắt, trộn hệ chữ, âm thanh, hook trùng.
Ghi chú KHÔNG chặn render — in ra (dòng `~`) và ghi vào qa.json (`creative`)."""
from __future__ import annotations

from pathlib import Path

from vf.edl import Effect, Graphic, Variant, output_duration
from vf.tokens import default_preset, load_tokens, preset

SFX_EXTS = (".wav", ".mp3", ".m4a", ".ogg")
CTA_SOFT_FROM, CTA_LATE = 0.6, 0.85  # CTA mềm trong 60–85 % thời lượng, ngoài CTA cuối
CTA_WORDS = ("giỏ", "bấm", "mua", "đặt", "link", "xem ngay", "săn")
MAX_WORDS_PER_S = 3.5
MAX_TEXT_AT_ONCE = 2
CHAPTER_ALIASES = {"problem": "pain", "solution": "benefit"}
# graphic → khoá trong tokens.auto_sfx
SFX_KEY_FOR_GRAPHIC = {"callout": "circle", "collage": "paper", "counter": "day_counter", "light_timer": "light_timer",
                       "whiten": "tooth_morph", "end_card": "end_card", "wipe": "wipe", "shade": "shade",
                       "teeth": "teeth", "paper_swipe": "paper", "steps": "light_timer", "live_cta": "end_card",
                       "nope": "circle", "cost_compare": "shade", "refill": "end_card",
                       "versus": "shade", "size_fit": "end_card", "compartments": "day_counter",
                       "badge": "end_card"}


def _timing() -> dict:
    return load_tokens()["timing"]


def piece_spans(v: Variant) -> list[tuple[float, float, object, str | None]]:
    """(đầu, cuối theo timeline output, đoạn, chương) cho hook + segments. Hook không ghi chương = "hook";
    đoạn không ghi chương = cùng chương với đoạn trước."""
    out, t, prev = [], 0.0, None
    for i, p in enumerate(v.pieces()):
        ch = p.chapter or ("hook" if i == 0 else prev)
        ch = CHAPTER_ALIASES.get(ch, ch)
        out.append((t, t + p.duration, p, ch))
        t += p.duration
        prev = ch
    return out


def chapter_cuts(v: Variant) -> list[float]:
    """Thời điểm (output) đổi chương — nơi preset đặt chuyển cảnh."""
    spans = piece_spans(v)
    return [a for (a, _, _, ch), (_, _, _, prev) in zip(spans[1:], spans) if ch != prev]


def hold_needed(text: str, sub: str = "") -> float:
    t = _timing()
    words = len((text + " " + sub).replace("*", " ").replace("[", " ").replace("]", " ").split())
    return max(t["min_hold_s"], t["hold_base_s"] + t["hold_per_word_s"] * words)


def text_limit(v: Variant, t: float, text_sources: set[str] | None = None,
               text_free: dict[str, list[tuple[float, float]]] | None = None) -> float:
    """Chữ bắt đầu ở `t` (output) được hiện tới đâu: hết đoạn đang chứa nó (không vắt qua điểm cắt), và với nguồn có
    chữ in sẵn thì tới hết khoảng `text_free` đang chứa nó (không lấn vào chữ của nguồn) — feedback lo-03."""
    for a, b, p, _ in piece_spans(v):
        if a - 1e-6 <= t < b:
            limit = b
            if text_sources and p.source in text_sources:
                src_t = p.start + (t - a)
                ends = [fe for fs, fe in (text_free or {}).get(p.source, []) if fs - 1e-6 <= src_t <= fe]
                limit = min(limit, a + (max(ends) - p.start)) if ends else a
            return limit
    return output_duration(v)


def auto_fix(v: Variant, text_sources: set[str] | None = None,
             text_free: dict[str, list[tuple[float, float]]] | None = None) -> tuple[Variant, list[str]]:
    """Kéo dài chữ hiện quá ngắn cho đủ đọc: max(1,2 s; 0,6 + 0,25 × số từ) — nhưng KHÔNG vắt qua điểm cắt và không
    lấn ra ngoài text_free (lỗi lo-03: "TRÀ SỮA, CÀ PHÊ" đè chữ in sẵn của cảnh sau). Không đủ chỗ → ghi chú rút chữ."""
    fixes, overlays = [], []
    for o in v.overlays:
        need = hold_needed(o.text, o.sub)
        if o.end - o.start < need - 1e-6:
            limit = max(o.end, text_limit(v, o.start, text_sources, text_free))
            new_end = min(limit, o.start + need)
            if new_end > o.end + 0.05:
                fixes.append(f"tự sửa: giữ chữ \"{o.text}\" {o.end - o.start:.1f} → {new_end - o.start:.1f} s")
                o = o.model_copy(update={"end": round(new_end, 3)})
            if new_end < o.start + need - 0.05:
                fixes.append(f"đọc không kịp: \"{o.text}\" chỉ hiện được {new_end - o.start:.1f} s (cần {need:.1f} s, "
                             "hết cảnh/hết khoảng không chữ) — rút chữ, bỏ dòng phụ hoặc đặt sớm hơn")
        overlays.append(o)
    return v.model_copy(update={"overlays": overlays}), fixes


def lint_cuts(v: Variant, words_by_source: dict, videos: list | None = None) -> list[str]:
    """Lỗi edit nhỏ ở điểm cắt (lo-03): cắt giữa từ, mất chữ đầu câu ('~~Ai~~ mà nằm vùng…'), đứng hình ở mép đoạn."""
    notes = []
    pieces = v.pieces()
    for i, p in enumerate(pieces):
        words = words_by_source.get(p.source) or []
        contiguous = i > 0 and pieces[i - 1].source == p.source and abs(pieces[i - 1].end - p.start) < 0.05
        txt = lambda w: (w.text if hasattr(w, "text") else w["text"]).strip()  # noqa: E731
        st = lambda w: w.start if hasattr(w, "start") else w["start"]  # noqa: E731
        en = lambda w: w.end if hasattr(w, "end") else w["end"]  # noqa: E731
        for w in words:
            if st(w) + 0.03 < p.start < en(w) - 0.03:
                notes.append(f"cắt giữa từ: đoạn {i} bắt đầu {p.start:.2f} s trong chữ \"{txt(w)}\" ({st(w):.2f}–{en(w):.2f})")
            if st(w) + 0.03 < p.end < en(w) - 0.03:
                notes.append(f"cắt giữa từ: đoạn {i} kết thúc {p.end:.2f} s trong chữ \"{txt(w)}\" ({st(w):.2f}–{en(w):.2f})")
        prev = [w for w in words if en(w) <= p.start + 0.03]
        first = [w for w in words if p.start - 0.03 <= st(w) < p.end]
        sentence_start = bool(first) and txt(first[0])[:1].isupper()  # bộ phiên âm viết hoa đầu câu (dù thiếu dấu chấm)
        if not contiguous and not sentence_start and prev and p.start - en(prev[-1]) < 0.1 and not txt(prev[-1]).endswith((".", "?", "!", ","))                 and en(prev[-1]) - st(prev[-1]) < 0.6 and p.start - st(prev[-1]) < 0.6:
            notes.append(f"mất chữ đầu câu: đoạn {i} ({p.start:.2f} s) bỏ \"{txt(prev[-1])}\" ngay trước — lùi mép về "
                         f"{st(prev[-1]):.2f} s hoặc về đầu câu")
        if videos and i < len(videos):
            pv = videos[i]
            if pv.head > 0.15 or pv.tail > 0.15:
                notes.append(f"đứng hình: đoạn {i} giữ khung {max(pv.head, pv.tail):.2f} s ở mép (mẩu cảnh khác) — dời mép "
                             "đoạn về đúng điểm chuyển cảnh")
    return notes


def transition_graphics(v: Variant) -> list[Graphic]:
    """(Đã bỏ — feedback lo-04) chuyển cảnh giờ làm bằng xfade trong ffmpeg (vf/render.py: plan_transitions)."""
    return []


def find_sfx(sfx_dir: Path, name: str) -> str | None:
    """Đường dẫn tương đối với library/brand (render.resolve_asset tìm theo brand dir)."""
    for ext in SFX_EXTS:
        p = Path(sfx_dir) / f"{name}{ext}"
        if p.exists():
            return f"{Path(sfx_dir).name}/{p.name}"
    return None


def auto_sfx(v: Variant, sfx_dir: Path) -> list[Effect]:
    """SFX tự thêm theo sự kiện (tokens.auto_sfx) — ít và nhỏ (feedback lo-03): chỉ đồ hoạ/chuyển cảnh quan trọng
    kéo dài ≥ min_event_s, cách nhau ≥ min_gap_s; khoá null (chữ hiện, zoom, ranh giới chương) = không gắn.
    Tắt hẳn khi `v.sfx_auto = False` hoặc preset có auto_sfx false (ugc)."""
    if not v.sfx_auto or not preset(v.preset).get("auto_sfx", True) or not Path(sfx_dir).is_dir():
        return []
    names = load_tokens()["auto_sfx"]
    min_event, min_gap = names.get("min_event_s", 0.5), names.get("min_gap_s", 2.0)
    cues: list[tuple[float, str | None]] = []
    cues += [(e.at, names.get("zoom")) for e in v.effects if e.kind in ("zoom_to", "zoom_punch")]
    cues += [(t, names.get("chapter")) for t in chapter_cuts(v)]
    for g in v.graphics:
        if g.end - g.start < min_event:
            continue
        if g.kind == "kinetic":
            cues.append((g.start, names.get("kinetic_word")))  # một cú đập ở đầu, không đập từng chữ
        elif g.kind in SFX_KEY_FOR_GRAPHIC:
            cues.append((g.start, names.get(SFX_KEY_FOR_GRAPHIC[g.kind])))
    cues += [(o.start, names.get("text_in")) for o in v.overlays]
    taken = [e.at for e in v.effects if e.kind == "sfx"]  # SFX khai tay luôn giữ
    out: list[Effect] = []
    for at, name in sorted(cues, key=lambda c: c[0]):
        if not name:
            continue
        asset = find_sfx(sfx_dir, name)
        if asset is None or any(abs(at - t) < min_gap for t in taken):
            continue
        out.append(Effect(kind="sfx", at=round(at, 3), asset=asset))
        taken.append(at)
    return out


def _is_cta(text: str, style: str) -> bool:
    return style == "cta" or any(w in text.lower() for w in CTA_WORDS)


def lint_variant(v: Variant) -> list[str]:
    """Ghi chú sáng tạo (sau khi đã gộp cam kết tự động, bỏ chữ ngoài text_free và tự sửa)."""
    tm = _timing()
    notes: list[str] = []
    dur = output_duration(v)
    spans = piece_spans(v)

    # hook: phần tử chữ/đồ hoạ đầu tiên
    firsts = [o.start for o in v.overlays] + [g.start for g in v.graphics if g.kind != "paper_swipe"]
    if not firsts or min(firsts) > tm["first_element_by_s"] + 1e-6:
        notes.append(f"hook: chưa có chữ/đồ hoạ trong {tm['first_element_by_s']} s đầu "
                     "(bỏ qua nếu nguồn đã có chữ in sẵn ở hook)")

    # CTA: có CTA, có CTA mềm giữa video, có CTA trong mấy giây cuối
    cta_kinds = ("end_card", "live_cta")
    ctas = [o.start for o in v.overlays if _is_cta(f"{o.text} {o.sub}", o.style)] + [g.start for g in v.graphics if g.kind in cta_kinds]
    ends = [o.end for o in v.overlays if _is_cta(f"{o.text} {o.sub}", o.style)] + [g.end for g in v.graphics if g.kind in cta_kinds]
    if not ctas:
        notes.append("CTA: chưa có thẻ CTA nào")
    else:
        if dur > 15 and not any(CTA_SOFT_FROM * dur <= t <= CTA_LATE * dur for t in ctas):
            notes.append(f"CTA: chỉ ở cuối — thêm một CTA mềm trong khoảng {CTA_SOFT_FROM * dur:.0f}–{CTA_LATE * dur:.0f} s")
        if not any(e >= dur - tm["end_cta_window_s"] for e in ends):
            notes.append(f"CTA: {tm['end_cta_window_s']:.0f} s cuối chưa có CTA/end_card")

    # đọc kịp, số khối chữ cùng lúc
    for o in v.overlays:
        words = len((o.text + " " + o.sub).split())
        if words / max(0.1, o.end - o.start) > MAX_WORDS_PER_S:
            notes.append(f"đọc không kịp: \"{o.text}\" {words} từ trong {o.end - o.start:.1f} s")
    for o in v.overlays:
        at_once = sum(1 for p in v.overlays if p.start <= o.start < p.end)
        if at_once > MAX_TEXT_AT_ONCE:
            notes.append(f"quá nhiều chữ cùng lúc ({at_once}) ở {o.start:.1f} s")
            break

    # nhịp cắt: cảnh ngắn, cảnh protect, cắt ngay sau khi chữ hiện
    for a, b, p, _ in spans:
        if not p.rapid and b - a < tm["scene_min_s"] - 1e-6:
            notes.append(f"nhịp: đoạn {a:.1f}–{b:.1f} s ngắn hơn {tm['scene_min_s']} s (ghi rapid nếu cố ý)")
        if p.protect and b - a < tm["protect_min_s"] - 1e-6:
            notes.append(f"cảnh protect {a:.1f}–{b:.1f} s ngắn hơn {tm['protect_min_s']} s — để cảnh gốc chạy trọn")
        if p.protect and any(o.position == "center" and o.start < b and a < o.end for o in v.overlays):
            notes.append(f"chữ giữa khung đè cảnh protect {a:.1f}–{b:.1f} s (miệng/răng) — dời lên trên/xuống dưới")
    cuts = [a for a, _, _, _ in spans[1:]]
    for o in v.overlays:
        if any(o.start < c < o.start + tm["no_cut_after_text_s"] for c in cuts):
            notes.append(f"cắt cảnh ngay sau khi chữ \"{o.text}\" hiện (< {tm['no_cut_after_text_s']} s)")
    # (bỏ luật "đổi nhịp mỗi ≤ 4 s" — feedback lo-04: zoom chèn vào để đổi nhịp gây giật cục)

    # đủ ý: chương còn thiếu
    check = load_tokens()["content_checklist"]
    chapters = {"hook"} | {ch for _, _, p, ch in spans if p.chapter}  # đoạn mở đầu luôn là hook
    if not any(p.chapter for _, _, p, _ in spans):
        notes.append("đủ ý: chưa ghi `chapter` cho đoạn nào — không kiểm được nỗi đau/lợi ích/hiệu quả/bằng chứng/nhanh/tiết kiệm")
    else:
        missing = [check["labels"][c] for c in check["required"] if c not in chapters]
        if missing:
            notes.append(f"đủ ý: còn thiếu {', '.join(missing)}")

    # thứ tự nội dung (feedback lo-04): đầu video dồn vào nỗi đau/lợi ích → hiệu quả → trước/sau;
    # tiện ích phụ (extra: du lịch, sạc, hộp) để sau hiệu quả/bằng chứng, ngay trước CTA
    first_res = min((a for a, _, p, ch in spans if ch in ("result", "proof")), default=None)
    last_res = max((a for a, _, p, ch in spans if ch in ("result", "proof")), default=None)
    first_extra = min((a for a, _, p, ch in spans if ch == "extra"), default=None)
    if first_res is not None and first_res > 0.45 * dur:
        notes.append(f"thứ tự: hiệu quả/bằng chứng xuất hiện muộn ({first_res:.0f} s / {dur:.0f} s) — đưa lên nửa đầu video")
    if first_extra is not None and last_res is not None and first_extra < last_res:
        notes.append(f"thứ tự: tiện ích phụ (extra) ở {first_extra:.0f} s đứng trước hiệu quả/bằng chứng — chỉ giữ khi nằm trong "
                     "chuỗi liệt kê khen, không thì bỏ (lo-05)")

    # độ dài mặc định (brief có target thì CLI kiểm ±10%)
    if not v.cutdown_of and not (tm["length_min_s"] * (1 - tm["length_tolerance"]) <= dur
                                 <= tm["length_max_s"] * (1 + tm["length_tolerance"])):
        notes.append(f"độ dài {dur:.0f} s ngoài khoảng ưu tiên {tm['length_min_s']}–{tm['length_max_s']} s")

    # một hệ chữ theo preset
    name = v.preset or default_preset()
    ostyle = preset(name).get("overlay_style", "lower")  # lower | vox | plain (tokens.presets)
    body = [o for o in v.overlays if not _is_cta(o.text, o.style)]  # thẻ CTA được dùng kiểu riêng
    mixed = {o.style for o in body if (o.style == "vox") != (ostyle == "vox") and o.style in ("vox", "lower")}
    if ostyle == "plain":
        mixed |= {o.style for o in body if o.style in ("lower", "vox")}
    if mixed:
        notes.append(f"trộn hệ chữ: preset {name} nhưng có chữ kiểu {', '.join(sorted(mixed))}")

    if not v.music and not any(e.kind == "sfx" for e in v.effects):
        notes.append("âm thanh: không có nhạc nền và SFX (chạy `vf make-sfx` hoặc thêm file vào library/brand/sfx/ hay profiles/<hồ sơ>/brand/sfx/)")
    return notes


def lint_batch(variants: list[Variant]) -> dict[str, list[str]]:
    """Biến thể render cùng lúc mà trùng đoạn hook → không phải phương án test khác nhau."""
    out: dict[str, list[str]] = {}
    for i, a in enumerate(variants):
        for b in variants[:i]:
            if a.hook.source != b.hook.source:
                continue
            inter = min(a.hook.end, b.hook.end) - max(a.hook.start, b.hook.start)
            if inter > 0.5 * min(a.hook.duration, b.hook.duration):
                out.setdefault(a.id, []).append(f"hook trùng với {b.id} — đổi câu/khung hình mở đầu")
    return out
