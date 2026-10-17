"""MẪU (hồ sơ smilee) — sinh edl.json cạnh file này (nguồn dqamii.mp4) — 4 biến thể mặc định mới (người dùng chốt 2026-10-16, ưu tiên khách
đang cân nhắc, đẩy hiệu quả lên ngay sau hook):
  1. hiệu quả trước (proof)          2. nỗi đau → hiệu quả ngay (pink)
  3. bút gel → hiệu quả nhanh (routine)  4. kêu gọi mua → review hiệu quả (gift)
Câu chuyện nỗi đau rút còn 2–3 s, gỡ nỗi lo (nha khoa đau ví/buốt, không ê buốt) trước khi nói tiền, CTA cuối một lệnh.
Mép đoạn: đầu câu, rơi vào khe giọng (dip) — nguồn có nhạc nền; mọi điểm chuyển cắt thẳng (style guide v2.6).
Thẻ/motion cỡ gốc, chỉ né mặt (`free`, trên đầu / dưới cằm), tránh phụ đề in sẵn (`avoid`)."""
import json
from pathlib import Path

import numpy as np

SRC = "dqamii.mp4"
ROOT = Path(__file__).resolve().parents[2]
W = json.loads((ROOT / "work" / SRC / "transcript.json").read_text(encoding="utf-8"))

import sys  # noqa: E402

sys.path.insert(0, str(ROOT))
from vf.audiocut import FRAME_S, _pcm, _rms_db  # noqa: E402

_x = _pcm(str(ROOT / "work" / SRC / "normalized.mp4"))
_DB = _rms_db(_x, float(np.percentile(np.abs(_x), 99)) + 1e-9)
_DB = np.convolve(_DB, np.ones(3) / 3, mode="same")  # 30 ms


# Phiên âm của dqamii ĐÚNG giờ (phiên âm lại đoạn ngắn 2026-10-16 ra cùng mốc). Lỗi "thiếu chữ 'không'", "không nói hết
# chữ '7'" (feedback lo-08) là do dò khe giọng ±0,3 s CẢ HAI PHÍA: nhạc nền làm chỗ thấp nhất rơi vào BÊN TRONG chữ cuối.
# Sửa: mép cuối chỉ tìm khe SAU chữ cuối (trước chữ kế), mép đầu chỉ tìm TRƯỚC chữ đầu (sau chữ liền trước).
OFF = 0.0


def word(text, near, field="start"):
    """mốc đầu/cuối (đã bù OFF) của chữ `text` gần `near` (giờ phiên âm) nhất."""
    c = [w for w in W if w["text"].strip(" ,.?!").lower() == text.lower() and abs(w["start"] - near) < 2.5]
    assert c, f"không thấy chữ '{text}' quanh {near}"
    return round(min(c, key=lambda w: abs(w["start"] - near))[field] + OFF, 3)


def dip(t, span=0.3):
    """chỗ âm lượng thấp nhất trong ±span quanh t (khe giữa hai chữ khi KOL nói liền, có nhạc nền)."""
    i0, i1 = max(0, int((t - span) / FRAME_S)), min(len(_DB), int((t + span) / FRAME_S))
    k = i0 + int(np.argmin(_DB[i0:i1] + 0.02 * np.abs(np.arange(i0, i1) - t / FRAME_S)))
    return round(k * FRAME_S, 3)


def _w(text, near):
    c = [w for w in W if w["text"].strip(" ,.?!").lower() == text.lower() and abs(w["start"] - near) < 2.5]
    assert c, f"không thấy chữ '{text}' quanh {near}"
    return min(c, key=lambda w: abs(w["start"] - near))


def _lowest(a, b):
    """chỗ âm lượng thấp nhất trong [a, b] (a ≥ b → a)."""
    i0, i1 = int(a / FRAME_S), int(b / FRAME_S)
    if i1 <= i0:
        return round(a, 3)
    return round((i0 + int(np.argmin(_DB[i0:i1]))) * FRAME_S, 3)


