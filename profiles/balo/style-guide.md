# Style guide riêng — Balo thời trang (KHUNG)

Trạng thái: KHUNG 2026-10-16 — **tinh chỉnh khi có source balo đầu tiên** (màu, preset, cỡ thẻ, cảnh tiền).
Luật chung: `library/style-guide.md` (đọc trước). Thông số: `profiles/balo/tokens.json` (gói đồ hoạ `balo`).

## 1. Riêng balo

- Khung đầu mạnh nhất: **nhét đồ thật vào balo** (laptop trượt vào vừa khít), **nước lăn trên mặt vải**, hoặc **dáng balo khi đeo** cùng outfit đẹp.
- Biến thể 3 mặc định ("hook sản phẩm phụ / giá trị"): ngăn đặc biệt (laptop chống sốc, ngăn bí mật, cổng sạc) hoặc giá trị (bền, đa dụng) → hiệu quả nhanh (vừa đồ, nhẹ).
- Số luôn được nhấn: **kích thước laptop (15,6″)**, **số ngăn**, **kích thước (cm)**, **trọng lượng**, **giá**.
- Không bịa thông số: kích thước, chất liệu, mức chống nước chỉ lấy từ lời KOL hoặc `product.md` đã xác nhận.
- Không làm thử nước giả bằng đồ hoạ — chỉ minh hoạ khi source có cảnh thử thật.
- Chương `saving` = giá trị (bền, đa dụng, giá); `extra` = phụ kiện nhỏ (móc khoá, túi phụ) — chỉ giữ khi đang nói dở chuỗi khen.

## 2. Preset (khung — màu tạm)

| Preset | Khi dùng | Chữ |
|---|---|---|
| `brand` (mặc định) | mọi bản thương hiệu | thẻ `lower` nền than, accent cam/xanh |
| `vox` | giải thích, so balo thường | chữ bút dạ vàng, khoanh đỏ |
| `kinetic` | hook mạnh | như brand + `kinetic` 1–1,5 s đầu |
| `proof` | kết quả trước: nhét đồ, thử nước, mặc thử | `wipe` trước/sau, `size_fit`, `compartments` |
| `lookbook` | phối nhiều outfit, nhịp theo nhạc | thẻ kem chữ mực, ít chữ |
| `ugc` | bản số lượng GMV Max | chữ `plain` trắng viền đen |
| `gift` | tựu trường, Tết, quà tặng | thẻ than, accent cam |
| `reply` | trả lời câu hỏi ("có vừa laptop 15,6 không?") | thẻ trắng chữ mực |

## 3. Đồ hoạ gói `balo` (component Remotion cơ bản — `remotion/src/BaloGraphics.tsx`)

| Ý | Cú pháp |
|---|---|
| Vừa laptop / kích thước | `{"kind": "size_fit", "start", "end", "label": "VỪA LAPTOP *15,6″*", "sub": "45 × 30 × 15 cm"}` — đúng lúc KOL nhét laptop/nói kích thước |
| Checklist ngăn | `{"kind": "compartments", "label": "BÊN TRONG CÓ GÌ", "steps": ["NGĂN LAPTOP \| chống sốc", "NGĂN CHAI NƯỚC \| 2 bên", "NGĂN BÍ MẬT \| sau lưng"], "times": [0, 1.4, 2.8]}` — tích từng dòng đúng lúc nói |
| Huy hiệu tính năng | `{"kind": "badge", "icon": "water", "label": "*CHỐNG NƯỚC*", "sub": "vải Oxford 900D"}` — icon: water, material, weight, zip, warranty, star |
| So balo thường | gói chung: `versus` (`left_label` mặc định "BALO THƯỜNG"), `nope` |
| Đếm ngày dùng / bền | gói chung: `counter` |

Ghi chú tinh chỉnh khi có source đầu tiên: đo chỗ trống thật trên khung (balo thường ở giữa/dưới khung khi quay lưng,
mặt KOL ở trên) → chọn `y` mặc định; đổi màu theo nhận diện thương hiệu; thêm icon balo đúng dáng sản phẩm thật.
