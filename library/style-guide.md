# Style guide CHUNG — edit video tự động (mọi sản phẩm)

Trạng thái: ĐÃ DUYỆT — tách từ style guide Smilee v2.6 (2026-10-16), chỉ giữ các luật **không phụ thuộc sản phẩm**.
Mỗi luật có nguồn gốc là feedback thật của người dùng qua 8 lô Smilee (lo-01 … lo-08); bằng chứng chi tiết ở
`profiles/smilee/learnings.md`.

Đọc kèm (bắt buộc mỗi lô):
- `profiles/<hồ sơ>/style-guide.md` — luật riêng sản phẩm (preset, đồ hoạ ngành, số luôn nhấn, điều cấm riêng). **Luật riêng thắng luật chung khi mâu thuẫn.**
- `library/tokens.base.json` (máy đọc: khung, vùng an toàn, cỡ chữ, thời gian, âm thanh, font) + `profiles/<hồ sơ>/tokens.json` (màu, preset, gói đồ hoạ) — render gộp hai file.
- `library/learnings.md` — bài học chung; `profiles/<hồ sơ>/learnings.md` — bài học riêng.

## 1. Nguyên tắc gốc

1. **Một hệ chữ cho cả video.** Mỗi biến thể đúng 1 `preset` (định nghĩa trong tokens của hồ sơ). Không trộn kiểu thẻ, chữ bút dạ (vox) và sticker trong cùng video.
2. **Đủ ý trước, đẹp sau.** Video phải có đủ: nỗi đau/lợi ích, hiệu quả, bằng chứng, nhanh/dễ, tiết kiệm/giá trị, CTA (`tokens.content_checklist`). Thiếu ý thì kéo dài video, không cắt cho ngắn.
3. **Thật hơn bóng bẩy.** Giữ cảnh thật, giọng thật. Đồ hoạ để giải thích, không để làm đẹp kết quả.
4. **Không bịa** before/after, review, số liệu không có trong tư liệu. Không chỉnh hình sản phẩm/kết quả thật trong footage — minh hoạ thì vẽ (đồ hoạ ghi "minh hoạ").
5. **Cam kết và lợi ích càng nổi bật càng tốt.** Không chặn claim, không disclaimer (người dùng chốt 2026-10-14). Cam kết của sản phẩm (`profiles/<hồ sơ>/commitments.txt`) tự highlight khi người nói nói ra. Chỉ chặn cụm mà brief của lô ghi trong `forbidden`.
6. **Nội dung có sẵn trong source gốc giữ nguyên** (chữ in sẵn, sticker, phụ đề KOL): không dời, không cắt, không né đoạn vì nó.
7. **Mượt, liền mạch là ưu tiên số 1** của người dùng: hạn chế thẻ toàn màn hình cắt người nói khỏi khung; đồ hoạ nổi trên video đang chạy.

## 2. Cấu trúc và độ dài

- Độ dài ưu tiên **45 s – 1 phút 40** tuỳ source (±10 %); brief/lệnh của người dùng ghi đè. Bản cắt ngắn tuỳ chọn: brief `cutdown_seconds` + `"cutdown_of"`.
- **Thứ tự chương** (`chapter` trên mỗi đoạn): `hook → pain/benefit → result → (hiệu quả nhanh thế nào) → proof → speed (cách dùng) → saving (giá trị, tiết kiệm) → khen kết → cta`. Hiệu quả/bằng chứng trong **45 % đầu**. **Đoạn khen kết ngay trước CTA**. **Tiện ích phụ** (`extra`) chỉ giữ khi KOL đang nói dở chuỗi liệt kê khen; nói xong ý chính rồi thì **bỏ**. Lint nhắc chương thiếu và thứ tự sai.
- **4 biến thể mặc định mỗi lô** (người dùng chốt 2026-10-16 — ưu tiên khách đang cân nhắc, đẩy hiệu quả lên sớm):
  1. **Hiệu quả trước**: hook kết quả (trước/sau thật, số đo) → hiệu quả cụ thể → nhanh/dễ → gỡ nỗi lo → đáng tiền → CTA.
  2. **Nỗi đau/lợi ích → hiệu quả ngay**: hook nỗi đau hoặc lợi ích, **ngay sau hook là hiệu quả**, câu chuyện kể sau.
  3. **Hook sản phẩm phụ / giá trị → hiệu quả nhanh**: hook về phần bổ sung, phụ kiện, chi phí duy trì hay giá trị thêm (Smilee: "hết gel chỉ mua lẻ"; balo: ngăn laptop, chống nước…) → hiệu quả nhanh → phần còn lại.
  4. **Kêu gọi mua → review**: hook CTA/ưu đãi (bấm live, voucher) → review hiệu quả thật → gỡ nỗi lo → CTA cuối.
  Chung: câu chuyện nỗi đau dài rút còn 3–5 s và đặt sau phần hiệu quả; gỡ nỗi lo trước khi nói tiền; **CTA cuối một lệnh**. Preset chọn theo nguồn và `learnings-stats.md` của hồ sơ.
