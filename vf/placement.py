"""Chọn vị trí dọc cho chữ/hiệu ứng: không che mặt (OpenCV Haar), tránh vùng nhiều chi tiết (sản phẩm, tay),
không đè lên chữ khác cùng lúc, và luôn nằm trong vùng an toàn của TikTok (vf/safezone.py)."""
from __future__ import annotations

import math
from pathlib import Path

from vf.edl import Graphic, Segment, TextOverlay
from vf.safezone import SAFE
from vf.scenes import PieceVideo

FRAME_H = 1920
# cỡ chữ + đệm dọc (px) — khớp với remotion/src/Overlay.tsx
FONT_PX = {"hook": 72, "commit": 64, "label": 50, "cta": 56, "plain": 56, "lower": 60, "tag": 46, "vox": 58}
PAD_PX = {"hook": 16, "commit": 18, "label": 14, "cta": 18, "plain": 12, "lower": 16, "tag": 10, "vox": 14}
SUB_PX = 34  # dòng phụ của thẻ lower — khớp remotion/src/Overlay.tsx (feedback lo-04: thẻ nhỏ hơn, bớt che chủ thể)
MAX_TEXT_W = 900
SIDE_PAD_PX = 36  # đệm ngang của hộp chữ — khớp remotion/src/Overlay.tsx
SLACK_PX = 24  # chừa cho viền chữ, bóng, nhịp đập CTA (×1.04), lắc nhẹ thẻ cam kết
UPPER_STYLES = {"lower", "tag", "vox"}  # viết hoa: chữ rộng hơn
GRAPHIC_H_PX = {"light": 150, "whiten": 520, "teeth": 350, "counter": 200, "callout": 1920, "collage": 1920,
                "shade": 300, "wipe": 1920, "light_timer": 180, "kinetic": 1920, "end_card": 300,
                "steps": 560, "live_cta": 320, "nope": 330, "cost_compare": 400, "refill": 300, "versus": 360,
                "size_fit": 330, "compartments": 520, "badge": 260}
GRAPHIC_W_PX = {"light": 620, "whiten": 520, "teeth": 540, "counter": 520, "callout": 1080, "collage": 1080,
                "shade": 620, "wipe": 1080, "light_timer": 680, "kinetic": 1080, "end_card": 620,
                "steps": 620, "live_cta": 620, "nope": 560, "cost_compare": 480, "refill": 600, "versus": 600,
                "size_fit": 620, "compartments": 600, "badge": 560}
FULL_FRAME = {"callout", "collage", "wipe", "kinetic", "paper_swipe"}  # counter giờ là thẻ gọn (đặt chỗ như thẻ thường)  # tự bố cục bên trong vùng an toàn (remotion, props `safe`)
OPAQUE = {"collage", "wipe", "paper_swipe"}  # thẻ so sánh lớn được bỏ qua vùng an toàn (người dùng cho phép, lo-03/lo-04)  # nền phủ kín khung: QA alpha bỏ qua (callout, kinetic vẫn kiểm)
TOP_MIN, BOTTOM_MAX = SAFE.y0, SAFE.y1  # vùng an toàn TikTok: trên 240 px, dưới 660 px
PREFERRED = {"top": 0.14, "center": 0.42, "bottom": 0.54}
FACE_WEIGHT, BUSY_WEIGHT, PREF_WEIGHT, COLLIDE_WEIGHT = 12.0, 1.0, 0.15, 10.0  # che chủ thể nặng hơn mọi thứ khác
SMALL_W, SMALL_H = 270, 480


def text_box(o: TextOverlay, max_w_px: float = MAX_TEXT_W) -> tuple[float, float]:
    """(rộng, cao) ước lượng theo tỉ lệ khung; `max_w_px` = bề rộng hộp tối đa (gồm đệm), chữ tự xuống dòng."""
    fs = FONT_PX[o.style]
    char_w = fs * (0.70 if o.style in UPPER_STYLES else 0.62)
    per_line = max(1, int((max_w_px - 2 * SIDE_PAD_PX) / char_w))
    lines = 0
    for_line = 0
    longest = 0
    for w in o.text.split():
        if for_line and for_line + 1 + len(w) > per_line:
            lines += 1
            longest = max(longest, for_line)
            for_line = len(w)
        else:
            for_line += (1 if for_line else 0) + len(w)
    lines += 1
    longest = max(longest, for_line)
    w = min(max_w_px, longest * char_w + 2 * SIDE_PAD_PX)
    if o.sub:
        w = max(w, min(max_w_px, len(o.sub) * SUB_PX * 0.55 + 2 * SIDE_PAD_PX))
    h = lines * fs * 1.18 + 2 * PAD_PX[o.style] + (SUB_PX * 1.3 + 6 if o.sub else 0)
    return w / 1080, h / FRAME_H


