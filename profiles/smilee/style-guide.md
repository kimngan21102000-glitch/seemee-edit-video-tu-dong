# Style guide riêng — Smilee (kit trắng răng)

Phần **riêng sản phẩm** tách từ style guide Smilee v2.6 (2026-10-16). Luật chung (cắt tiếng, né mặt, vùng an toàn, cắt thẳng,
4 biến thể, thẻ màu…) ở `library/style-guide.md` — đọc cả hai; luật ở đây thắng khi mâu thuẫn.
Thông số máy đọc: `profiles/smilee/tokens.json` (màu, 8 preset, gói đồ hoạ `nha_khoa`). Lịch sử skill: `CHANGELOG-smilee-video.md`.

## 1. Riêng Smilee

- **Không bao giờ chỉnh màu răng thật** trong footage. Hiệu ứng "vàng → trắng" chỉ dùng hình minh hoạ (`whiten`, `teeth`).
- 3 cam kết (trắng sau 5–7 ngày, bật 3–4 tone, trắng như sứ) tự highlight khi người nói nói ra (`commitments.txt`), ưu tiên giữ các đoạn đó, được đưa lên hook.
- Khung đầu mạnh nhất: cận răng/kết quả, đèn đang sáng, hộp quà mở.
- Biến thể 3 mặc định ("hook sản phẩm phụ"): **bút gel** — "hết gel chỉ mua lẻ, không mua lại máy" → hiệu quả nhanh (15 phút, số ngày).
- Gỡ nỗi lo trước khi nói tiền: ê buốt (đèn đỏ dịu nướu), so nha khoa (~8 triệu, 1/3 chi phí).
- Chương `saving` = mua lại gel, 1/3 nha khoa; `extra` = nam châm, du lịch, sạc, hộp.
- Số luôn được nhấn: **10 PHÚT** (xanh – đèn xanh), **5 PHÚT** (đỏ – đèn đỏ), **NGÀY 7**, **3–4 TONE**.
- Không nêu tên phòng khám/đối thủ.

## 2. Preset (8)

Mỗi biến thể đúng 1 preset; các biến thể trong lô khác nhau rõ về **kiểu hook hoặc preset** (không chỉ khác chữ). Bảng màu, chuyển cảnh, auto SFX của từng preset ở `tokens.presets`.

| Preset | Khi dùng | Chữ | Chuyển cảnh | Âm thanh |
|---|---|---|---|---|
| `pink` (mặc định) | mọi bản thương hiệu | thẻ `lower` tím mận 2 tầng, accent hồng/xanh | cắt thẳng | pop, whoosh, click |
| `vox` | giải thích, nỗi đau, "vì sao" | chữ `vox` đen trên bút dạ vàng, khoanh đỏ, ảnh ghép giấy | cắt thẳng | giấy, bút dạ |
| `kinetic` | hook mạnh | như pink + `kinetic` 1–1,5 s đầu | cắt thẳng | slam theo từng cụm |
| `proof` | kết quả trước | `wipe`/`collage` trước/sau, `counter`, `shade` | cắt thẳng | tick, ding |
| `ugc` | bản số lượng GMV Max | chữ `plain` trắng viền đen, không hộp | cắt thẳng | không auto SFX |
| `gift` | 20.10, Tết, Valentine | thẻ hồng đậm | cắt thẳng | pop, ding |
| `routine` | quy trình 15 phút: gel → đèn xanh → đèn đỏ | thẻ `lower` accent xanh, `light_timer`, `teeth` | cắt thẳng | click, giữ tiếng ASMR thật |
| `reply` | trả lời câu hỏi khán giả (xử lý phản đối) | thẻ trắng chữ mực, câu hỏi ở hook | cắt thẳng | pop |

Preset cũ của v1.4: `result_rewind` → `proof`, `beat` → `kinetic` (edl tự đổi). Preset nào thắng được học dần qua `vf learn --write` (theo preset × hook × độ dài) — điều chỉnh bảng này khi có bằng chứng.

## 3. Thư viện đồ hoạ (gói `nha_khoa` + chung)