- **Khung hình đầu là hình mạnh nhất**. Chữ/đồ hoạ đầu tiên ≤ 0,3 s (trừ khi nguồn đã có chữ in sẵn ở hook). Hook ≤ 3 s. **Không mở đầu bằng giá.**
- CTA hai lần: CTA mềm ở 60–85 % thời lượng + CTA/`end_card` trong 3 s cuối.

## 3. Ngữ pháp cắt dựng

| Luật | Giá trị |
|---|---|
| Cảnh ngắn nhất | **1,2 s**, nhắm 2–4 s. Chuỗi cắt nhanh có chủ đích: `rapid: true` |
| Giữ chữ tối thiểu | `max(1,2 s; 0,6 + 0,25 × số từ)` — render tự kéo dài, nhưng không vắt qua điểm cắt, không lấn khỏi `text_free` |
| Không cắt cảnh trong | 0,4 s sau khi chữ vừa hiện |
| Cảnh "tiền" (trước/sau, mở hộp, dùng sản phẩm, cận kết quả) | `protect: true`, ≥ 2,5 s, để cảnh gốc chạy trọn; không đặt chữ giữa khung đè chủ thể |
| Đổi nhịp | bằng **nội dung** (cảnh/ý mới, đồ hoạ minh hoạ), **không** chèn zoom để đổi nhịp; **không zoom nhẹ mỗi khi chuyển câu** |
| Chuyển cảnh | **Cắt thẳng** ở mọi điểm chuyển, **mọi preset** (lo-07: chồng mờ đè hình hai cảnh/hai khẩu hình). Tiếng chỉ làm mềm mép 25–40 ms, không chồng tiếng. **Không** whip, giấy lướt, flash |
| Chữ có sẵn trong nguồn | nguồn vào `text_sources`; **chữ chỉ ở khoảng `text_free`** (giờ nguồn không có chữ in sẵn). Nguồn đã giải thích đủ thì không thêm. Phụ đề in sẵn gần như suốt video → không khai text_free, đặt thẻ nhỏ ở nửa không có phụ đề và khai `avoid` |
| Đoạn nguồn đã tự minh hoạ | để nguyên, không chồng đồ hoạ cùng ý |
| Zoom vào chi tiết | zoom → khoanh → mũi tên → nhãn, đúng thứ tự |
| Không dùng | đoạn có clip người sáng tạo/người nổi tiếng khác chèn trong nguồn; đoạn mời livestream của KOL (trừ biến thể kêu gọi mua) |
| Mép đoạn | bắt đầu ở **đầu câu/ý** — không bỏ chữ đầu câu, không cắt giữa từ; mép lệch điểm chuyển cảnh > 0,15 s gây đứng hình → dời về đúng điểm chuyển cảnh, hoặc nối thêm câu kế để chạy liền qua điểm đó |

### 3.1 Cắt tiếng — không lấn voice (lo-04, lo-05, lo-08)

- **Mép đầu = đầu chữ phiên âm − 0,02 s.**
- **Mép cuối = trũng âm lượng đầu tiên SAU cuối chữ phiên âm** (tìm ≤ 0,3 s — cuối chữ của phiên âm thường sớm 0,1–0,2 s khi nói liền). Không tìm "chỗ lặng nhất" hai phía: dễ rơi vào bên trong chữ cuối.
- Nguồn sạch (không nhạc nền): `vf snap` dời mép về khoảng lặng thật (±0,25 s), nói liền thì tắt tiếng mẩu dính ≤ 80 ms. **Nguồn có nhạc nền: KHÔNG chạy `vf snap`** (kéo mép lấn chữ kế); mép thật sự dính giọng là mép > −17 dB.
- Nói hết câu mà đoạn sau là cảnh khác → **`video_end`** trên đoạn: tiếng chạy tới hết chữ, hình dừng ở điểm chuyển cảnh, **khúc cuối làm chậm 0,2–1 s**.
- Đầu mỗi lô: phiên âm lại 1 đoạn ngắn + đo trũng âm lượng để biết nguồn lệch bao nhiêu (có nguồn lệch đều +0,3 s cả file → cộng OFF cho mọi mốc).
- Sau render: **phiên âm lại output**, soát mọi chỗ nối không mất/thừa chữ. Lint `cắt giữa từ` / `dính tiếng` là lỗi thật, không bỏ qua.
- Mẫu code: `examples/smilee-lo-08/build_edl.py` (`edge_start`, `edge_end`, `dip`) + `slow_tails.py`.