def safe_text_w_px(y_top: float, y_bot: float) -> float:
    """Bề rộng hộp chữ (px) tối đa ở độ cao này: hẹp lại (và lệch trái, SAFE.center_x) khi chạm hàng cột nút."""
    return min(MAX_TEXT_W, SAFE.max_w(y_top, y_bot) * 1080 - SLACK_PX)


def _box(w: float, y: float, h: float) -> tuple[tuple[float, float, float, float], float]:
    """Hộp rộng w đặt giữa khoảng an toàn ở độ cao y..y+h → (hộp, tâm ngang)."""
    cx = SAFE.center_x(y, y + h)
    return (cx - w / 2, y, cx + w / 2, y + h), cx


def graphic_box(g: Graphic) -> tuple[float, float]:
    h = 230 if g.kind == "steps" and g.compact else GRAPHIC_H_PX[g.kind]  # khớp StepsFx compact (remotion)
    s = g.scale if g.kind not in FULL_FRAME else 1.0
    return GRAPHIC_W_PX[g.kind] * s / 1080, h * s / FRAME_H


def source_time(pieces: list[Segment], videos: list[PieceVideo], t: float) -> tuple[str, float]:
    """Giờ output → (nguồn, giờ nguồn của khung hình THẬT đang hiện), tính cả phần giữ khung."""
    acc = 0.0
    for p, pv in zip(pieces, videos):
        if t < acc + p.duration or p is pieces[-1]:
            rel = min(max(t - acc, pv.head), p.duration - pv.tail - 1e-3)
            return p.source, p.start + max(0.0, rel)
        acc += p.duration
    raise ValueError(t)


class _Frames:
    def __init__(self, sources: dict[str, Path]):
        import cv2

        self.cv2 = cv2
        self.sources = sources
        self.caps: dict[str, object] = {}
        self.front = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.profile = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
        self.cache: dict[tuple[str, int], tuple] = {}

    def analyse(self, source: str, t: float):
        """→ (mặt: list[(x0,y0,x1,y1)] theo tỉ lệ, mật độ cạnh theo hàng/cột: ma trận nhỏ)."""
        key = (source, int(t * 10))
        if key in self.cache:
            return self.cache[key]
        cv2 = self.cv2
        cap = self.caps.get(source)
        if cap is None:
            cap = self.caps[source] = cv2.VideoCapture(str(self.sources[source]))
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            self.cache[key] = ([], None)
            return self.cache[key]
        gray = cv2.cvtColor(cv2.resize(frame, (SMALL_W, SMALL_H)), cv2.COLOR_BGR2GRAY)
        faces = []
        for casc, flip in ((self.front, False), (self.profile, False), (self.profile, True)):
            img = cv2.flip(gray, 1) if flip else gray
            for (x, y, w, h) in casc.detectMultiScale(img, 1.1, 5, minSize=(28, 28)):
                if flip:
                    x = SMALL_W - x - w
                # nới hộp mặt: tóc, cằm, miệng đang ngậm khay — và xuống dưới cằm (máy, tay cầm máy):
                # feedback lo-04 "thẻ chữ che chủ thể đang dùng kit"
                x0, y0 = (x - 0.25 * w) / SMALL_W, (y - 0.35 * h) / SMALL_H
                x1, y1 = (x + 1.25 * w) / SMALL_W, (y + 2.3 * h) / SMALL_H
                faces.append((max(0, x0), max(0, y0), min(1, x1), min(1, y1)))
        edges = cv2.GaussianBlur(cv2.Canny(gray, 80, 160), (9, 9), 0).astype("float32") / 255.0
        self.cache[key] = (faces, edges)
        return self.cache[key]

    def close(self):
        for c in self.caps.values():
            c.release()


def _overlap(a: tuple, b: tuple) -> float:
    """Diện tích giao / diện tích a."""
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    if w <= 0 or h <= 0:
        return 0.0
    return w * h / max(1e-6, (a[2] - a[0]) * (a[3] - a[1]))


