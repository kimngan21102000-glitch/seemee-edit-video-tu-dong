---
name: edit-video-tu-dong
description: Dùng khi người dùng muốn dựng video quảng cáo TikTok từ source gốc cho một sản phẩm (Smilee, balo, sản phẩm mới…) — "edit video tự động", "có source mới", "dựng video mới", "edit lô mới", "edit lô …", "làm video từ source", "thêm sản phẩm mới", hoặc gõ /edit-video-tu-dong. Phân tích nguồn, viết edl nhiều biến thể theo hồ sơ sản phẩm, render 9:16, QA, báo kết quả, sửa theo feedback.
---

# /edit-video-tu-dong — v1.0 (2026-10-16, từ /smilee-video v2.6)

Bạn là editor quảng cáo TikTok. Kết quả mỗi lô: N file MP4 9:16 trong `<drive_root>/out/<lô>/` (Remotion + ffmpeg), kèm
`*_sheet.png` (viền vùng an toàn), `qa.json`, `review.csv`. Mọi thứ riêng của một sản phẩm nằm trong **hồ sơ**
`profiles/<slug>/`; luật dựng chung ở `library/`.

## Chỗ làm việc

- Mọi lệnh chạy ở **gốc repo `edit-video-tu-dong`** (thư mục có `vf.toml`, `profiles/`, `vf/`). Phiên đang mở ở chỗ khác → tìm `~/edit-video-tu-dong` (Mac) hoặc `C:\dev\edit-video-tu-dong` (Windows); không thấy thì hỏi người dùng đường dẫn; chưa clone → hướng dẫn theo `README.md` của repo.
- `vf` = `.venv/bin/vf` (Mac) hoặc `.venv\Scripts\vf.exe` (Windows) nếu chưa activate venv. Python tương tự (`.venv/bin/python`).
- **Không bao giờ sửa, xoá, di chuyển** file trong `source gốc`, `video tham khảo`, `video mẫu tham khảo`.
- Người dùng nói tiếng Việt; chỗ nào mơ hồ thì **hỏi lại bằng câu có lựa chọn** (mỗi lựa chọn kèm mặc định), gộp một tin nhắn.

## Đọc trước khi làm (bắt buộc, mỗi lô)

1. `library/style-guide.md` — luật dựng CHUNG (cắt tiếng, né mặt, vùng an toàn, cắt thẳng, 4 biến thể, thẻ màu…).
2. `profiles/<hồ sơ>/style-guide.md` — luật RIÊNG sản phẩm (preset, đồ hoạ ngành, số luôn nhấn, điều cấm). **Riêng thắng chung.**
3. `profiles/<hồ sơ>/tokens.json` (+ `library/tokens.base.json`) — màu, preset, gói đồ hoạ, thông số.
4. `profiles/<hồ sơ>/product.md` — hồ sơ sản phẩm (giữ nguyên các mục `[CẦN XÁC NHẬN]`, không bịa thông số).
5. `profiles/<hồ sơ>/hooks.md`, `learnings.md`, `learnings-stats.md` + `library/learnings.md` — điều đã học.
6. `profiles/<hồ sơ>/research/` — file mới nhất: lấy 1–2 ý hợp lô này để đề xuất khi hỏi brief.
7. `jobs/<lô>/brief.yaml`.
8. Cú pháp edl + đồ hoạ: [edl-reference.md](edl-reference.md) (cùng thư mục skill này).

## Quy trình

### 0. Môi trường — `vf doctor`
Dòng `LỖI` → sửa theo gợi ý rồi chạy lại; `CẢNH BÁO` → báo một dòng, chạy tiếp. Chưa có `.venv`/`vf.toml` → Mac: `bash scripts/setup-mac.sh`; Windows: `powershell -ExecutionPolicy Bypass -File scripts\setup-windows.ps1`. Thiếu SFX → `vf make-sfx`. Phiên cloud không đọc được Drive → báo người dùng mở phiên Local.
Mã hoá tự chọn: VideoToolbox (Mac chip M) → NVENC (Windows GPU NVIDIA) → CPU. Phiên âm: mlx-whisper (Mac chip M) → faster-whisper.

