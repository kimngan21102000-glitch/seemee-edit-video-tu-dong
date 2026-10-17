# Tự kiểm tra trên MacBook (Apple Silicon)

Bản này đã kiểm trên Windows (pytest, render thử Smilee bằng hồ sơ mới, cài plugin). Riêng **VideoToolbox** và
**mlx-whisper** chỉ chạy được trên Mac — làm lần lượt các bước sau ở máy Mac, mỗi bước có "đạt khi".

## 1. Cài đặt
```bash
cd ~/edit-video-tu-dong && bash scripts/setup-mac.sh
```
Đạt khi: script chạy hết 6 bước, dòng 2 in `ffmpeg có h264_videotoolbox`, bước 6 tải xong model
`mlx-community/whisper-large-v3-mlx`.

## 2. vf doctor
```bash
.venv/bin/vf doctor
```
Đạt khi có các dòng:
- `Máy: Darwin arm64`
- `OK        VideoToolbox (chip Apple) — mã hoá video nhanh`
- `OK        phiên âm: mlx-whisper (chip Apple)` và `model phiên âm … đã tải`
- `OK        Remotion đã cài — chữ động`
- `OK        …/source gốc: N video` (Drive đọc được)
- `OK        hồ sơ sản phẩm: balo, smilee …`

Không đạt → xem cột "Lỗi thường gặp" trong `skills/edit-video-tu-dong/SKILL.md`.

## 3. Test tự động
```bash
.venv/bin/python -m pytest -q
```
Đạt khi: tất cả qua (≈ 150 test, 5–10 phút). Thêm test phiên âm thật bằng mlx (lâu, lần đầu tải model):
```bash
.venv/bin/python -m pytest -q -m slow
```

## 4. Thử nhanh hai bộ tăng tốc
```bash
ffmpeg -v error -f lavfi -i testsrc2=s=1080x1920:d=3 -c:v h264_videotoolbox -q:v 65 -y /tmp/vt.mp4 && echo VT-OK
```
```bash
.venv/bin/python -c "from vf.transcribe import backend; print(backend())"
```
Đạt khi: in `VT-OK` và `mlx`.

## 5. Render thử 1 bản Smilee
Chép lô mẫu và chạy (cần `dqamii.mp4` trong `EDIT/source gốc/`):
```bash
mkdir -p jobs/smilee-lo-08 && cp examples/smilee-lo-08/* jobs/smilee-lo-08/
```
```bash
.venv/bin/vf analyze smilee-lo-08
```
```bash
.venv/bin/vf render smilee-lo-08 --only lo-08_routine_gel-nhanh
```
Đạt khi:
- `analyze` in `Phiên âm bằng mlx-whisper (Apple Silicon)`, xong trong vài phút (nhanh hơn nhiều so với CPU).
- `render` in `OK lo-08_routine_gel-nhanh (…)`, không có dòng `vùng an toàn: …`; file
  `EDIT/out/smilee-lo-08/lo-08_routine_gel-nhanh.mp4` ~80 s, mở xem: chữ/thẻ đúng màu tím mận/hồng, tiếng không bị
  cắt lấn chữ, thẻ đèn "kính tối".
- Mở `…_sheet.png` cạnh bản Windows (`EDIT/out/lo-08/`): bố cục giống nhau.
- Lưu ý: phiên âm mlx có thể lệch vài chục ms so với faster-whisper → các mốc trong `edl.json` mẫu (tính từ phiên âm
  Windows) vẫn dùng được; lô mới thì edl viết theo phiên âm của chính máy Mac.

Dọn sau khi thử: xoá `jobs/smilee-lo-08` và `EDIT/out/smilee-lo-08` (không xoá gì trong `source gốc`).

## 6. Plugin
Trong Claude Code (mở ở `~/edit-video-tu-dong`):
```
/plugin marketplace add OWNER/edit-video-tu-dong
/plugin install edit-video-tu-dong@edit-video-tu-dong
```
Đạt khi: gõ `/edit-video-tu-dong` thấy skill; hỏi "edit lô mới cho balo" → Claude chạy `vf doctor`, `vf profiles`, hỏi brief.

## 7. Báo lại
Gửi Claude: kết quả `vf doctor`, số test qua/hỏng, thời gian `analyze` + `render` một bản. Bước nào hỏng, dán nguyên
thông báo lỗi.