def _score(box, frames_data, pref: float | None, placed: list[tuple], ) -> float:
    s = 0.0
    for faces, edges in frames_data:
        s += FACE_WEIGHT * sum(_overlap(box, f) for f in faces)
        if edges is not None:
            y0, y1 = int(box[1] * SMALL_H), max(int(box[1] * SMALL_H) + 1, int(box[3] * SMALL_H))
            x0, x1 = int(box[0] * SMALL_W), max(int(box[0] * SMALL_W) + 1, int(box[2] * SMALL_W))
            s += BUSY_WEIGHT * float(edges[y0:y1, x0:x1].mean()) * 4
    s /= max(1, len(frames_data))
    if pref is not None:
        s += PREF_WEIGHT * abs(box[1] - pref)
    s += COLLIDE_WEIGHT * sum(_overlap(box, p) for p in placed)
    return s


def _bands(avoid) -> list[tuple]:
    """dải dọc phải tránh (phụ đề in sẵn) → hộp phủ hết bề ngang, tính như vật đã đặt."""
    return [(0.0, a, 1.0, b) for a, b in (avoid or [])]


def _core(f: tuple) -> tuple:
    """Hộp mặt nới (tóc → tay cầm máy, xem _Frames.analyse) → mặt lõi trán dưới → cằm."""
    w, h = (f[2] - f[0]) / 1.5, (f[3] - f[1]) / 2.65
    return (f[0] + 0.25 * w, f[1] + 0.5 * h, f[0] + 1.25 * w, f[1] + 1.5 * h)


def face_cover(frames_data, box) -> float:
    """Trung bình phần MẶT LÕI (trán dưới → cằm) bị hộp này che, trên các khung lấy mẫu (lo-07: hộp mặt nới phủ gần
    hết khung khi cận mặt, nên không dùng để quyết định dời)."""
    if not frames_data:
        return 0.0
    return sum(sum(_overlap(_core(f), box) for f in faces) for faces, _ in frames_data) / len(frames_data)


def best_y_off_face(frames_data, w: float, h: float, pref: float, placed: list[tuple]) -> float:
    """y gần `pref` nhất mà che mặt lõi ít nhất, tránh vật đã đặt + dải phụ đề (`placed`, phạt nặng hơn che mặt:
    không bao giờ đè chữ in sẵn), trong vùng an toàn."""
    best, best_s = pref, math.inf
    y = TOP_MIN
    while y + h <= BOTTOM_MAX + 1e-6:
        if w <= SAFE.max_w(y, y + h) + 1e-6:
            box, _ = _box(w, y, h)
            s = (FACE_WEIGHT * face_cover(frames_data, box) + 5 * COLLIDE_WEIGHT * sum(_overlap(box, p) for p in placed)
                 + PREF_WEIGHT * abs(y - pref))
            if s < best_s - 1e-9:
                best, best_s = y, s
        y += 0.01
    return round(best, 3)


FACE_COVER_MAX = 0.02  # feedback lo-06/lo-07: "motion che mặt KOL" — y đặt tay mà che mặt thì tự dời


FREE_TOP, FREE_BOTTOM = 0.02, 0.97  # thẻ `free`: cả khung trừ mép, không theo vùng an toàn


def best_y_free(frames_data, w: float, h: float, pref: float, placed: list[tuple]) -> float:
    """Thẻ `free` (người dùng 2026-10-16): giữ cỡ gốc, chỉ né MẶT (trên đầu hoặc dưới cằm) — được ra ngoài vùng an toàn;
    vẫn tránh dải chữ in sẵn (`placed`) và ưu tiên gần `pref`."""
    best, best_s = pref, math.inf
    y = FREE_TOP
    while y + h <= FREE_BOTTOM + 1e-6:
        box = (0.5 - w / 2, y, 0.5 + w / 2, y + h)
        s = (FACE_WEIGHT * 4 * face_cover(frames_data, box) + 5 * COLLIDE_WEIGHT * sum(_overlap(box, p) for p in placed)
             + PREF_WEIGHT * abs(y - pref))
        if s < best_s - 1e-9:
            best, best_s = y, s
        y += 0.01
    return round(best, 3)


def best_y(frames_data, w: float, h: float, pref: float | None, placed: list[tuple]) -> float:
    best, best_s = TOP_MIN, math.inf
    y = TOP_MIN
    while y + h <= BOTTOM_MAX + 1e-6:
        if w > SAFE.max_w(y, y + h) + 1e-6:  # không vừa bề ngang an toàn ở độ cao này (hàng cột nút)
            y += 0.02
            continue
        box, _ = _box(w, y, h)
        s = _score(box, frames_data, pref, placed)
        if s < best_s - 1e-9:
            best, best_s = y, s
        y += 0.02
    return round(best, 3)