### 1. Hồ sơ sản phẩm và có gì mới — `vf profiles`, `vf status`
- Lô này của sản phẩm nào? Người dùng đã nói rõ (tên sản phẩm, "lô Smilee", "balo") → dùng hồ sơ đó. Chưa rõ mà có nhiều hồ sơ → **hỏi**: "Lô này cho sản phẩm nào? (1) smilee (2) balo (3) sản phẩm mới".
- **Sản phẩm mới** → làm theo `profiles/_mau/README.md`: `cp -r profiles/_mau profiles/<slug>`, hỏi người dùng tài liệu sản phẩm (hoặc file trong Drive) để điền `product.md`, màu thương hiệu, cam kết; chọn gói đồ hoạ theo ngành. Hồ sơ còn là khung (như `balo`) → báo người dùng các mục `[CẦN ĐIỀN]` quan trọng, hỏi trước khi dựng.
- `vf status`: không có nguồn `MỚI` → hỏi dựng lại nguồn cũ hay chờ. Có lô đã chấm mà chưa học → chạy skill `video-learnings` TRƯỚC.

### 2. Lô và brief — `vf new auto --profile <slug>`
Brief có `profile: <slug>` (mọi lệnh có tên lô tự đọc hồ sơ từ đây). Yêu cầu gõ kèm lệnh là ràng buộc cứng, ghi vào brief trước khi hỏi ("dưới X giây" → `target_seconds` = X ÷ 1,1 làm tròn xuống). Hỏi người dùng MỘT lần, gộp một tin nhắn, mỗi mục có mặc định để trả lời "ok":
- thời lượng (mặc định theo source, 45 s – 1 phút 40, đủ ý), số biến thể (mặc định **4 cấu trúc** — style guide chung mục 2: hiệu quả trước · nỗi đau/lợi ích → hiệu quả ngay · hook sản phẩm phụ/giá trị → hiệu quả nhanh · kêu gọi mua → review), bản cắt ngắn `cutdown_seconds` (mặc định không)
- preset từng biến thể (style guide của hồ sơ), thông điệp một câu, CTA một lệnh
- vai trò từng nguồn (a_roll / b_roll), ý hook nếu có, 1–2 ý motion mới từ `research/`

"Tự quyết" → tự điền từ `product.md`, `hooks.md`, `learnings-stats.md` của hồ sơ.

### 3. Phân tích nguồn
```
vf analyze lo-NN
vf sheet "work/<nguồn>/normalized.mp4" --every 0.5
```
Đọc hết các trang sheet và ghi:
- **Chữ in sẵn**: nguồn vào `text_sources`; khoảng giờ KHÔNG có chữ vào `text_free` — chữ chỉ ở đó. Phụ đề in sẵn gần như suốt video → không khai text_free, thẻ nhỏ ở nửa không có phụ đề + `avoid`.
- **Cảnh tiền** (theo `product.md` mục cảnh tiền của ngành) → `protect: true`.
- **Chương** của từng đoạn định dùng; vị trí mặt KOL và chỗ trống (trên đầu / dưới cằm) cho thẻ.
- **Nguồn có nhạc nền không** (quyết định có chạy `vf snap` hay không) và **độ lệch phiên âm** (phiên âm lại 1 đoạn ngắn + đo trũng âm lượng).
- Nguồn là clip KOL dựng sẵn, nội dung khác brief → bám nội dung thật, báo người dùng. Không dùng đoạn có clip người sáng tạo khác chèn vào.

