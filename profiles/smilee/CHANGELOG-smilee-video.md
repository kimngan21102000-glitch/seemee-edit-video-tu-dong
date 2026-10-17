# Lịch sử skill smilee-video

## v2.6 — 2026-10-16 (feedback lo-06, lo-07)

- Không che mặt KOL: `y` ghi tay của thẻ/chữ chỉ là vị trí mong muốn — che mặt thì `vf/placement.py` tự dời; trường mới `avoid` (dải y phụ đề in sẵn); công cụ soát `scripts/face_cover_check.py`.
- Chuyển cảnh: mọi preset cắt thẳng (bỏ chồng mờ — đè hình/đè khẩu hình giữa các cảnh).
- Bỏ chip teaser "CUỐI VIDEO" — chỉ minh hoạ điều KOL đang nói.
- Thẻ/motion `free`: giữ cỡ gốc, chỉ né mặt (trên đầu / dưới cằm), được ra ngoài vùng an toàn, tránh phụ đề in sẵn (`avoid`).
- 4 biến thể mặc định: hiệu quả trước · nỗi đau/lợi ích → hiệu quả ngay · bút gel → hiệu quả nhanh · kêu gọi mua → review.
- Cắt không lấn voice (feedback lo-08): mép đầu = đầu chữ phiên âm, mép cuối = trũng âm lượng đầu tiên sau cuối chữ; nguồn có nhạc nền bỏ `vf snap`; trường `video_end` — tiếng chạy hết câu, hình dừng ở điểm chuyển cảnh và làm chậm khúc cuối.
- Thẻ đèn: từng thẻ một (10′ xanh → 5′ đỏ cùng chỗ), một hàng, màu "kính tối" cố định; preset gift đổi nền tím mận (hồng nóng chữ trắng chỉ 2,9:1).

## v2.5 — 2026-10-15 (lô lo-05)

- `vf snap`: mép đoạn về **khoảng lặng thật đo được** (≥ 30 ms dưới −26 dB) trong ±0,25 s, cả hai phía — không tin ranh giới chữ của phiên âm (lệch tới 0,2 s; lo-05 thừa chữ "nữa" sau "mua lẻ thêm gel"). Nói liền không có khoảng lặng → tắt tiếng mẩu chữ kề ≤ 80 ms (`mute_head`/`mute_tail` trên đoạn, giữ hình).
- Thứ tự: đoạn khen kết ngay trước CTA; tiện ích phụ (`extra`) chỉ giữ khi nằm trong chuỗi liệt kê khen, không thì bỏ (thay luật lo-04).
- Đồ hoạ mới: `nope` (miếng dán gạch chéo), `cost_compare` (cột chi phí theo tỉ lệ), `gel_refill` (bút gel mua lẻ); `steps` có `times` (sáng đúng lúc nói) + `compact` (thẻ gọn nửa dưới); `callout.y` đặt nhãn tay; graphic `xc` đặt tay được.

## v2.4 — 2026-10-15 (feedback lo-04: 3–3,5đ, bản thử _v2 ≥ 3,5đ)

| Feedback | Thay đổi |
|---|---|
| Transition chưa mượt | Bỏ whip/giấy lướt → chồng mờ (xfade) 0,3 s ở ranh giới chương, gạt mềm cho vox; thời lượng giữ nguyên (`vf/render.py: plan_transitions`) |
| Zoom nhẹ mỗi khi chuyển câu giật cục | Bỏ zoom chèn đoạn dài (fill_pace) và zoom xen kẽ ở cắt nhảy; cắt nhảy chồng mờ 0,2 s; bỏ luật lint "đổi nhịp mỗi 4 s" |
| Khung trước/sau nhỏ trên nền tím | Thanh gạt thành thẻ lớn ~1000 px nổi trên video đang chạy; đếm ngày thành thẻ gọn — hạn chế thẻ toàn màn hình (liền mạch là ưu tiên số 1) |
| Thẻ chữ che chủ thể đang dùng kit | Thẻ nhỏ hơn (lower 60 px); vùng bảo vệ mặt kéo xuống dưới cằm (miệng ngậm máy, tay cầm máy) |
| Tiện lợi du lịch nên để sau, trước CTA; đầu video tập trung nỗi đau/lợi ích, hiệu quả, trước/sau | Chương `extra`; lint thứ tự (extra sau bằng chứng, bằng chứng trong 45% đầu) |
| Còn dính mẩu tiếng thừa ở điểm cắt | `vf snap` (`vf/audiocut.py`): đo năng lượng âm thanh, dời mép về khoảng lặng (ra ngoài ≤ 0,25 s, vào trong ≤ 60 ms); render báo `dính tiếng`; fade mép 25 ms |
| (vận hành) file cũ đang mở làm render lỗi | Lưu tên `_v2` thay vì mất bản vừa render |