def _first_trough(t, direction, span=0.3, drop=6.0):
    """Từ mốc phiên âm t, quét theo `direction` (+1 sau / −1 trước) tới điểm TRŨNG âm lượng đầu tiên (cực tiểu cục bộ thấp
    hơn đỉnh đã qua ≥ `drop` dB) — chỗ chữ thật sự dứt / bắt đầu. Feedback lo-08: mốc cuối chữ của phiên âm sớm hơn tiếng
    thật 0,1–0,2 s khi KOL nói liền ("ảo quá ~~không~~", "luôn ~~ý~~", "có quà ~~nữa~~", "em máy ~~này~~")."""
    i = int(t / FRAME_S)
    n = int(span / FRAME_S)
    peak = _DB[i]
    for k in range(1, n):
        j = i + direction * k
        if j <= 0 or j >= len(_DB) - 1:
            break
        peak = max(peak, _DB[j])
        if _DB[j] <= _DB[j - 1] and _DB[j] <= _DB[j + 1] and _DB[j] <= peak - drop:
            return round(j * FRAME_S, 3)
    return round(t + direction * 0.12, 3)  # không thấy trũng: nới 0,12 s


def edge_start(text, near):
    """mép đầu ngay trước chữ `text`: mốc ĐẦU chữ của phiên âm đúng giờ (render 2026-10-16 phiên âm lại đều đủ chữ đầu
    câu), lùi 0,02 s. Không quét lùi tìm trũng — dễ lấn vào câu trước ("…đấy rồi | Ngày đầu tiên")."""
    return round(_w(text, near)["start"] - 0.02, 3)


def edge_end(text, near):
    """mép cuối ngay SAU chữ `text` (trũng âm lượng đầu tiên khi quét tới từ cuối chữ)."""
    return _first_trough(_w(text, near)["end"], +1)


def cut(a_text, a_near, b_text, b_near):
    return edge_start(a_text, a_near), edge_end(b_text, b_near)


# thư viện đoạn (giờ nguồn, chương)
P = {}
P["date"] = (*cut("Mọi", 3.78, "vàng", 10.66), "pain")          # đi date chỉ cần make up đẹp… với mình thì không… răng ố vàng
P["nhakhoa"] = (*cut("Chắc", 13.4, "nữa", 20.04), "pain")       # ra nha khoa tẩy trắng: vừa đau ví vừa buốt răng
P["ice"] = (*cut("Thử", 20.20, "luôn", 25.82), "pain")          # ngày date anh ấy đưa ly nước đá — buốt tận chân răng
P["sol"] = (*cut("Nhưng", 27.6, "xong", 33.5), "benefit")       # đừng lo, Quỳnh có tip: kit Smilee là xong
P["day1_3"] = (*cut("Ngày", 40.70, "7", 48.54), "result")       # ngày đầu mức 7–8 → sau 3 ngày mức 6–7
P["day7"] = (*cut("Cho", 53.4, "ý", 59.8), "result")            # 7 ngày liên tiếp → thang số 3 số 4 luôn ý
P["split"] = (*cut("Chỉ", 59.9, "không", 66.26), "proof")       # chỉ cần ngậm 15 phút mà từ số 7 lên số 3 (khung trước/sau)
P["benefit"] = (*cut("Quan", 68.74, "buốt", 74.70), "benefit")  # vừa hiệu quả, an toàn, tiết kiệm thời gian, không ê buốt
P["kit"] = (*cut("Đầu", 88.4, "người", 94.98), "benefit")       # trong kit: thước thang đo, có sẵn máy, 3 bút gel
P["usage"] = (*cut("Trước", 128.06, "nếu", 140.6), "speed")    # đánh răng, lau khô, chà gel, ngậm + nút, 10′ xanh → 5′ đỏ
P["durable"] = (*cut("Cái", 157.50, "này", 160.82), "saving")   # máy bền tới 5 năm, mình dùng con máy này
P["gel"] = (*cut("Hết", 161.0, "á", 165.58), "saving")          # hết gel thì mua gel mới, lúc nào cũng thủ sẵn
P["confident"] = (*cut("Khi", 119.3, "lần", 124.8), "benefit")  # khen kết: ra ngoài giao tiếp thoải mái nói cười, tự tin x1000
P["cta"] = (*cut("Trước", 165.78, "này", 176.5), "cta")         # mua trong livestream của brand: voucher + quà, sale lớn, nhanh tay