Nguyên tắc (lo-04): đồ hoạ **nổi trên video đang chạy**, hạn chế thẻ toàn màn hình cắt người nói ra khỏi khung. **Không che mặt KOL** (lo-06/lo-07): `y` ghi tay chỉ là vị trí mong muốn — pipeline tự dời nếu che mặt; phụ đề/chữ in sẵn khai bằng `avoid: [[y0, y1]]`; sau render chạy `scripts/face_cover_check.py <lô>`. Chỉ thêm thẻ minh hoạ đúng điều KOL đang nói — không chip teaser rời ("CUỐI VIDEO: …"). Thẻ so sánh trước/sau to (~1000 px), đúng tỉ lệ ảnh, được bỏ qua vùng an toàn. Thẻ chữ không che mặt, miệng đang ngậm máy, tay cầm máy — đặt trên đầu hoặc dưới ngực, cỡ nhỏ hơn.


| Thành phần (skill v2) | Trong edl | Ghi chú |
|---|---|---|
| label | `overlays` (`lower`, `tag`, `hook`, `plain`, `cta`, `commit`, `vox`) | chữ theo preset |
| light_timer | `graphics.kind = "light_timer"`, `rows` | **Từng thẻ một** (feedback lo-08): 10′ xanh trước, đúng lúc đèn chuyển đỏ (`at`) thì thay bằng 5′ đỏ cùng chỗ — một hàng, trong vùng an toàn trên đầu KOL, không sát mép trên (TikTok che). Màu cố định **"kính tối"** (người dùng chọn 2026-10-16): nền đen mờ `rgba(20,18,24,.92)`, số + viền + thanh tiến độ theo màu đèn (xanh `#40A0FF`, đỏ `#FF4D4D`), chữ trắng — tương phản 18:1, không theo preset; mặc định `y` 0,13 (ngay dưới vùng TikTok che) |
| tooth_morph | `whiten` | icon răng vàng → trắng, ghi "Hình minh họa" |
| (hàm răng vector) | `teeth` | đèn xanh quét làm răng trắng dần, đèn đỏ dịu nướu — người dùng muốn giữ |
| draw_circle | `effects.zoom_to` (track teeth) + `graphics.callout` | zoom → khoanh → mũi tên → nhãn |
| polaroid | `collage` | 1–2 ảnh thật cắt từ nguồn, băng keo, nền giấy. Thẻ nền kín → **bỏ qua vùng an toàn**: 2 ảnh to (~900 px), một trên một dưới, giãn ra, không chồng; nhãn TRƯỚC/SAU không bị che (feedback lo-03) |
| day_counter | `counter` | NGÀY 1 → 7, 1–1,5 s |
| kinetic_hook | `kinetic`, `words` | cụm `*như này*` tô màu nhấn |
| end_card | `end_card`, `label`, `sub`, `live` | CTA cuối trong vùng an toàn |
| (thang màu) | `shade` | chỉ dùng số mức người nói nói ra |
| (thanh gạt trước/sau) | `wipe`, 2 `stills` | từ cảnh trước/sau thật |
| (chuyển cảnh giấy) | `paper_swipe` | render tự thêm ở ranh giới chương cho preset vox |

Gợi ý ghép:
- Cảnh đèn xanh/đỏ → `light_timer` (hoặc `teeth` + `light`). Không chồng nếu nguồn đã có chữ "ÁNH SÁNG XANH".
- Nỗi đau răng vàng → `zoom_to` bám răng → `callout` → nhãn.
- Kết quả → `wipe` hoặc `collage` sau khi cảnh trước/sau gốc chạy trọn; `shade` khi người nói nói số mức.
- Ngay sau cảnh dùng máy → `whiten`/`teeth` 1,5–2 s.