## v2.3 — 2026-10-14 (lo-03 chấm 3đ: "đã cải thiện, còn nhiều lỗi edit nhỏ" — tự soát, không render lại)

| Lỗi tìm được (tự soát lo-03) | Thay đổi |
|---|---|
| Chữ tự kéo dài vắt qua điểm cắt, đè chữ in sẵn của nguồn (cả 6 bản) | `auto_fix` dừng ở điểm cắt và hết `text_free`; không đủ chỗ → `đọc không kịp … rút chữ` (`vf/creative.py: text_limit`) |
| Mất chữ đầu câu ("~~Ai~~ mà nằm vùng"), cắt giữa từ ("Tất"), đứng hình 0,25 s ở mép | `lint_cuts`: render báo `mất chữ đầu câu`, `cắt giữa từ`, `đứng hình` (dòng `~`) |
| Bộ dò cảnh bỏ sót điểm cắt (bản 2) | Luật: xem sheet 0,5 s + dò lại bằng scdet quanh mép hook |
| Chữ kinetic đè lên răng | Luật: chữ/thẻ lớn không đè thứ cần cho xem |

Việc cần làm: L-cut (hình đoạn trước chạy thêm thay vì đứng hình khi mép lệch điểm chuyển cảnh).

## v2.2 — 2026-10-14 (feedback lô lo-03, không render lại)

| Feedback | Thay đổi |
|---|---|
| SFX whoosh quá nhiều, quá to, lấn tiếng video | Không SFX khi chữ hiện / zoom / ranh giới chương; chỉ đồ hoạ quan trọng ≥ 0,5 s, cách nhau ≥ 2 s, −16 dB (`tokens.auto_sfx`, `vf/creative.py`) |
| Ảnh ghép trước/sau (vox) díu vào nhau | Ảnh ghép bỏ qua vùng an toàn: 2 ảnh ~900 px, một trên một dưới, không chồng, nhãn không bị che |
| Cần typographic + motion graphic đa dạng hơn (vàng → trắng, thang đo theo ngày 1 → 7, đếm ngày, educate vox/motion, CTA bấm vào live) | Style guide mục 7 "Việc cần làm tiếp" (làm khi người dùng yêu cầu bản tiếp theo) |
| Rút kinh nghiệm + gợi ý cải thiện sau mỗi lần render | SKILL.md bước 6: mục bắt buộc "Rút kinh nghiệm & gợi ý cải thiện" |

## v2.1 — 2026-10-14 (tối ưu thời gian render, vòng feedback)

Người dùng chốt: bỏ bước bản nháp, render thẳng bản final rồi feedback; skill học từ feedback để sửa phần được yêu cầu.
- `vf/cache.py`: dấu vân tay mỗi biến thể (edl + brief + nguồn + code/tokens/SFX/font) → bản không đổi được giữ (`GIỮ …`); `--force` để render lại.
- `vf render --jobs 2` (mặc định): 2 biến thể song song; Remotion `--timeout=120000` + thử lại 1 lần khi quá hạn khởi tạo trình duyệt; chép font có khoá.
- NVENC (h264_nvenc, cq 21) khi driver hỗ trợ, tự quay về libx264 khi lỗi; `vf doctor` báo trạng thái (máy hiện tại: driver 591.66 < 610 ffmpeg 9 cần → đang dùng CPU).
- SKILL.md: mục "Feedback của người dùng" — ghi đúng biến thể vào review.csv → video-learnings → chỉ sửa phần được yêu cầu → render lại (bản không đổi tự giữ).

## v2.0.1 — 2026-10-14 (pilot lo-03)