# chỉnh tay các mép còn dính giọng (đo cực tiểu âm lượng quanh mép, 2026-10-16; nền nhạc ≈ −19…−26 dB)
P["kit"] = (P["kit"][0], edge_end("nha", 95.24), P["kit"][2])   # sau "…cho mọi người rồi nha" (trước "Một")
P["cta"] = (P["cta"][0], edge_end("này", 176.70), P["cta"][2])  # sau "…một em máy này" (trước "Để")
P["day7"] = (max(53.27, edge_start("Cho", 53.32)), P["day7"][1], P["day7"][2])  # trước "Cho đến ngày hôm nay", sau điểm chuyển cảnh 53,267       # cực tiểu −12 dB ngay trước "Cho đến ngày hôm nay" (sau điểm chuyển cảnh 53,25)
P["sol"] = (27.32, P["sol"][1], P["sol"][2])          # cực tiểu −14 dB trước "Nhưng mà mọi người đừng lo"
P["durable"] = (P["durable"][0], P["gel"][0], P["durable"][2])  # nối liền đoạn gel (khe 160,7–161,7 không có chỗ ngắt)



# tách CTA: "mua trong livestream… có voucher, có quà nữa" | "sắp có dịp sale lớn… nhanh tay sắm một em máy này"
P["cta_a"] = (P["cta"][0], edge_end("nữa", 171.80), "cta")  # sau "…có quà nữa" | "Đang sắp có…"
P["cta_b"] = (P["cta_a"][1], P["cta"][1], "cta")
P["p15"] = (*cut("Chỉ", 60.18, "không", 66.26), "proof")      # chỉ cần ngậm 15 phút mỗi ngày mà từ số 7 lên số 3, có ảo quá không
P["day7"] = (P["day7"][0], P["split"][0], "result")           # … thang số 3 số 4 luôn ý (dừng trước câu 15 phút)
P["vang"] = (edge_start("Bởi", 8.20), edge_end("vàng", 10.66), "pain")  # khe −15 dB trước "Bởi vì một chi tiết nhỏ — đó chính là răng ố vàng" (giữ trọn câu)

HOOKS = {
    "h_kq": (edge_start("từ", 62.80), edge_end("3", 64.80), "proof"),   # "từ thang răng số 7 lên răng số 3" + khung trước/sau
    "h_vang": (edge_start("Bởi", 8.20), edge_end("vàng", 10.66), "pain"),                                           # trọn câu "Bởi vì… răng ố vàng" (voice liền mạch hơn mép cảnh 8,467)
    "h_gel": (P["gel"][0], edge_end("mới", 163.48), "saving"),         # "hết gel thì mình có thể mua gel mới"
    "h_mua": (P["cta_a"][0], edge_end("Brand", 167.82), "cta"),        # "trước là mình mua con này ở trong livestream của Brand"
}
HOOKS = {k: (a, round(min(b, a + 3.0), 3), ch) for k, (a, b, ch) in HOOKS.items()}  # hook ≤ 3 s
TAIL = ["kit", "durable", "gel"]
ORDER = {
    "h_kq": ["day1_3", "day7", "usage", "nhakhoa", "benefit"] + TAIL + ["vang", "confident", "cta_a", "cta_b"],
    "h_vang": ["p15", "day1_3", "day7", "nhakhoa", "benefit", "usage"] + TAIL + ["confident", "cta_a", "cta_b"],
    "h_gel": [("gel", "rest"), "p15", "day1_3", "day7", "usage", "nhakhoa", "benefit", "kit", "durable",
              "confident", "cta_a", "cta_b"],
    "h_mua": [("cta_a", "rest"), "p15", "day1_3", "day7", "nhakhoa", "benefit", "usage"] + TAIL + ["confident", "cta_b"],
}