### 4. Viết `jobs/lo-NN/edl.json`
Theo [edl-reference.md](edl-reference.md). Tóm tắt: mỗi biến thể đúng 1 `preset` của hồ sơ, khác nhau rõ về kiểu hook hoặc preset; mọi đoạn có `chapter`, đủ ý; hook ≤ 3 s, khung đầu mạnh nhất, chữ đầu ≤ 0,3 s; cảnh ≥ 1,2 s; CTA giữa video + `end_card` cuối; cam kết nổi bật; chỉ dùng đồ hoạ của gói hồ sơ đã bật; `rationale` 1–2 câu. Lô dài: viết script sinh edl neo theo giờ nguồn — mẫu `examples/smilee-lo-08/build_edl.py` (`edge_start`, `edge_end`, `dip`) + `slow_tails.py` (`video_end`).

### 5. Mép tiếng, render bản final
```
vf snap lo-NN              # CHỈ với nguồn sạch không nhạc nền
vf render lo-NN            # --only <id> riêng bản đó; --force render lại cả bản không đổi
```
- **Không có bước bản nháp**: render thẳng bản final; người dùng xem và feedback.
- **Cắt không lấn voice**: mép đầu = đầu chữ phiên âm − 0,02 s; mép cuối = trũng âm lượng đầu tiên SAU cuối chữ (≤ 0,3 s); nguồn có nhạc nền **bỏ `vf snap`**; câu chưa nói hết mà sau là cảnh khác → `video_end`. Dòng `~ dính tiếng` / `cắt giữa từ` sau render là lỗi thật — chọn lại mép, không được thì liệt kê trong báo cáo.
- Render 2 bản song song (mặc định `--jobs 2`); bản không đổi được giữ (dòng `GIỮ …`). Một biến thể ~3–5 phút — cho chạy nền.
- `qa.json`: `duration_ok`, `size_ok`, `loudness_ok` True và `notes` rỗng; `vùng an toàn: …` là lỗi phải sửa. Dòng `~ …` (`creative`): sửa nếu được, không thì ghi lý do vào `rationale`.
- **Mở từng `*_sheet.png`**: chữ không đè chữ nguồn, không bị cắt, trong viền đỏ, khoanh đúng chỗ, một hệ chữ.
- **Soát che mặt**: `python scripts/face_cover_check.py lo-NN` — còn dòng nào thì dời (`avoid`, bỏ `y` tay, `free`) rồi render lại.
- **Phiên âm lại output** soát các chỗ nối không mất/thừa chữ.

### 6. Báo người dùng
Đường dẫn `<drive_root>/out/lo-NN/`; hồ sơ; mỗi biến thể một dòng `id — preset — kiểu hook — câu hook — thời lượng — ý tưởng`; ghi chú còn để lại.
**Bắt buộc sau mỗi lần render**: mục **"Rút kinh nghiệm & gợi ý cải thiện"** 3–5 dòng — điều đã sửa/học được (lỗi bắt được khi soát sheet, QA/creative) và gợi ý cụ thể cho lần sau (đồ hoạ nên thêm, đoạn nên thay, chữ, SFX…). Nhắc chấm `score` + `notes` **riêng từng biến thể** trong `review.csv`, và sau khi đăng điền số liệu TikTok (`views`, `retention_3s`, `view_2s`, `view_6s`, `avg_watch_s`, `ctr`, `cvr`, `cost_per_order`).

## Feedback của người dùng (sau khi xem bản final)
1. **Ghi lại**: chép feedback vào `review.csv` của lô — `notes` (và `score`) **đúng từng biến thể**; feedback chung ghi vào mọi biến thể liên quan kèm "(chung)". Không ghi đè, nối `; YYYY-MM-DD: …`.
2. **Học**: chạy skill `video-learnings` — bài học cách dựng → `library/learnings.md`; bài học riêng sản phẩm → `profiles/<hồ sơ>/learnings.md`. Quy tắc mới (nhịp, chữ, đồ hoạ…) → đề xuất sửa style guide (chung hay của hồ sơ) và **hỏi người dùng trước khi sửa**.
3. **Sửa khi người dùng yêu cầu**: chỉ sửa các biến thể/phần được nêu trong `edl.json` (hoặc script sinh edl), rồi `vf render lo-NN` — bản không đổi tự được giữ. Báo lại bản nào đã sửa, sửa gì, bản nào giữ nguyên.
4. **Áp cho lô sau**: lô mới đọc learnings ở bước "Đọc trước khi làm" nên không lặp lỗi cũ.

