"""Dựng một biến thể từ edl bằng ffmpeg."""
from __future__ import annotations

import math
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from functools import lru_cache
from pathlib import Path

from vf.captions import remap_words, words_to_ass
from vf.creative import auto_fix, auto_sfx, chapter_cuts, lint_cuts, lint_variant, transition_graphics
from vf.tokens import load_tokens, preset
from vf.edl import Effect, TextOverlay, Variant, output_duration
from vf.ffutil import run
from vf.paths import BRAND_DIR, CAPTION_STYLE, STYLE_GUIDE
from vf.probe import MediaInfo
from vf.safezone import SAFE
from vf.placement import OPAQUE
from vf.qa import ClaimViolation, check_claims, check_safe_zone, measure_lufs
from vf.scenes import PieceVideo, plan_piece_video
from vf.transcribe import Word

W, H, FPS = 1080, 1920, 30
SOURCE_TARGET_LUFS = -16.0
BROLL_TARGET_LUFS = -26.0  # nguồn không có lời nói: chỉ giảm, không bao giờ tăng (tránh đẩy tiếng ồn nền)
# chuyển cảnh (feedback lo-04: whip/giấy lướt chưa mượt) — xfade chồng 2 đoạn, lấy thêm hình ở 2 bên điểm cắt
# nên thời lượng không đổi; tiếng vẫn cắt thẳng ở đúng điểm cắt
XFADE = {"fade": "fade", "smooth": "smoothleft"}  # tokens.presets.<p>.transition → kiểu xfade
CHAPTER_XFADE_S, JUMP_XFADE_S = 0.3, 0.2
JOIN_FADE_S = 0.04  # nửa của 0.08 s mỗi bên chỗ nối hai nguồn khác nhau
DECLICK_S = 0.025  # feedback lo-04 (dính mẩu tiếng thừa): mép tiếng mềm hơn
FONT_EXTS = (".ttf", ".otf")
DEFAULT_BRAND = BRAND_DIR
DEFAULT_STYLE = CAPTION_STYLE
DEFAULT_STYLE_GUIDE = STYLE_GUIDE