def seg(a, b, ch=None, **kw):
    d = {"source": SRC, "start": a, "end": b}
    if ch:
        d["chapter"] = ch
    d.update(kw)
    return d


class V:
    def __init__(self, vid, hook_type, preset, hook, rationale):
        h = HOOKS[hook]
        kw = {"protect": True} if hook == "h_kq" else {}
        self.d = {"id": vid, "hook_type": hook_type, "preset": preset, "hook": seg(h[0], h[1], h[2], **kw),
                  "segments": [], "overlays": [], "graphics": [], "effects": [], "captions": False,
                  "rationale": rationale}
        self.pieces = [(h[0], h[1])]
        for k in ORDER[hook]:
            if isinstance(k, tuple):  # phần còn lại của đoạn sau hook (nối liền)
                a, b, ch = P[k[0]]
                a = h[1]
            else:
                a, b, ch = P[k]
            self.d["segments"].append(seg(a, b, ch))
            self.pieces.append((a, b))

    def out(self, t):
        acc = 0.0
        for a, b in self.pieces:
            if a - 1e-6 <= t <= b + 1e-6:
                return round(acc + (t - a), 3)
            acc += b - a
        return None

    def text(self, a, b, text, sub="", y=None, style=None, **kw):
        s = self.out(a)
        if s is None or self.out(b) is None:
            return
        style = style or ("vox" if self.d["preset"] == "vox" else "lower")
        o = {"text": text, "sub": sub, "style": style, "position": "bottom", "animation": "pop", "emphasis": [],
             "start": s, "end": round(s + (b - a), 3), **kw}
        if y is not None:
            o["y"] = y
        self.d["overlays"].append(o)

    def gfx(self, a, b, kind, **kw):
        s = self.out(a)
        if s is None or self.out(b) is None:
            return
        self.d["graphics"].append({"kind": kind, "start": s, "end": round(s + (b - a), 3), **kw})


def common(v):
    """Người dùng 2026-10-16: giữ CỠ GỐC của thẻ/motion (bản 1), chỉ né gương mặt KOL — đặt trên đầu hoặc dưới cằm,
    được ra ngoài vùng an toàn (`free`); vẫn tránh phụ đề in sẵn (`avoid`)."""
    SUB_TOP = [(0.08, 0.26)]      # phụ đề in sẵn ở trên (phần lớn video)
    SUB_BOTTOM = [(0.62, 0.74)]   # phụ đề in sẵn ở dưới (đoạn cách dùng)
    a, b, _ = P["benefit"]
    # thang màu 7–8 → 3–4 sau 7 ngày (số KOL tự đo)
    v.gfx(a + 0.1, a + 3.0, "shade", from_shade=8, to_shade=3, days=7, label="", y=0.6, free=True, avoid=SUB_TOP)
    # NHA KHOA vs SMILEE đúng câu "vừa hiệu quả vừa an toàn… không ê buốt"
    v.gfx(a + 3.1, b, "versus", left_label="NHA KHOA", right_label="SMILEE",
          steps=["đau ví | 15 phút tại nhà", "buốt răng | không ê buốt"], y=0.6, free=True, avoid=SUB_TOP)
    # trong kit có gì — sáng từng món đúng lúc kể
    ka, kb, _ = P["kit"]
    v.gfx(ka, kb, "steps", label="TRONG KIT CÓ GÌ", compact=True, y=0.6, free=True, avoid=SUB_TOP,
          steps=["THƯỚC THANG ĐO | đo độ trắng", "MÁY ĐÈN LED | có sẵn trong hộp", "3 BÚT GEL | dùng cả liệu trình"],
          times=[round(word(t, n) - ka, 2) for t, n in (("thước", 89.5), ("máy", 91.5), ("3", 93.6))])
    # cách dùng: thanh đèn 10′ xanh → 5′ đỏ (đèn đỏ thật từ ~137,4 s); phụ đề ở dưới → ưu tiên trên đầu
    ua, ub, _ = P["usage"]
    v.gfx(133.6, ub, "light_timer", y=0.13, free=True, avoid=[(0.0, 0.125)] + SUB_BOTTOM, rows=[  # thẻ một hàng, dưới vùng TikTok che
        {"min": 10, "title": "ÁNH SÁNG XANH", "sub": "làm trắng", "color": "blue", "at": 0},
        {"min": 5, "title": "ÁNH SÁNG ĐỎ", "sub": "dịu nướu", "color": "red", "at": round(137.4 - 133.6, 2)}])
    da, db_, _ = P["durable"]
    v.text(da + 0.2, db_, "BỀN TỚI *5 NĂM*", sub="bấm giỏ hàng xem ngay", y=0.6, free=True, avoid=SUB_TOP)
    ga, gb, _ = P["gel"]
    if v.d["hook"]["start"] != HOOKS["h_gel"][0]:  # bản gel: câu này đã là hook — không chồng thẻ
        v.gfx(ga + 0.1, gb, "gel_refill", label="HẾT GEL? *MUA LẺ*", sub="không mua lại máy", y=0.6, free=True,
              avoid=SUB_TOP)
    ca, cb, _ = P["cta_b"]  # đoạn "sắp sale lớn… nhanh tay" — có ở mọi bản, kể cả bản mở bằng CTA
    v.gfx(ca + 0.1, min(cb, 174.9), "live_cta", label="BẤM VÀO LIVE", sub="voucher + quà tặng", y=0.6,
          free=True, avoid=SUB_TOP)