- `zoom_to` có `place` (mặc định bám răng (0.5, 0.34)): răng ở 1/3 trên khung để vòng khoanh nằm trong vùng an toàn (cột nút 300 px từng kéo lệch vòng khoanh khỏi răng ở bản thử lo-03_1).
- Nhãn khoanh/ảnh ghép đọc cú pháp `*nhấn*` (trước hiện nguyên dấu `*`).
- Mẫu script sinh edl neo theo giờ nguồn: `jobs/lo-03/build_edl.py`; ưu tiên nội dung theo người dùng: nỗi đau/lợi ích, hook giữ chân, hiệu quả trước/sau, cách dùng chi tiết, thời gian duy trì, mua lại bút gel, CTA mua hàng.

## v2 — 2026-10-14 (gộp bản đóng gói từ Claude chat `smilee-video-SKILL.md` vào vf + Remotion)

Người dùng chốt các xung đột giữa bản chat và repo:

| Xung đột | Quyết định | Thay đổi |
|---|---|---|
| Kiến trúc: bản chat viết cho `tools/render_edl.py` (Pillow) | Đưa luật v2 vào vf + Remotion | Không xây bộ tools/ mới; thêm thành phần, lint, lệnh vào `vf/` và `remotion/src/` |
| Claim: bản chat chặn tới khi có bằng chứng; repo không chặn 3 cam kết | Không chặn gì, không cảnh báo, cam kết càng nổi bật càng tốt | Bỏ kiểm `forbidden.txt` / `claims_pending.txt` (file giữ làm tham khảo); chỉ chặn cụm brief của lô ghi trong `forbidden` |
| Disclaimer, nhãn Quảng cáo, nhãn AI | Bỏ hết | Không có thành phần `disclaimer`, không trường `ad_label`/`ai_content` |
| Chữ in sẵn: bản chat cho đặt khác vùng dọc | Giữ cũ: chỉ thêm ở khoảng `text_free` | Không đổi |
| Nhịp: bản chat đoạn ≥ 0,8 s + flash | Giữ feedback cũ: cảnh ≥ 1,2 s, không flash | `tokens.timing.scene_min_s` 1,2; proof/gift dùng whip |
| Độ dài: bản chat 20–30 s, 6 biến thể | 45 s – 1 phút 40 tuỳ source, ±10 %, phải đủ ý | `content_checklist` + lint chương; mặc định 6 biến thể |
| Preset: bản chat 6, repo v1.4 6 khác | Gộp: pink, vox, kinetic, proof, ugc, gift, routine, reply; học dần | `tokens.presets`; result_rewind → proof, beat → kinetic |

Lấy từ bản chat (không xung đột):
- `library/brand/tokens.json` — nguồn thông số duy nhất (màu, cỡ chữ, thời gian, vùng an toàn, audio, auto SFX, preset, font).
- Vùng an toàn phải 300 px khi y > 840 (chặt hơn v1.4); chữ nửa dưới lệch trái (`xc`).
- EDL: `chapter`, `protect`, `rapid`; thành phần mới `light_timer`, `kinetic` (kinetic hook), `end_card`; chữ nhấn `*accent*` / `[accent2]`; bảng màu theo preset.
- Lint (cảnh báo, không chặn): chữ đầu tiên ≤ 0,3 s, giữ chữ tối thiểu (tự sửa), không cắt 0,4 s sau chữ, protect ≥ 2,5 s, đổi nhịp ≤ 4 s, CTA 3 s cuối, trộn hệ chữ, chương còn thiếu.
- Chuyển cảnh ở ranh giới chương theo preset: whip (ffmpeg), paper (`paper_swipe`, Remotion), cut.
- Âm thanh: SFX theo sự kiện (`tokens.auto_sfx`), `vf make-sfx` tạo SFX tạm bằng numpy, nhạc tự hạ khi có giọng (sidechain).
- `vf sheet` (ảnh tổng quan có mốc giờ + viền vùng an toàn), `vf expand` (ma trận hooks × bodies × ctas × presets cho GMV Max), `vf learn --write` (`library/learnings-stats.md` theo preset × hook × độ dài); `review.csv` thêm `preset`, `length_s` và cột số liệu TikTok.
- Font theo `tokens.fonts` (Be Vietnam Pro nếu có file, không thì Montserrat).

Chưa làm: phụ đề từng từ đổi màu theo preset, chữ có chân nghiêng (Lora) cho dòng dẫn Vox, các hiệu ứng ở style guide mục 7 "Chưa có".