def best_text_y(frames_data, o: TextOverlay, pref: float | None, placed: list[tuple]) -> tuple[float, float, float] | None:
    """(y, rộng, cao) tốt nhất cho chữ mà cả hộp nằm trong vùng an toàn; bề rộng co lại khi hộp chạm hàng cột nút.
    None = chữ quá dài, không vị trí nào vừa."""
    best, best_s = None, math.inf
    y = TOP_MIN
    while y < BOTTOM_MAX:
        w, h = text_box(o, safe_text_w_px(y, y))
        if y + h > SAFE.rail_y:  # chạm hàng cột nút → hẹp lại, chữ xuống dòng nhiều hơn
            w, h = text_box(o, safe_text_w_px(y, y + 1))
        if y + h <= BOTTOM_MAX + 1e-6:
            box, _ = _box(w, y, h)
            s = _score(box, frames_data, pref, placed)
            if s < best_s - 1e-9:
                best, best_s = (round(y, 3), w, h), s
        y += 0.02
    return best


def _fit_explicit_y(o: TextOverlay) -> tuple[float, float, float]:
    """`y` ghi tay trong edl: giữ nếu vừa vùng an toàn, không thì kéo vào trong."""
    y = min(max(o.y, TOP_MIN), BOTTOM_MAX - 0.01)
    w, h = text_box(o, safe_text_w_px(y, y + 1))  # bản hẹp: chắc chắn không chạm cột nút
    return math.floor(max(TOP_MIN, min(y, BOTTOM_MAX - h)) * 1000) / 1000, w, h  # làm tròn xuống: không lố mép dưới


def fit_callout(g: Graphic) -> Graphic:
    """Vòng khoanh (cx, cy, rx, ry) phải nằm trọn trong vùng an toàn; nhãn bút dạ do Remotion tự đặt trên/dưới vòng."""
    ry = min(g.ry, (BOTTOM_MAX - TOP_MIN) / 2 - 0.01)
    cy = min(max(g.cy, TOP_MIN + ry), BOTTOM_MAX - ry)
    x0, x1 = SAFE.x_range(cy - ry, cy + ry)
    rx = math.floor(min(g.rx, (x1 - x0) / 2 - 0.01) * 1000) / 1000  # làm tròn xuống: không lấn ra sau khi làm tròn
    cx = min(max(g.cx, x0 + rx), x1 - rx)
    cx = min(max(round(cx, 3), x0 + rx), x1 - rx)
    return g.model_copy(update={"cx": cx, "cy": round(cy, 3), "rx": rx, "ry": round(ry, 3)})