def _filter_path(p: Path) -> str:
    """Đường dẫn an toàn trong filtergraph (Windows có 'G:' và '\\')."""
    s = str(Path(p).resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    return f"'{s}'"


def find_font(brand: Path) -> Path:
    """Font brand theo tokens.json (fonts.main), rồi file .ttf/.otf đầu tiên trong library/brand,
    nếu chưa có thì dùng font hệ thống có dấu tiếng Việt."""
    from vf.tokens import font_file

    if brand and Path(brand).is_dir():
        try:
            chosen = font_file("main", brand)
        except (FileNotFoundError, ValueError):  # ValueError: chưa chọn hồ sơ (vf sheet) → font đầu tiên
            chosen = None
        if chosen:
            return chosen
        fonts = sorted(p for p in Path(brand).rglob("*") if p.suffix.lower() in FONT_EXTS)
        if fonts:
            return fonts[0]
    candidates = [Path("C:/Windows/Fonts/arialbd.ttf"), Path("/Library/Fonts/Arial Bold.ttf"),
                  Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")]
    if shutil.which("fc-match"):
        out = subprocess.run(["fc-match", "-f", "%{file}", "Arial:bold"], capture_output=True, encoding="utf-8", errors="replace").stdout
        if out:
            candidates.insert(0, Path(out))
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError("Không tìm thấy font: hãy bỏ file .ttf/.otf vào library/brand/")


def resolve_asset(name: str, brand: Path) -> Path:
    for base in (Path(brand), Path(brand).parent / "assets", BRAND_DIR, BRAND_DIR.parent / "assets", Path(".")):
        p = base / name
        if p.exists():
            return p
    raise FileNotFoundError(f"Không thấy file '{name}' trong {brand} hoặc library/assets/")


def _is_vertical(info: MediaInfo) -> bool:
    return info.width / info.height <= 0.65


def _fit(label_in: str, label_out: str, info: MediaInfo, i: int) -> list[str]:
    if _is_vertical(info):
        return [f"{label_in}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1{label_out}"]
    # nguồn ngang/vuông: nền blur + hình gốc giữ tỉ lệ ở giữa, không crop mất người nói
    return [
        f"{label_in}split=2[bg{i}][fg{i}]",
        f"[bg{i}]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2[bgb{i}]",
        f"[fg{i}]scale={W}:{H}:force_original_aspect_ratio=decrease[fgs{i}]",
        f"[bgb{i}][fgs{i}]overlay=(W-w)/2:(H-h)/2,setsar=1{label_out}",
    ]


def _between(e: Effect) -> str:
    return f"between(t,{e.at:.3f},{e.at + e.duration:.3f})"


def _focus_expr(e: Effect, axis: int) -> str:
    """Toạ độ điểm zoom theo thời gian: hằng số, hoặc nội suy tuyến tính giữa các keyframe (bám theo răng)."""
    if not e.keyframes:
        return f"{e.focus[axis - 1]:.3f}"
    k = e.keyframes
    expr = f"{k[-1][axis]:.3f}"
    for (t0, *a), (t1, *b) in reversed(list(zip(k, k[1:]))):
        v0, v1 = a[axis - 1], b[axis - 1]
        lerp = f"{v0:.3f}+({v1 - v0:.3f})*(t-{e.at + t0:.3f})/{max(t1 - t0, 1e-3):.3f}"
        expr = f"if(lt(t,{e.at + t1:.3f}),{lerp},{expr})"
    return f"if(lt(t,{e.at + k[0][0]:.3f}),{k[0][axis]:.3f},{expr})"


def _tracked(v: Variant, sources: dict[str, Path]) -> Variant:
    """Điền keyframes cho zoom_to có track="teeth" (dò trên đoạn nguồn tương ứng)."""
    if not any(e.kind == "zoom_to" and e.track for e in v.effects):
        return v
    from vf.track import track_teeth

    effects = []
    for e in v.effects:
        if e.kind == "zoom_to" and e.track and not e.keyframes:
            acc = 0.0
            for p in v.pieces():
                if acc <= e.at < acc + p.duration:
                    src_t = p.start + (e.at - acc)
                    e = e.model_copy(update={"keyframes": track_teeth(sources[p.source], src_t, src_t + e.duration)})
                    break
                acc += p.duration
        effects.append(e)
    return v.model_copy(update={"effects": effects})


CPU_ARGS = ["-c:v", "libx264", "-preset", "medium", "-crf", "20"]
# NVENC (GPU NVIDIA, Windows): chất lượng tương đương libx264 crf 20, nhanh hơn nhiều; card phổ thông cho ≥ 3 phiên cùng lúc
NVENC_ARGS = ["-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq", "-rc", "vbr", "-cq", "21", "-b:v", "0",
              "-maxrate", "20M", "-bufsize", "40M", "-profile:v", "high"]
# VideoToolbox (Mac Apple Silicon): chất lượng cố định -q:v (0–100, cao = đẹp); 65 ≈ libx264 crf 20 cho video nói chuyện
VT_ARGS = ["-c:v", "h264_videotoolbox", "-q:v", "65", "-profile:v", "high"]


def _encoder_env() -> str:
    """VF_ENCODER = auto (mặc định) | cpu | nvenc | videotoolbox."""
    return os.environ.get("VF_ENCODER", "auto").lower()


@lru_cache(maxsize=4)
def _encoder_works(codec: str) -> bool:
    """Thử mã hoá 1 khung (có trong ffmpeg chưa đủ — phải có phần cứng + driver)."""
    proc = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=s=256x256:d=0.1", "-frames:v", "1",
                           "-c:v", codec, "-f", "null", "-"], capture_output=True)
    return proc.returncode == 0


def nvenc_available() -> bool:
    if _encoder_env() in ("cpu", "videotoolbox") or sys.platform == "darwin":
        return False
    return _encoder_works("h264_nvenc")


def videotoolbox_available() -> bool:
    if _encoder_env() in ("cpu", "nvenc") or sys.platform != "darwin":
        return False
    return _encoder_works("h264_videotoolbox")