## v1.4 — 2026-10-14 (nghiên cứu xu hướng quảng cáo TikTok 2026 + yêu cầu vùng an toàn)

| Vấn đề / gợi ý | Thay đổi |
|---|---|
| Chữ/hình **thêm vào** có thể bị giao diện TikTok che (vùng an toàn chỉ áp cho phần Claude thêm; nội dung source gốc giữ nguyên) (placement cũ chỉ chừa 6 % trên, 20 % đáy, không tính cột nút phải) | `vf/safezone.py` (trên 240 px, dưới 660 px, hai bên 120 px, cột nút 180 px từ y 840): placement chỉ đặt trong vùng an toàn, hộp chữ thu hẹp ở hàng cột nút (`max_w`), `y` ghi tay và `callout` bị kéo vào; Remotion nhận `safe` (thẻ đếm ngày, ảnh ghép, nhãn khoanh, chữ Vox xuống dòng); chữ tĩnh và phụ đề ASS cũng theo vùng an toàn. QA đọc kênh alpha lớp chữ → `vùng an toàn: …` + CẦN XEM; `*_sheet.png` kẻ viền đỏ vùng an toàn. |
| lo-02 không có nhạc lẫn SFX dù pipeline hỗ trợ | SFX tự động theo hiệu ứng từ `library/brand/sfx/` (`vf/creative.py`), −8 dB; `vf doctor` cảnh báo khi thiếu SFX; style guide mục 7. |
| Trộn nhiều ngôn ngữ đồ hoạ trong một bản; biến thể khó thành phương án test khác nhau | `preset` mỗi biến thể (ugc, result_rewind, vox, routine, reply, beat — style guide mục 11); QA nhắc hook trùng trong cùng lần render. |
| CTA chỉ ở ~94 % thời lượng; người xem rời mạnh sau ~25 s | CTA mềm ở 60–85 % + CTA cuối; bản cắt ngắn `cutdown_seconds` / `cutdown_of`. |
| Typography: chỉ một font, không quy tắc đọc | Style guide mục 12: tối đa 2–3 kiểu chữ, phân màu theo vai trò, chỉ từ khoá chuyển động, hook có chữ trước 0.5 s, ≤ 3.5 từ/giây — QA nhắc (`creative`). |
| Motion graphic mới theo xu hướng beauty | `shade` (thang màu răng, chỉ dùng số người nói nói ra) và `wipe` (thanh gạt trước/sau từ cảnh thật). Các hiệu ứng chưa làm ghi ở style guide mục 14. |
| Vòng học chỉ có điểm cảm tính | Nhắc điền `views`, `retention_3s`; video-learnings có mốc retention 3 s và học theo preset. |

## v1.3.1 — 2026-10-14 (lo-02 v7–v9: 3đ)

- Vox giữ nguyên. Người dùng nhắc: **không bỏ** motion graphic răng vàng → trắng khi đèn xanh/đỏ, vầng sáng, thẻ đếm ngày — dùng tiếp khi hợp bối cảnh (style guide mục 10, video-batch-edit).

## v1.3 — 2026-10-14 (feedback lo-02 v4–v6: 2.5đ)

| Feedback | Thay đổi |
|---|---|
| Đoạn nguồn đã có hình/video minh hoạ thì không cần thêm | Bỏ hàm răng vector, vầng sáng, thẻ đếm ngày trên cảnh đèn/bảng màu; chỉ thêm đồ hoạ ở đoạn trơn. |
| Đoạn có chữ in sẵn thì không thêm chữ | Giữ `text_free`; bỏ thẻ đè lên đoạn có sticker. |
| Chuyển cảnh nhanh; để trọn cảnh trước/sau gốc rồi mới thêm graphic | Cảnh BEFORE → AFTER gốc chạy trọn (54.48–59.15); ảnh ghép TRƯỚC/SAU đặt ngay sau. Cách dùng chỉ lấy phần đèn (bỏ chuỗi 0.8 s). |
| Phong cách Vox | `zoom_to` (ống kính bám răng, `vf/track.py`), `callout` (khoanh tay → mũi tên → bút dạ), `collage` (giấy, băng keo, ảnh cắt từ nguồn), chữ `vox`. Style guide mục 10. |
| Răng vàng: zoom vào răng hoặc chỉ vào rồi mới ghi chú | Zoom 1.6 bám răng + khoanh + mũi tên + nhãn "RĂNG Ố VÀNG", đúng thứ tự. |

