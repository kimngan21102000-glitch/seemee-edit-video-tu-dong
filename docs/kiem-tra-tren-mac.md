# Tự kiểm tra trên MacBook (Apple Silicon)

Bản này đã kiểm trên Windows (pytest, render thử bằng hồ sơ, cài plugin). Riêng **VideoToolbox** và
**mlx-whisper** chỉ chạy được trên Mac — làm lần lượt các bước sau ở máy Mac, mỗi bước có "đạt khi".

## 1. Cài đặt
```bash
cd ~/seemee-edit-video-tu-dong && bash scripts/setup-mac.sh
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
- `OK        hồ sơ sản phẩm: seemee …`

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

## 5. Render thử SeeMee
Render thử đồ hoạ SeeMee (preset `brand`, thẻ tím dâu) + một lô mẫu tổng hợp qua `vf analyze`/`vf render` bằng VideoToolbox:
```bash
.venv/bin/python -m pytest -q tests/test_profile.py::test_seemee_graphics_render tests/test_cli.py::test_analyze_then_render
```
Phân tích thử một source SeeMee thật (cần ít nhất 1 video trong `EDIT/source gốc/`):
```bash
.venv/bin/vf new auto --profile seemee
```
```bash
.venv/bin/vf analyze lo-01
```
(thay `lo-01` bằng tên lô mà lệnh `vf new auto` in ra.)
Đạt khi:
- pytest báo `2 passed`.
- `analyze` in `Phiên âm bằng mlx-whisper (Apple Silicon)`, xong trong vài phút (nhanh hơn nhiều so với CPU);
  có `work/<nguồn>/transcript.json` và các trang `*_sheet_NNN.png`.
- Phiên âm mlx có thể lệch vài chục ms so với faster-whisper → edl của lô viết theo phiên âm của chính máy Mac.

Dọn sau khi thử: xoá `jobs/<lô thử>` nếu không dùng tiếp (không xoá gì trong `source gốc`).

## 6. Plugin
Trong Claude Code (mở ở `~/seemee-edit-video-tu-dong`):
```
/plugin marketplace add kimngan21102000-glitch/seemee-edit-video-tu-dong
/plugin install edit-video-tu-dong@seemee-edit-video-tu-dong
```
Đạt khi: gõ `/edit-video-tu-dong` thấy skill; hỏi "edit lô mới cho SeeMee" → Claude chạy `vf doctor`, `vf profiles`, hỏi brief.

## 7. Báo lại
Gửi Claude: kết quả `vf doctor`, số test qua/hỏng, thời gian `analyze` + `render` một bản. Bước nào hỏng, dán nguyên
thông báo lỗi.
