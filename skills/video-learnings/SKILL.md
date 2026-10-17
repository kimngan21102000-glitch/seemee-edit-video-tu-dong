---
name: video-learnings
description: Dùng khi người dùng nói "Chạy video-learnings", gửi feedback về video đã dựng, hoặc đã chấm điểm / nhập số liệu TikTok vào review.csv của một hay nhiều lô — tổng hợp theo preset, kiểu hook, độ dài cho từng hồ sơ sản phẩm, cập nhật learnings-stats.md, hooks.md, learnings.md (của hồ sơ và chung) để lô sau dựng tốt hơn.
---

# Học từ điểm chấm và feedback

Chạy ở gốc repo `edit-video-tu-dong` (`vf` = `.venv/bin/vf` trên Mac, `.venv\Scripts\vf.exe` trên Windows).
Mỗi hồ sơ sản phẩm học riêng: lô thuộc hồ sơ nào xem `profile:` trong `jobs/<lô>/brief.yaml` (lô không ghi = hồ sơ mặc định).

## Bước 1. Lấy số liệu (từng hồ sơ có lô đã chấm)

```
vf --profile <slug> learn --write
```
Đọc mọi `<drive_root>/out/*/review.csv` của hồ sơ đó, in bảng theo kiểu hook và ghi `profiles/<slug>/learnings-stats.md`: điểm TB, giữ chân 3 s, số liệu TikTok (`view_2s`, `view_6s`, `avg_watch_s`, `ctr`, `cvr`, `cost_per_order`) theo **kiểu hook, preset, preset × kiểu hook, nhóm độ dài** (≤45 s, 46–75 s, >75 s) + top 3 biến thể. Dòng chưa có `score` bị bỏ qua.

Sau đó đọc trực tiếp từng `review.csv` (cột `notes`, `hook_text`, `preset`, `length_s`) và `jobs/<lô>/edl.json` để biết biến thể được dựng thế nào.

## Bước 2. Cập nhật `profiles/<slug>/hooks.md`

- Thay bảng xếp hạng bằng bảng `vf learn` vừa in, thêm cột "Ví dụ thắng": `hook_text` của biến thể điểm cao nhất mỗi kiểu (kèm `lô/id`). Ghi ngày cập nhật.
- Dưới 3 lần chấm cho một kiểu hook thì ghi "chưa đủ dữ liệu", không kết luận.

## Bước 3. Ghi bài học — đúng chỗ

- **Riêng sản phẩm** (nội dung, hook, preset, đồ hoạ ngành, khách hàng) → `profiles/<slug>/learnings.md`.
- **Cách dựng chung** (cắt tiếng, nhịp, chữ, vùng an toàn, né mặt, âm thanh, quy trình) → `library/learnings.md`, ghi bằng chứng kèm `<slug>/<lô>`.
- Mỗi bài học một dòng: `YYYY-MM-DD — bài học — bằng chứng (lô/id, điểm, notes hoặc retention)`.
- Chỉ ghi điều có bằng chứng trong review.csv / feedback. Không suy diễn từ một biến thể đơn lẻ trừ khi notes của người dùng nói thẳng.
- Retention 3 s (khi có) quan trọng hơn điểm cảm tính khi mâu thuẫn; ghi rõ. Mốc tham khảo: retention 3 s ≥ 55 % là hook mạnh, < 40 % phải làm lại hook — ưu tiên so các biến thể trong cùng tài khoản.
- Preset/kiểu hook thắng rõ (≥ 3 lần chấm) → đề xuất dùng nhiều hơn; thua rõ → ghi điều cần sửa trong preset đó. Sửa style guide (`library/style-guide.md` hoặc `profiles/<slug>/style-guide.md`) → **hỏi người dùng trước**.
- **Không xoá bài học cũ**, trừ khi dữ liệu mới bác bỏ: gạch `~~…~~` và thêm dòng mới nêu bằng chứng.

## Bước 4. Báo người dùng

Tóm tắt 3–5 dòng mỗi hồ sơ: preset và kiểu hook đang thắng, độ dài hiệu quả, điều sẽ làm khác ở lô sau, chỗ còn thiếu dữ liệu (chưa nhập số liệu TikTok, notes chung thay vì riêng từng biến thể).