def encoder_name() -> str:
    """Bộ mã hoá sẽ dùng: h264_videotoolbox (Mac) / h264_nvenc (Windows có GPU NVIDIA) / libx264 (CPU)."""
    return video_encoder_args()[1]


def video_encoder_args() -> list[str]:
    if videotoolbox_available():
        return VT_ARGS
    if nvenc_available():
        return NVENC_ARGS
    return CPU_ARGS


TRACK_PLACE = (0.5, 0.34)  # bám răng: răng ở 1/3 trên khung — vòng khoanh nằm trên hàng cột nút phải (vùng an toàn)


def zoom_place(e: Effect) -> tuple[float, float]:
    """Vị trí trên khung output mà điểm focus của zoom_to được đặt vào."""
    if e.place is not None:
        return e.place
    return TRACK_PLACE if e.track else (0.5, 0.5)


def _effect_filters(effects: list[Effect]) -> list[str]:
    out: list[str] = []
    zooms = [e for e in effects if e.kind == "zoom_punch"]
    if zooms:
        z = "+".join(f"0.08*{_between(e)}*(t-{e.at:.3f})/{max(e.duration, 0.01):.3f}" for e in zooms)
        zw, zh = f"2*trunc({W}*(1+{z})/2)", f"2*trunc({H}*(1+{z})/2)"
        # crop không thấy kích thước đổi theo khung → tính tâm trực tiếp từ cùng biểu thức zoom
        out.append(f"scale=w='{zw}':h='{zh}':eval=frame,crop={W}:{H}:x='({zw}-{W})/2':y='({zh}-{H})/2'")
    tos = [e for e in effects if e.kind == "zoom_to"]
    if tos:
        # Vox "zoom ống kính": phóng mượt (smoothstep 0.35 s) tới điểm focus, giữ tới hết effect rồi về 1 (thường trùng cắt cảnh)
        def ease(e: Effect) -> str:
            p = f"clip((t-{e.at:.3f})/0.35,0,1)"
            return f"{_between(e)}*{p}*{p}*(3-2*{p})"
        z = "1+" + "+".join(f"{e.zoom - 1:.3f}*{ease(e)}" for e in tos)
        on = "+".join(_between(e) for e in tos)
        cx = "+".join(f"({_focus_expr(e, 1)})*{_between(e)}" for e in tos) + f"+0.5*(1-({on}))"
        cy = "+".join(f"({_focus_expr(e, 2)})*{_between(e)}" for e in tos) + f"+0.5*(1-({on}))"
        # điểm focus được đặt tại `place` trên khung output (bám răng: cao 1/3 khung, để vòng khoanh tránh cột nút)
        px = "+".join(f"{zoom_place(e)[0]:.3f}*{_between(e)}" for e in tos) + f"+0.5*(1-({on}))"
        py = "+".join(f"{zoom_place(e)[1]:.3f}*{_between(e)}" for e in tos) + f"+0.5*(1-({on}))"
        zw, zh = f"2*trunc({W}*({z})/2)", f"2*trunc({H}*({z})/2)"
        out.append(f"scale=w='{zw}':h='{zh}':eval=frame,"
                   f"crop={W}:{H}:x='clip(({cx})*{zw}-{W}*({px}),0,{zw}-{W})'"
                   f":y='clip(({cy})*{zh}-{H}*({py}),0,{zh}-{H})',setsar=1")
    shakes = [e for e in effects if e.kind == "shake"]
    if shakes:
        dx = "+".join(f"{_between(e)}*16*sin(90*t)" for e in shakes)
        dy = "+".join(f"{_between(e)}*16*cos(70*t)" for e in shakes)
        out.append(f"scale={W + 40}:{H + 72},crop={W}:{H}:x='20+{dx}':y='36+{dy}'")
    for e in effects:
        if e.kind == "flash":
            out.append(f"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.75:t=fill:enable='{_between(e)}'")
        elif e.kind == "highlight":
            out.append(f"drawbox=x=0:y=ih*0.44:w=iw:h=ih*0.12:color=yellow@0.35:t=fill:enable='{_between(e)}'")
    return out


OVERLAY_Y = {"top": "h*0.12", "center": "(h-text_h)/2", "bottom": "h*0.70"}