def place(
    pieces: list[Segment],
    videos: list[PieceVideo],
    sources: dict[str, Path],
    overlays: list[TextOverlay],
    graphics: list[Graphic],
    *,
    faces: bool = True,
) -> tuple[list[TextOverlay], list[Graphic], list[str]]:
    """Đặt `y` (và bề rộng chữ `max_w`) cho mọi chữ/hiệu ứng, luôn trong vùng an toàn TikTok.
    Hiệu ứng đặt trước (to hơn), chữ tránh hiệu ứng đang hiện. `faces=False` (thiếu OpenCV): không né mặt,
    vẫn giữ vùng an toàn. Trả thêm ghi chú cho những gì phải kéo vào / không vừa."""
    frames = _Frames(sources) if faces else None
    placed: list[tuple[float, float, tuple]] = []  # (start, end, box)
    notes: list[str] = []

    def sample(start: float, end: float):
        if frames is None:
            return []
        ts = [start + 0.15, (start + end) / 2, max(start + 0.15, end - 0.15)]
        return [frames.analyse(*source_time(pieces, videos, t)) for t in ts]

    def busy(start, end):
        return [b for (s, e, b) in placed if s < end and start < e]

    try:
        out_g = []
        for g in graphics:
            if g.kind == "callout":
                fitted = fit_callout(g)
                if (fitted.cx, fitted.cy, fitted.rx, fitted.ry) != (g.cx, g.cy, g.rx, g.ry):
                    notes.append(f"vùng an toàn: vòng khoanh lúc {g.start:.1f} s được kéo vào trong khung an toàn")
                g = fitted
            if g.kind in FULL_FRAME:  # toàn màn hình, tự bố cục trong vùng an toàn
                placed.append((g.start, g.end, (0.0, 0.0, 1.0, 1.0)))
                keep_y = g.kind in ("kinetic", "callout") and g.y is not None  # callout: y = mép trên nhãn đặt tay
                out_g.append(g.model_copy(update={"y": g.y if keep_y else 0.0}))
                continue
            w, h = graphic_box(g)
            if g.free:
                y = best_y_free(sample(g.start, g.end), w, h, g.y if g.y is not None else 0.6,
                                busy(g.start, g.end) + _bands(g.avoid))
                box = (0.5 - w / 2, y, 0.5 + w / 2, y + h)
                placed.append((g.start, g.end, box))
                out_g.append(g.model_copy(update={"y": y, "xc": 0.5}))
                continue
            if g.y is not None:
                y = min(max(g.y, TOP_MIN), BOTTOM_MAX - h)
                if abs(y - g.y) > 1e-6:
                    notes.append(f"vùng an toàn: {g.kind} lúc {g.start:.1f} s, y {g.y} → {y:.3f}")
                # y đặt tay chỉ là vị trí mong muốn: che mặt KOL thì dời tới chỗ gần nhất không che (lo-06/lo-07)
                fd = sample(g.start, g.end)
                if face_cover(fd, _box(w, y, h)[0]) > FACE_COVER_MAX:
                    y2 = best_y_off_face(fd, w, h, y, busy(g.start, g.end) + _bands(g.avoid))
                    if face_cover(fd, _box(w, y2, h)[0]) < face_cover(fd, _box(w, y, h)[0]):
                        y = y2
            else:
                y = best_y(sample(g.start, g.end), w, h, None, busy(g.start, g.end) + _bands(g.avoid))
            y = round(y, 3)
            box, cx = _box(w, y, h)
            if g.xc is not None:  # tâm ngang đặt tay (lo-05: né mặt ở khung 2 người lệch tầng), giữ trong vùng an toàn
                x0, x1 = SAFE.x_range(y, y + h)
                lo, hi = x0 + w / 2, x1 - w / 2
                cx = min(max(g.xc, lo), max(lo, hi))
                box = (cx - w / 2, y, cx + w / 2, y + h)
            placed.append((g.start, g.end, box))
            out_g.append(g.model_copy(update={"y": y, "xc": round(cx, 4)}))
        out_o = []
        for o in overlays:
            pref = PREFERRED[o.position]
            if o.free:
                w, h = text_box(o, MAX_TEXT_W)
                y = best_y_free(sample(o.start, o.end), w, h, o.y if o.y is not None else 0.6,
                                busy(o.start, o.end) + _bands(o.avoid))
                box = (0.5 - w / 2, y, 0.5 + w / 2, y + h)
                placed.append((o.start, o.end, box))
                out_o.append(o.model_copy(update={"y": y, "xc": 0.5, "max_w": MAX_TEXT_W}))
                continue
            if o.y is not None:
                y, w, h = _fit_explicit_y(o)
                if abs(y - o.y) > 1e-6:
                    notes.append(f"vùng an toàn: chữ \"{o.text}\" y {o.y} → {y}")
                fd = sample(o.start, o.end)
                if face_cover(fd, _box(w, y, h)[0]) > FACE_COVER_MAX:  # y tay che mặt → dời (lo-06/lo-07)
                    found = best_text_y(fd, o, o.y, busy(o.start, o.end) + _bands(o.avoid))
                    if found is not None and face_cover(fd, _box(found[1], found[0], found[2])[0]) < face_cover(fd, _box(w, y, h)[0]):
                        y, w, h = found
            else:
                found = best_text_y(sample(o.start, o.end), o, pref, busy(o.start, o.end) + _bands(o.avoid))
                if found is None:
                    y = TOP_MIN
                    w, h = text_box(o, safe_text_w_px(0, 1))
                    notes.append(f"vùng an toàn: chữ \"{o.text}\" quá dài, không vừa khung an toàn — rút ngắn chữ")
                else:
                    y, w, h = found
            box, cx = _box(w, y, h)
            placed.append((o.start, o.end, box))
            # Remotion: hộp chữ không rộng quá bề rộng an toàn ở độ cao này (chữ tự xuống dòng bên trong)
            out_o.append(o.model_copy(update={"y": y, "xc": round(cx, 4), "max_w": int(safe_text_w_px(y, y + h))}))
        return out_o, out_g, notes
    finally:
        if frames is not None:
            frames.close()