variants = []
for vid, hook_type, preset, hook, why in (
    ("lo-08_proof_hieu-qua", "result_first", "proof", "h_kq",
     "Hiệu quả trước: khung trước/sau 'từ số 7 lên số 3' → ngày 1/3/7 → cách dùng → gỡ nỗi lo (nha khoa, không ê buốt) "
     "→ kit, bền 5 năm, gel mua lẻ → răng ố vàng (cầu nối) → tự tin → live."),
    ("lo-08_pink_vang-hieu-qua", "pain", "pink", "h_vang",
     "Nỗi đau → hiệu quả ngay: 'răng ố vàng' rồi lập tức 'chỉ cần ngậm 15 phút mà từ số 7 lên số 3' + hành trình 7 ngày."),
    ("lo-08_routine_gel-nhanh", "cost_compare", "routine", "h_gel",
     "Bút gel → hiệu quả nhanh: 'hết gel mua gel mới, lúc nào cũng thủ sẵn' → '15 phút mà từ 7 lên 3' → cách dùng."),
    ("lo-08_gift_mua-review", "cta_first", "gift", "h_mua",
     "Kêu gọi mua → review: 'mình mua trong livestream, có voucher, có quà' → review hiệu quả thật → gỡ nỗi lo → "
     "'sắp sale lớn, nhanh tay' + bấm vào live."),
):
    v = V(vid, hook_type, preset, hook, why)
    common(v)
    variants.append(v)

for v in variants:
    for k in ("overlays", "graphics"):
        v.d[k].sort(key=lambda o: o["start"])
edl = {"_doc": "lo-08 (2026-10-16): nguồn dqamii, 4 biến thể mặc định mới (hiệu quả trước, nỗi đau → hiệu quả, gel → "
               "hiệu quả nhanh, mua → review). Sinh bằng build_edl.py (mẫu ở examples/smilee-lo-08/).", "job": "lo-08",
       "variants": [v.d for v in variants]}
Path(__file__).with_name("edl.json").write_text(json.dumps(edl, ensure_ascii=False, indent=1), encoding="utf-8")
for v in variants:
    print(f"{v.d['id']}: {sum(b - a for a, b in v.pieces):.1f} s, {len(v.d['overlays'])} chữ, {len(v.d['graphics'])} đồ hoạ")