## 4. Typography

- Font chính theo `tokens.fonts.main` (Be Vietnam Pro Black/ExtraBold — thiết kế cho tiếng Việt; thiếu thì Montserrat ExtraBold). Hồ sơ có font riêng thì để trong `profiles/<hồ sơ>/brand/fonts/` và khai trong tokens của hồ sơ. Chừa ~22 % cỡ chữ phía trên dòng cho dấu chồng (Ề, Ẫ, Ỗ).
- Thang cỡ chữ (px, 1080×1920): hook 92 · claim 84 · cta 76 · label 64 · dòng phụ 38–44 · note 32 · kinetic 150.
- Nhãn tối đa 2 tầng: dòng chính ≤ 6 từ (~12–14 ký tự, không để chữ lẻ rớt dòng), dòng phụ ≤ 8 từ, tối đa 3 dòng. ≤ 3,5 từ/giây, tối đa 2 khối chữ cùng lúc.
- Nhấn màu: `*từ*` = accent, `[từ]` = accent2; tối đa 2 cụm mỗi nhãn. **Số luôn được nhấn** (số phút, số ngày, kích thước, mức giá…). Tránh dấu gạch trong cụm số dài ("600–700K" bị ngắt dòng) — viết gọn ("TỪ 600K").
- Chỉ từ khoá chuyển động (`highlight` + `emphasis`, `pop`); đặt đúng lúc người nói nói ra từ đó.
- Không phụ đề toàn bộ lời (`captions: false`) trừ khi brief yêu cầu.

## 5. Vùng an toàn TikTok (chỉ cho phần thêm vào)

Khung 1080×1920 (`library/tokens.base.json → safe_zone`, `vf/safezone.py`): chừa **trên 240 px, dưới 660 px, trái/phải 120 px, phải 300 px khi y > 840** (cột nút avatar/tim/bình luận/chia sẻ).

- Pipeline tự đặt `y` và tâm ngang `xc`: nửa trên căn giữa, nửa dưới lệch trái; hộp chữ tự hẹp lại. Đừng ghi `y` trừ khi buộc phải.
- QA đọc kênh alpha lớp thêm vào: chỗ đặc lấn vùng cấm → `vùng an toàn: …`, biến thể **CẦN XEM** — phải sửa. `*_sheet.png` kẻ viền đỏ vùng an toàn.
- Ngoại lệ: thẻ nền kín toàn màn hình, thẻ so sánh trước/sau lớn (~1000 px), thẻ **`free`** (cỡ gốc, chỉ né mặt — xem mục 6).
- Thẻ/chữ không sát mép trên (thanh tìm kiếm/tab TikTok che): nằm dưới y ≈ 0,13.

## 6. Né mặt KOL và đặt thẻ (lo-04 … lo-07)

- **Không che mặt KOL**, miệng, tay đang cầm/dùng sản phẩm. Thẻ đặt **trên đầu hoặc dưới cằm/ngực**.
- `y` ghi tay chỉ là vị trí mong muốn — pipeline tự dời nếu che mặt. Phụ đề/chữ in sẵn của nguồn khai bằng **`avoid: [[y0, y1]]`**, không ghim `y`.
- **Thẻ `free`** (người dùng 2026-10-16): giữ **cỡ gốc**, không thu nhỏ để nhét vừa; chỉ cần né mặt, được lấn vùng chú thích TikTok phía dưới; vẫn tránh phụ đề in sẵn.
- Khung 2 người lệch tầng: chỗ trống là góc trên phía người đứng thấp — đặt tay `y` + `xc`, thẻ hẹp (~480 px).
- Sticker/emoji in sẵn của nguồn cũng là nội dung phải né.
- Cận mặt kín khung: không khoanh/chữ ở cảnh đó, đưa ý vào thẻ khác.
- **Soát bắt buộc sau render**: `python scripts/face_cover_check.py <lô>` liệt kê thẻ/chữ che mặt (≥ 8 %) theo từng bản → dời rồi render lại.
- Thẻ đồ hoạ mới phải đo đủ chiều cao thật (icon + nhãn + dòng phụ + nảy spring) trước khi đặt.

## 7. Thẻ đồ hoạ — luật chung