**Việc cần làm tiếp sau lô lo-05 (người dùng chọn 2026-10-15, lo-05 đạt 3,5–4đ) — ưu tiên:**
- **Thẻ CÁCH CŨ vs SMILEE**: hai cột ✗/✓ nổi trên video đúng chỗ chuyển "miếng dán ê buốt" → "chân trời mới" (miếng dán ê buốt ✗ / đèn đỏ dịu nướu ✓).
- **Checklist "TRONG HỘP CÓ GÌ"**: tích từng món đúng lúc KOL kể (hướng dẫn, thang đo, 3 bút gel) — thay chuỗi cảnh hộp cắt nhanh chỉ có hình.
- **Vòng đếm 15 PHÚT** khi nói "mỗi tối 15 phút" + **thanh đèn xanh 10′ → đỏ 5′** trong thẻ bước 3, chạy theo màu đèn thật của nguồn.
- **Bản xử lý phản đối "Ê buốt không?"** (preset `reply`): thẻ câu hỏi khán giả ở hook, trả lời bằng đoạn "lần đầu hơi ê nhẹ, lần sau hết" (songvy 127–134 s) + đèn đỏ dịu nướu.
- Nghiên cứu motion/bố cục hay trên TikTok mỗi ngày (`library/research/`) và học video tham khảo người dùng bổ sung hàng tuần (skill `video-style-learning`) → gợi ý thêm.

**Việc cần làm tiếp sau lô lo-04 (người dùng "ok" 2026-10-15) — đã làm ở lo-05 (miếng dán gạch chéo, thẻ bước đồng bộ lời, cột 1/3, bút gel, khoanh thang đo):**
- **Thẻ các bước đồng bộ lời nói**: sáng từng bước đúng lúc KOL nói (không đợi nói xong mới tóm tắt). Đoạn nguồn có phụ đề in sẵn ở trên → thẻ nhỏ ở **nửa dưới**, không trùng vùng chữ in sẵn (người dùng đồng ý nới luật cho trường hợp này).
- **Motion ở 20 s đầu sau hook** (đoạn giữ chân quan trọng nhất): ví dụ miếng dán gạch chéo + "Ê BUỐT", hộp Smilee bật vào khi nói "chân trời mới".
- **Cột so sánh chi phí** ("chỉ bằng 1/3 nha khoa") và **icon bút gel** ("hết gel chỉ mua lẻ, không mua lại máy").
- Bản hook kết quả trước: chỗ nhắc lại trước/sau dùng hình khác hook (cận thang đo + khoanh), không lặp đúng khung hook.
- Chia motion đều, ưu tiên nửa đầu video (lo-04 dồn nửa sau).

**Việc cần làm tiếp (người dùng gợi ý sau lô lo-03, làm khi có yêu cầu bản tiếp theo):**
- Thang đo độ trắng **theo ngày**: con trỏ thang màu chạy cùng nhãn NGÀY 1 → 7 (`shade` + `days`).
- **Các bước cách dùng** (`steps`): Bôi gel → Đèn xanh 10′ → Đèn đỏ 5′ → Xúc miệng — cho đoạn giải thích khi nguồn chưa đủ rõ (dạng vox hoặc motion tuỳ tình huống).
- **Thanh thời gian duy trì** 8–10 tháng (lịch/tháng chạy); **so sánh chi phí** máy 1 lần + bút gel nhiều lần vs nha khoa ~8 triệu.
- **CTA bấm vào live**: huy hiệu LIVE nhấp nháy + mũi tên chỉ avatar/giỏ hàng (trong vùng an toàn), đếm ngược ưu đãi live.
- Typographic đa dạng hơn: chữ có chân nghiêng (Lora) cho dòng dẫn vox, chữ nằm sau người, số đếm chạy (3 → 4 TONE, 700K → 600K).

**Chưa có (cần làm thêm code):** chữ nằm sau người (tách nền), dừng hình + viền trắng cut-out, sản phẩm tách nền bay vào ở CTA, cột so sánh 8 triệu vs 800k, phụ đề từng từ đổi màu theo preset, chữ có chân nghiêng (Lora) cho dòng dẫn Vox.

## Phụ lục — video mẫu đã học (chỉ kỹ thuật)

- **A** `snaptik.vn_7690505641718271284.mp4` (33,4 s): bản dựng lại clip KOL hộp quà 20/10. Cảnh ~3,3 s, thẻ chữ tím mận 2 tầng gần mỗi cảnh, thẻ toàn màn hình khi chuyển ý, thanh đèn có tiến độ, nhãn TRƯỚC/SAU, polaroid.
- **B** `snaptik.vn_7694846295957081365.mp4` (45 s): motion graphic giải thích; câu dẫn nghiêng nhỏ + ô từ khoá viết hoa, bộ đếm số chạy.