## v1.2 — 2026-10-14 (feedback lo-02: v1 3đ, v2 3đ, v3 2đ)

| Feedback | Thay đổi |
|---|---|
| Chuyển cảnh nhanh làm xém chữ/hình | Nguyên nhân: chuỗi dựng nhanh 0.6 s có sẵn trong nguồn (nhật ký 7 ngày). Quy tắc cảnh ≥ 1.2 s; bỏ chuỗi đó, thay bằng cảnh before/after dài + thẻ đếm ngày. |
| Cần motion graphic đèn xanh/đỏ làm răng vàng → trắng | `graphics.kind = "teeth"`: hàm răng vector, thanh LED xanh quét → răng trắng dần, pha đỏ dịu nướu, ghi "Minh họa". |
| Không mở đầu bằng chi phí; tập trung nỗi đau răng vàng, làm trắng nhanh, biến đổi vàng → trắng, gel tiết kiệm | lo-02 v4–v6 viết lại theo hướng này; "gel tiết kiệm" đặt gần cuối. ("cấp tốc" là cụm cấm → không đưa lên chữ.) |
| Tham khảo phong cách 2 video mẫu | `library/style-guide.md` (ĐÃ DUYỆT): thẻ `lower` hai dòng tím mận/hồng, nhãn `tag`, thẻ `counter` toàn màn hình, bảng màu. |
| Nguồn có chữ in sẵn: chỉ thêm chữ ở cảnh không có chữ | Brief `text_free` (khoảng giờ nguồn không có chữ); `strip_text` chỉ giữ chữ nằm trong các khoảng đó. |

## v1.1 — 2026-10-14 (lô lo-02)

- Yêu cầu người dùng: nguồn đã có chữ in sẵn trên hình thì không thêm chữ minh hoạ. Brief có trường `text_sources`; `vf/motion.py: strip_text` bỏ mọi chữ chồng lên đoạn của các nguồn đó (cả cam kết tự động), hiệu ứng hình giữ nhưng bỏ nhãn.

## v1 — 2026-10-14 (sau lô pilot lo-01)

Feedback người dùng sau lo-01 và cách xử lý:

| Feedback | Thay đổi |
|---|---|
| Video bị vấp, díu hình; vài khung hình cắt lỗi, chuyển cảnh không dứt khoát | `vf analyze` ghi `scenes.json` (điểm chuyển cảnh, `vf/scenes.py`). Render bỏ mẩu cảnh < 0.5 s ở mép đoạn, giữ khung hình kề bên (tiếng không đổi); cắt nhảy trong cùng cảnh thì phóng to xen kẽ ×1.12. Bỏ hiệu ứng `flash`. Skill yêu cầu cắt theo `scenes.json`. |
| Font lỗi tiếng Việt; chữ cần viền, nền dễ nhìn, không che vật thể/mặt | Font Montserrat ExtraBold trong `library/brand/`. Chữ hook có viền + nền tối mờ, thẻ nhãn/CTA hồng Smilee. `vf/placement.py` dùng OpenCV (nhận diện mặt + mật độ chi tiết) tự chọn vị trí dọc cho từng chữ. |
| Chưa có hiệu ứng minh hoạ đèn xanh/đỏ và before/after răng | `graphics` trong edl: `light` (viền sáng + đồng hồ đếm phút) và `whiten` (icon răng vàng → trắng, ghi "Hình minh họa" vì hồ sơ sản phẩm cấm tự bịa before/after). Remotion: `remotion/src/Graphics.tsx`. |

Sửa lỗi cài đặt trên Windows:
- Repo ở đường dẫn dài → `pip` lỗi `WinError 206`: clone vào đường dẫn ngắn (`C:\dev\game-dev`).
- faster-whisper GPU thiếu `cublas64_12.dll`: thêm `nvidia-cublas-cu12`, `nvidia-cudnn-cu12` vào phụ thuộc, `vf/transcribe.py` tự nạp DLL.
- OpenCV giữ bản 4.x (bản 5 bỏ file Haar cascade).

## v0 — 2026-10-13

Quy trình đầu tiên: doctor → status → brief → analyze → edl → render → QA → review.csv.