def _overlay_filter(o: TextOverlay, idx: int, font: Path, text_dir: Path) -> str:
    text_dir.mkdir(parents=True, exist_ok=True)
    tf = text_dir / f"overlay_{idx}.txt"
    tf.write_text("\n".join(textwrap.wrap(o.text, width=20)) or o.text, encoding="utf-8")
    size = 88 if o.style == "hook" else 64
    return (
        f"drawtext=fontfile={_filter_path(font)}:textfile={_filter_path(tf)}:expansion=none:"
        f"fontsize={size}:fontcolor=white:borderw=7:bordercolor=black:line_spacing=12:"
        f"x=(w-text_w)/2:y={OVERLAY_Y[o.position]}:enable='between(t,{o.start:.3f},{o.end:.3f})'"
    )


def source_gains(
    sources: dict[str, Path], infos: dict[str, MediaInfo], names: set[str], speech: set[str] | None = None
) -> dict[str, float]:
    """Gain (dB) đưa nguồn có lời nói về -16 LUFS, đo một lần cho cả file.
    `speech`: các nguồn có lời nói; None = coi mọi nguồn là có lời nói."""
    gains = {}
    for name in names:
        lufs = measure_lufs(sources[name]) if infos[name].has_audio else -math.inf
        if lufs < -60:
            gains[name] = 0.0
        elif speech is None or name in speech:
            gains[name] = max(-20.0, min(20.0, SOURCE_TARGET_LUFS - lufs))
        else:
            gains[name] = max(-20.0, min(0.0, BROLL_TARGET_LUFS - lufs))
    return gains


def plan_transitions(v: Variant, videos: list[PieceVideo], infos: dict[str, MediaInfo]) -> list[tuple[str, float] | None]:
    """Chuyển cảnh ở từng ranh giới (feedback lo-04): ranh giới chương → kiểu của preset (fade/smooth) 0,3 s;
    cắt nhảy trong cùng cảnh → fade 0,2 s (thay cho zoom xen kẽ). Không đủ hình ở 2 bên điểm cắt → cắt thẳng."""
    pieces = v.pieces()
    kind = XFADE.get(preset(v.preset).get("transition", "cut"))
    starts, acc = [], 0.0
    for p in pieces:
        starts.append(acc)
        acc += p.duration
    cuts = chapter_cuts(v)
    out: list[tuple[str, float] | None] = [None] * len(pieces)
    for i in range(1, len(pieces)):
        if kind and any(abs(starts[i] - c) < 1e-3 for c in cuts):
            t = (kind, CHAPTER_XFADE_S)
        elif kind and i < len(videos) and videos[i].jump:
            t = ("fade", JUMP_XFADE_S)
        else:
            continue
        a, b, h = pieces[i - 1], pieces[i], t[1] / 2
        if b.start - h < 0 or a.end + h > infos[a.source].duration or min(a.duration, b.duration) < 3 * t[1]:
            continue  # không đủ hình để chồng
        out[i] = t
    return out


