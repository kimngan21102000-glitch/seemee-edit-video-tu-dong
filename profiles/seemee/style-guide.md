# Style guide riêng — SeeMee (máy uốn tóc xoăn lơi PREMIUM 2026)

Luật chung: `library/style-guide.md` (đọc trước). Ở đây chỉ ghi luật RIÊNG sản phẩm; luật riêng thắng khi mâu thuẫn.
Thông số máy đọc: `profiles/seemee/tokens.json` (màu tím dâu/hồng, 5 preset, chỉ gói đồ hoạ `chung` — **không** bật `nha_khoa`).
Thông tin sản phẩm: `product.md`; cam kết tự highlight: `commitments.txt`.

## 1. Riêng sản phẩm
- Khung đầu mạnh nhất: **lọn tóc xoăn bung khỏi trục**, hoặc trước/sau tóc thẳng → cả mái xoăn lơi (KOL hất tóc, soi gương).
  Cảnh trục tự cuốn tóc và tay chạm vỏ máy không bỏng là cảnh tiền thứ hai (`protect: true`).
- 3 nâng cấp độc quyền PREMIUM 2026 là xương sống phần body — nói theo thứ tự người xem lo nhất:
  **chống bỏng dày gấp 2** → **thẻ cài tóc rộng gấp 1,5 (uốn nhiều tóc, nhanh hơn)** → **phủ tinh dầu, +85% bóng mượt**.
- Biến thể 3 mặc định ("hook giá trị"): **bảo hành 12 tháng tại nhà** / quà trong hộp (kẹp + lược hồng) / giá sale so giá gốc
  → hiệu quả nhanh (lọn bung sau 10 giây).
- Gỡ nỗi lo trước khi nói tiền: bỏng (hàng rào chống bỏng), hư tóc (chọn mức nhiệt 140–200°C, phủ tinh dầu), vụng tay (máy tự cuốn).
- Chương `speed` = 10 giây/lọn, trục 65 vòng/phút; `saving` = tự làm ở nhà thay ra tiệm, bảo hành 12 tháng;
  `extra` = dây 170 cm xoay 360°, kẹp + lược trong hộp.
- Số luôn được nhấn: **10 GIÂY**, **GẤP 2** (chống bỏng), **GẤP 1,5** (thẻ cài), **+85%** (bóng mượt), **4 MỨC NHIỆT**, **12 THÁNG**, **32MM**.
- Không bao giờ: chỉnh màu/độ xoăn của tóc thật trong footage, đổi con số của nhãn hàng, nêu tên đối thủ (ANN, PRO EXTRA, AKIO…)
  hay tiệm tóc, hứa "không bao giờ bỏng"/"không hư tóc" (xem `forbidden.txt`). Số đánh giá/lượt bán chỉ ghi khi có ảnh
  chụp có ngày (`claims_pending.txt`). Giá chỉ ghi khi brief của lô xác nhận đợt sale.

## 2. Preset
| Preset | Khi dùng | Chữ |
|---|---|---|
| `brand` (mặc định) | mọi bản thương hiệu | thẻ `lower` nền tím dâu, chữ trắng, accent hồng/vàng kim |
| `vox` | giải thích, nỗi đau (bỏng, vụng tay, tóc xơ) | chữ bút dạ vàng, khoanh đỏ |
| `proof` | kết quả trước: tóc thẳng → xoăn lơi, lọn bung | `wipe`/`collage` trước/sau, `kinetic` "10 GIÂY" |
| `ugc` | bản số lượng GMV Max | chữ `plain` |
| `reply` | trả lời câu hỏi khán giả ("có bỏng không?", "có hư tóc không?") | thẻ trắng chữ mực, câu hỏi ở hook |

Thẻ nền hồng nóng + chữ trắng tương phản thấp và chìm trên máy/đồ hồng → thẻ luôn nền tím dâu (`berry`) hoặc trắng;
hồng chỉ làm màu nhấn (`*…*`).

## 3. Đồ hoạ nên dùng
Chỉ gói **chung** (`tokens.json → graphics_packs: []`). Gợi ý ghép:
- Ba nâng cấp PREMIUM 2026 → `steps` (sáng từng dòng đúng lúc KOL nói) hoặc `versus` **MÁY CŨ vs SEEMEE** (✗ bỏng tay / ✓ chống bỏng gấp 2…).
- Hẹn giờ 10 giây / lọn bung → `kinetic` "*10 GIÂY*" hoặc nhãn `lower`; sau đó cắt vào cảnh lọn bung
  (`counter` chỉ đếm "NGÀY 1 → N" — không hợp sản phẩm này).
- Trước/sau tóc → `wipe` hoặc `collage` sau khi cảnh trước/sau gốc chạy trọn.
- Ra tiệm vs tự uốn ở nhà → `cost_compare` **RA TIỆM vs SEEMEE** (chỉ khi KOL nói số tiền cụ thể).
- Chỉ vào trục/thẻ cài/vỏ chống bỏng → `effects.zoom_to` + `callout` + nhãn ("TRỤC *32MM*", "THẺ CÀI *GẤP 1,5*").
- CTA → `live_cta` / `end_card` ("BẢO HÀNH *12 THÁNG*").