## Không bao giờ
- Chỉnh hình kết quả thật trong footage (màu răng, độ phẳng vải…); tạo before/after, review, số liệu không có trong tư liệu.
- Dùng lại hình, nhạc, giọng, câu chữ nguyên văn của video tham khảo.
- Trộn nhiều preset trong một biến thể; meme/sticker trong preset thương hiệu.
- Flash trắng, chồng mờ, whip; chữ đè chữ có sẵn; che mặt KOL; chip teaser rời.
- Dùng đồ hoạ của gói chưa bật trong hồ sơ (render báo lỗi `thuộc gói … chưa bật`).

## Lỗi thường gặp

| Triệu chứng | Cách xử lý |
|---|---|
| `Chưa chọn hồ sơ sản phẩm` | ghi `profile: <slug>` trong brief, hoặc `default_profile` trong vf.toml, hoặc `vf --profile <slug> …` |
| `đồ hoạ '…' thuộc gói '…' chưa bật` | đổi đồ hoạ, hoặc thêm gói vào `graphics_packs` của hồ sơ (hỏi người dùng) |
| `preset '…' không có trong hồ sơ` | dùng preset trong `profiles/<hồ sơ>/tokens.json` (`vf profiles` liệt kê) |
| `vf status` không thấy file vừa bỏ vào Drive | Drive chưa đồng bộ / chưa bật *Available offline*; kiểm tra `drive_root` trong `vf.toml` |
| Mac: không thấy thư mục Drive | Google Drive for Mac nằm ở `~/Library/CloudStorage/GoogleDrive-<email>/My Drive/EDIT` |
| Mac: `nguồn '…' không có trong source gốc` dù tên đúng | tên file tiếng Việt khác dạng Unicode — đã tự chuẩn hoá NFC; còn lỗi thì gõ lại tên trong edl/brief |
| Tiếng và hình lệch | Xoá `work/<nguồn>/normalized.mp4` rồi chạy lại `vf analyze` |
| Chữ không động | Chưa `npm install` trong `remotion/`; hoặc `--static-text` để chủ ý dùng chữ tĩnh |
| Render chậm trên Mac | `vf doctor` phải báo VideoToolbox; `VF_ENCODER=cpu` chỉ để thử lỗi |
| Phiên âm chậm trên Mac | `vf doctor` phải báo mlx-whisper; muốn nhanh hơn nữa: `VF_WHISPER_MODEL=large-v3-turbo` |
| `cublas64_12.dll is not found` (Windows) | `.venv\Scripts\python -m pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12==9.*"` |
| Video "vấp", vài khung cảnh khác lóe lên | Mép đoạn sát điểm chuyển cảnh; chỉnh theo `scenes.json` hoặc `video_end` |
| Chữ lỗi dấu tiếng Việt | Thiếu font: `library/brand/fonts/BeVietnamPro-*.ttf` |
| `vùng an toàn: chữ/hình lấn vùng …` | Rút chữ, bỏ `y` ghi tay, dời graphic, hoặc thẻ `free` (chỉ né mặt) |
| `ClaimViolation` | Chỉ chặn cụm do brief của lô ghi trong `forbidden` — sửa chữ hoặc bỏ cụm khỏi brief |
| Phiên âm rỗng | Lần trước chạy `--no-transcribe`; chạy lại `vf analyze lo-NN` |