def build_ffmpeg_cmd(
    sources: dict[str, Path],
    infos: dict[str, MediaInfo],
    v: Variant,
    ass: Path | None,
    brand: Path,
    out: Path,
    *,
    gains: dict[str, float] | None = None,
    text_dir: Path | None = None,
    speech: set[str] | None = None,
    overlay: Path | None = None,
    videos: list[PieceVideo] | None = None,
) -> list[str]:
    """`overlay`: video chữ động nền trong suốt (Remotion) chồng lên hình; khi có thì không vẽ drawtext.
    `videos`: cách lấy hình từng đoạn (vf.scenes.plan_piece_video); None = lấy nguyên."""
    pieces = v.pieces()
    if gains is None:
        gains = source_gains(sources, infos, {p.source for p in pieces}, speech)
    text_dir = Path(text_dir) if text_dir else Path(tempfile.mkdtemp(prefix="vf-text-"))
    n = len(pieces)
    videos = videos or [PieceVideo() for _ in pieces]
    trans = plan_transitions(v, videos, infos)  # trans[i]: (kiểu xfade, thời lượng) ở ranh giới đoạn i-1 → i
    hb = [0.0] * n  # phần hình lấy thêm trước đầu đoạn (cho chồng mờ)
    ha = [0.0] * n  # phần hình lấy thêm sau cuối đoạn
    for i, t in enumerate(trans):
        if t:
            hb[i] = ha[i - 1] = t[1] / 2
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for i, p in enumerate(pieces):
        # seek theo từng đoạn: nhanh với file gốc dài, và mỗi đoạn có luồng riêng
        cmd += ["-ss", f"{p.start - hb[i]:.3f}", "-t", f"{p.duration + hb[i] + ha[i]:.3f}", "-i", str(sources[p.source])]
    fc: list[str] = []
    for i, (p, pv) in enumerate(zip(pieces, videos)):
        info = infos[p.source]
        fc += _fit(f"[{i}:v]setpts=PTS-STARTPTS,fps={FPS},", f"[vf{i}]", info, i)
        chain = []
        head = 0.0 if hb[i] else pv.head  # có chồng mờ ở mép → mẩu cảnh ở mép được che, không giữ khung
        tail = 0.0 if ha[i] else pv.tail
        length = hb[i] + p.duration + ha[i]
        vin = f"[vf{i}]"
        if p.video_end is not None and p.video_end < p.end - 0.02 and not ha[i]:
            # tiếng chạy tới p.end, hình dừng ở video_end: làm chậm khúc hình cuối (≥ 0,3 s, tối đa chậm ~2,5×)
            vd = p.video_end - p.start
            extra = p.end - p.video_end
            w = max(0.15, min(vd - 0.1, max(0.3, extra / 1.5)))
            k = (w + extra) / w
            a0 = hb[i] + head
            fc.append(f"[vf{i}]split=2[vs{i}a][vs{i}b]")
            fc.append(f"[vs{i}a]trim=start={a0:.3f}:end={hb[i] + vd - w:.3f},setpts=PTS-STARTPTS,"
                      f"tpad=start_mode=clone:start_duration={head:.3f}[vs{i}c]")
            fc.append(f"[vs{i}b]trim=start={hb[i] + vd - w:.3f}:end={hb[i] + vd:.3f},setpts=(PTS-STARTPTS)*{k:.4f},"
                      f"fps={FPS}[vs{i}d]")
            fc.append(f"[vs{i}c][vs{i}d]concat=n=2:v=1:a=0,tpad=stop_mode=clone:stop_duration=0.1[vs{i}e]")
            vin, head, tail = f"[vs{i}e]", 0.0, 0.0
        if head or tail:
            # mẩu cảnh vài khung hình ở mép: bỏ, giữ khung hình kề bên cho đủ thời lượng (tiếng không đổi)
            chain.append(f"trim=start={hb[i] + head:.3f}:end={hb[i] + p.duration + ha[i] - tail:.3f},setpts=PTS-STARTPTS,"
                         f"tpad=start_mode=clone:start_duration={head:.3f}"
                         f":stop_mode=clone:stop_duration={tail + 0.1:.3f}")
        if pv.zoom != 1.0:
            zw, zh = 2 * round(W * pv.zoom / 2), 2 * round(H * pv.zoom / 2)
            chain.append(f"scale={zw}:{zh},crop={W}:{H},setsar=1")
        chain.append(f"trim=duration={length:.3f},setpts=PTS-STARTPTS,format=yuv420p,settb=1/{FPS}")
        fc.append(vin + ",".join(chain) + f"[v{i}]")
        fade_in = JOIN_FADE_S if i > 0 and pieces[i - 1].source != p.source else DECLICK_S
        fade_out = JOIN_FADE_S if i < n - 1 and pieces[i + 1].source != p.source else DECLICK_S
        src = (f"[{i}:a]asetpts=PTS-STARTPTS,atrim=start={hb[i]:.3f},asetpts=PTS-STARTPTS,"
               if info.has_audio else "anullsrc=r=48000:cl=stereo,")
        fc.append(
            f"{src}aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
            f"volume={gains.get(p.source, 0.0):.2f}dB,apad,atrim=duration={p.duration:.3f},"
            # mute_head/mute_tail (feedback lo-05): im hẳn mẩu chữ kề ở mép — afade làm im trước st / sau st+d
            f"afade=t=in:st={p.mute_head:.3f}:d={fade_in},"
            f"afade=t=out:st={max(0.0, p.duration - p.mute_tail - fade_out):.3f}:d={fade_out}[a{i}]"
        )
    # hình: nối lần lượt — chồng mờ (xfade) ở ranh giới có chuyển cảnh, nối thẳng ở chỗ khác
    cur, cur_len = "[v0]", hb[0] + pieces[0].duration + ha[0]
    for i in range(1, n):
        nxt_len = hb[i] + pieces[i].duration + ha[i]
        lab = f"[vx{i}]"
        if trans[i]:
            kind, d = trans[i]
            fc.append(f"{cur}[v{i}]xfade=transition={kind}:duration={d:.3f}:offset={cur_len - d:.3f}{lab}")
            cur_len += nxt_len - d
        else:
            fc.append(f"{cur}[v{i}]concat=n=2:v=1:a=0,settb=1/{FPS}{lab}")  # xfade cần cùng timebase
            cur_len += nxt_len
        cur = lab
    fc.append(f"{cur}null[vc]")
    fc.append("".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[ac]")

    total = output_duration(v)
    extra = n
    vchain = _effect_filters(v.effects)
    if overlay is not None:
        # hiệu ứng (zoom, rung) chỉ áp vào hình quay; chữ động chồng lên sau nên không bị zoom theo
        cmd += ["-i", str(overlay)]
        fc.append("[vc]" + ",".join(vchain or ["null"]) + "[vfx]")
        fc.append(f"[{extra}:v]setpts=PTS-STARTPTS,fps={FPS}[ovl]")
        vchain = [f"[vfx][ovl]overlay=0:0:format=auto:eof_action=pass"]
        extra += 1
    else:
        font = find_font(brand) if v.overlays else None
        vchain += [_overlay_filter(o, k, font, text_dir) for k, o in enumerate(v.overlays)]
    if ass is not None and v.captions:
        vchain.append(f"subtitles=filename={_filter_path(ass)}:fontsdir={_filter_path(brand)}")
    vchain.append(f"fps={FPS},format=yuv420p")
    if overlay is not None:
        fc.append(vchain[0] + "," + ",".join(vchain[1:]) + "[vout]")
    else:
        fc.append("[vc]" + ",".join(vchain) + "[vout]")
    audio = load_tokens()["audio"]
    mix = ["[ac]"]
    if v.music:
        cmd += ["-stream_loop", "-1", "-i", str(resolve_asset(v.music, brand))]
        m_lufs = measure_lufs(resolve_asset(v.music, brand))
        # nhạc nằm dưới giọng music_gain_db, và tự hạ thêm khi có giọng (sidechain, khoá = giọng)
        m_gain = 0.0 if m_lufs < -60 else SOURCE_TARGET_LUFS + audio["music_gain_db"] - m_lufs
        d = audio["duck"]
        fc.append("[ac]asplit=2[acv][key]")
        mix = ["[acv]"]
        fc.append(f"[{extra}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration={total:.3f},"
                  f"volume={m_gain:.2f}dB,afade=t=out:st={max(0.0, total - 0.5):.3f}:d=0.5[mus0]")
        fc.append(f"[mus0][key]sidechaincompress=threshold={d['threshold']}:ratio={d['ratio']}"
                  f":attack={d['attack']}:release={d['release']}[mus]")
        mix.append("[mus]")
        extra += 1
    for k, e in enumerate(x for x in v.effects if x.kind == "sfx" and x.asset):
        cmd += ["-i", str(resolve_asset(e.asset, brand))]
        ms = int(e.at * 1000)
        fc.append(f"[{extra}:a]aresample=48000,aformat=channel_layouts=stereo,volume={audio['sfx_gain_db']}dB,"
                  f"adelay={ms}|{ms}[sfx{k}]")
        mix.append(f"[sfx{k}]")
        extra += 1
    if len(mix) > 1:
        fc.append("".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0[amix]")
        alabel = "[amix]"
    else:
        alabel = "[ac]"
    fc.append(f"{alabel}loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,atrim=duration={total:.3f}[aout]")

    cmd += [
        "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
        "-r", str(FPS), *video_encoder_args(), "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out),
    ]
    return cmd


def _placed(v: Variant, videos: list[PieceVideo], sources: dict[str, Path]) -> tuple[Variant, list[str]]:
    """Đặt chữ/hiệu ứng trong vùng an toàn TikTok, không che mặt; thiếu OpenCV thì chỉ giữ vùng an toàn."""
    from vf.placement import place

    try:
        import cv2  # noqa: F401
        faces = True
    except ImportError:
        faces = False
    overlays, graphics, notes = place(v.pieces(), videos, sources, v.overlays, v.graphics, faces=faces)
    return v.model_copy(update={"overlays": overlays, "graphics": graphics}), notes


def _extract_stills(v: Variant, sources: dict[str, Path]) -> None:
    """Ảnh cho collage → remotion/public/stills/<biến thể>_<k>.jpg (Remotion đọc bằng staticFile)."""
    from vf.motion import REMOTION_DIR

    k = 0
    for g in v.graphics:
        for st in g.stills:
            dst = REMOTION_DIR / "public" / "stills" / f"{v.id}_{k}.jpg"
            dst.parent.mkdir(parents=True, exist_ok=True)
            x0, y0, x1, y1 = st.crop
            run(["ffmpeg", "-y", "-v", "error", "-ss", f"{st.t:.3f}", "-i", str(sources[st.source]), "-frames:v", "1",
                 "-vf", f"crop=iw*{x1 - x0:.4f}:ih*{y1 - y0:.4f}:iw*{x0:.4f}:ih*{y0:.4f},scale=720:-2", "-q:v", "3", str(dst)])
            k += 1


def render_variant(
    sources: dict[str, Path],
    infos: dict[str, MediaInfo],
    v: Variant,
    out: Path,
    *,
    words_by_source: dict[str, list[Word]] | None = None,
    brand: Path = DEFAULT_BRAND,
    style_path: Path = DEFAULT_STYLE,
    work_dir: Path | None = None,
    forbidden: list[str] | None = None,
    motion: bool | None = None,
    cuts_by_source: dict[str, list[float]] | None = None,
    text_sources: set[str] | None = None,
    text_free: dict[str, list[tuple[float, float]]] | None = None,
    notes: list[str] | None = None,
    creative: list[str] | None = None,
) -> Path:
    """`creative` (nếu truyền): nhận ghi chú sáng tạo (vf/creative.py), không chặn render.
    `notes` (nếu truyền): nhận ghi chú vùng an toàn (chữ/hình bị kéo vào, lấn vùng giao diện TikTok).
    `forbidden`: cụm cấm riêng của lô (brief.forbidden) — chữ trên màn hình chứa cụm đó → ClaimViolation, không tạo file.
    Không còn kiểm forbidden.txt / claims_pending.txt (người dùng chốt 2026-10-14: không chặn claim).
    Overlay = chữ trong edl + cam kết tự phát hiện trong lời nói (profiles/<hồ sơ>/commitments.txt).
    motion=None: dùng Remotion nếu đã cài, không thì vẽ chữ tĩnh bằng drawtext."""
    from vf.edl import apply_graphic_defaults, check_profile
    from vf.motion import plan_overlays, remotion_available, render_overlay, strip_text

    errs = check_profile(v)  # preset / gói đồ hoạ phải có trong hồ sơ đang dùng
    if errs:
        raise ValueError("; ".join(errs))
    v = apply_graphic_defaults(v)
    forbidden = forbidden or []  # chỉ cụm cấm riêng của lô (brief.forbidden); không dùng forbidden.txt
    v = v.model_copy(update={"overlays": plan_overlays(v, words_by_source or {})})
    v = strip_text(v, text_sources or set(), text_free)
    words = remap_words(words_by_source or {}, v.pieces()) if v.captions else []
    texts = ([o.text for o in v.overlays] + [o.sub for o in v.overlays if o.sub]
             + [st.label for g in v.graphics for st in g.stills if st.label] + [g.label for g in v.graphics if g.label]
             + ([" ".join(w.text for w in words)] if words else []))
    hits = check_claims(texts, forbidden)
    if hits:
        raise ClaimViolation(f"biến thể '{v.id}': chữ trên màn hình chứa cụm cấm/chưa có bằng chứng: {hits}")
    work = Path(work_dir) if work_dir else Path(tempfile.mkdtemp(prefix=f"vf-{v.id}-"))
    work.mkdir(parents=True, exist_ok=True)
    ass_path = None
    if v.captions:
        if words:
            ass_path = work / f"{v.id}.ass"
            ass_path.write_text(words_to_ass(words, style_path), encoding="utf-8")
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp_out = out.with_name(out.stem + ".partial" + out.suffix)
    spoken = {name for name, ws in (words_by_source or {}).items() if ws}
    speech = spoken or None  # chưa có transcript nào → không đoán, coi mọi nguồn là có lời nói
    videos = plan_piece_video(v.pieces(), cuts_by_source or {})
    v = _tracked(v, sources)
    v, fixes = auto_fix(v, text_sources, text_free)  # giữ chữ đủ lâu để đọc, không vắt qua cắt/chữ in sẵn
    v = v.model_copy(update={"graphics": v.graphics + transition_graphics(v)})
    sfx_dir = Path(brand) / "sfx" if (Path(brand) / "sfx").is_dir() else BRAND_DIR / "sfx"
    v = v.model_copy(update={"effects": v.effects + auto_sfx(v, sfx_dir)})
    if creative is not None:
        from vf.audiocut import lint_audio_edges

        creative += fixes + lint_cuts(v, words_by_source or {}, videos) + lint_audio_edges(v, sources) + lint_variant(v)
    overlay_path = None
    notes = notes if notes is not None else []
    if v.overlays or v.graphics:
        v, placed_notes = _placed(v, videos, sources)
        notes += placed_notes
    if (v.overlays or v.graphics) and (remotion_available() if motion is None else motion):
        _extract_stills(v, sources)
        overlay_path = render_overlay(v, DEFAULT_STYLE_GUIDE, work / f"{v.id}_overlay.mov", brand=brand,
                                      props_path=work / f"{v.id}_overlay.json")
        full = [(g.start - 0.3, g.end + 0.1) for g in v.graphics if g.kind in OPAQUE]  # làm tròn khung hình; tờ giấy xoay lọt mép từ khung đầu
        # thẻ `free` được người dùng cho ra ngoài vùng an toàn (2026-10-16) — QA alpha bỏ qua lúc chúng hiện
        full += [(g.start - 0.1, g.end + 0.1) for g in v.graphics if g.free]
        full += [(o.start - 0.1, o.end + 0.1) for o in v.overlays if o.free]
        notes += check_safe_zone(overlay_path, skip=full)
    cmd = build_ffmpeg_cmd(sources, infos, v, ass_path, brand, tmp_out, text_dir=work / f"{v.id}_text",
                           speech=speech, overlay=overlay_path, videos=videos)
    try:
        try:
            run(cmd)
        except Exception:
            if CPU_ARGS[1] in cmd:
                raise
            # NVENC/VideoToolbox lỗi (driver, hết phiên mã hoá…) → mã hoá lại bằng CPU
            i = cmd.index("-c:v")
            j = cmd.index("-pix_fmt")
            run(cmd[:i] + CPU_ARGS + cmd[j:])
    except Exception:
        tmp_out.unlink(missing_ok=True)
        raise
    try:
        tmp_out.replace(out)
    except PermissionError:
        # file cũ đang mở (trình phát video, Drive đang đồng bộ) → lưu tên khác thay vì mất bản vừa render
        k = 2
        while (alt := out.with_name(f"{out.stem}_v{k}{out.suffix}")).exists():
            try:
                alt.unlink()
                break
            except PermissionError:
                k += 1
        tmp_out.replace(alt)
        notes.append(f"file cũ {out.name} đang mở — bản mới lưu thành {alt.name}")
        out = alt
    return out