- **Chỉ thêm thẻ minh hoạ đúng điều KOL đang nói.** **Không chip teaser rời** ("CUỐI VIDEO: …", lời hứa không liên quan đoạn đang nói).
- Thẻ "sáng đúng lúc nói" (bước, checklist): từng dòng sáng **đúng lúc người nói nói tới**, không đợi nói xong mới tóm tắt. Phụ đề in sẵn của KOL thường hiện trước lời ~0,5 s — bám tiếng thật, chấp nhận lệch.
- **Màu thẻ tương phản cao với nền video**: đo trên nguồn — nền bão hoà (xanh/đỏ/hồng nóng) dễ hoà vào hình (1,0–1,6:1). Nền tối (đen mờ, màu đậm của thương hiệu) hoặc trắng mới tách khỏi hình. Thẻ có màu theo ý nghĩa (đèn, cảnh báo) dùng kiểu **"kính tối"**: nền đen mờ `rgba(20,18,24,.92)`, chỉ số/viền/thanh tiến độ mang màu ý nghĩa, chữ trắng (tương phản ~18:1), không theo preset.
- Thẻ nhiều trạng thái (vd đồng hồ 2 pha): **từng thẻ một**, một hàng, cùng chỗ — không xếp chồng khối cao (bị đẩy lên sát mép trên).
- Preset có thẻ nền sáng: mọi chữ trên nền thẻ dùng **màu chữ của preset** (`PALETTE.cardText`), không cứng `#FFFFFF`.
- Motion chia đều, **ưu tiên 20 s đầu sau hook** (đoạn giữ chân quan trọng nhất).
- Trước/sau: để trọn cảnh trước/sau gốc rồi mới thêm thẻ; thẻ so sánh to (~1000 px), đúng tỉ lệ ảnh; nhắc lại trước/sau thì dùng hình khác hook.

### Bộ đồ hoạ

Gói theo hồ sơ (`tokens.json → graphics_packs`; render báo lỗi nếu dùng đồ hoạ của gói chưa bật):

| Gói | `graphics.kind` |
|---|---|
| **chung** (luôn bật) | `counter` (đếm ngày), `steps` (các bước), `versus` (cách cũ vs sản phẩm), `cost_compare` (cột chi phí), `live_cta` (bấm vào live), `end_card` (CTA cuối), `wipe` / `collage` (trước/sau), `callout` (khoanh), `kinetic` (chữ đập), `nope` (gạch chéo cách cũ), `refill` (phần bổ sung mua lẻ — tên cũ `gel_refill`), `paper_swipe` |
| **nha_khoa** (Smilee) | `teeth`, `whiten`, `shade`, `light`, `light_timer`, `zoom_to` + `track: "teeth"` |
| **balo** (khung) | `size_fit` (vừa laptop/kích thước), `compartments` (checklist ngăn), `badge` (chống nước/chất liệu) |

Cú pháp từng loại: docstring `Graphic` trong `vf/edl.py`. Nhãn mặc định theo hồ sơ (`tokens.graphic_defaults`, vd cột phải `cost_compare` = tên thương hiệu).

## 8. Âm thanh

- Giọng −14 LUFS. Nhạc nền dưới giọng 20 dB và tự hạ khi có giọng. Nhạc trend: để trống `music`, gắn nhạc Commercial Music Library trên TikTok.
- **SFX ít và nhỏ** (lo-03): không gắn khi chữ hiện, khi zoom, ở mỗi ranh giới chương. Chỉ ở đồ hoạ/chuyển cảnh **quan trọng** hoặc kéo dài > 0,5 s; cách nhau ≥ 2 s; −16 dB (`tokens.auto_sfx`). Preset kiểu UGC không auto SFX.
- File SFX ở `library/brand/sfx/` (hoặc `profiles/<hồ sơ>/brand/sfx/`); `vf make-sfx` tạo bản tạm.
- Giữ tiếng ASMR thật của nguồn (mở hộp, kéo khoá, bấm máy…).

## 9. Nên / không nên

**Nên:** một hệ chữ; đủ ý theo chương; hiệu quả sớm; giữ trọn cảnh tiền; zoom rồi mới chú thích; cam kết nổi bật; CTA giữa + cuối, một lệnh; 4 biến thể khác nhau rõ về kiểu hook hoặc preset; soát sheet + face_cover_check + phiên âm lại output.

**Không:** chữ đè chữ có sẵn; chữ ngoài `text_free`; che mặt KOL; chip teaser rời; mở đầu bằng giá; flash trắng; chồng mờ/whip; zoom mỗi câu; cảnh < 1,2 s; cắt lấn voice; bịa before/after/số liệu; dùng hình, nhạc, giọng, câu chữ nguyên văn của video tham khảo; meme/sticker trong preset thương hiệu.
