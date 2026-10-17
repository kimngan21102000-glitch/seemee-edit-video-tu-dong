---
name: video-style-learning
description: Dùng khi cần học phong cách dựng từ các video trong thư mục "video tham khảo" (hoặc video mẫu người dùng bổ sung) và viết/cập nhật style guide — chung (library/style-guide.md) hoặc của một hồ sơ sản phẩm (profiles/<slug>/style-guide.md, research/): nhịp cắt, hook, chuyển cảnh, kiểu chữ, hiệu ứng, nhạc/SFX, màu.
---

# Học phong cách từ video tham khảo

Chạy ở gốc repo `edit-video-tu-dong`. Video tham khảo chỉ để học **kỹ thuật** (nhịp, chuyển cảnh, kiểu chữ, bố cục motion).
Không sao chép, không trích hình, nhạc, giọng hay câu chữ nguyên văn. **Không sửa, xoá, di chuyển** file trong `video tham khảo`.

Hỏi trước (câu có lựa chọn) nếu chưa rõ: video tham khảo này để học cho **(1) mọi sản phẩm** (→ `library/style-guide.md`) hay **(2) một hồ sơ** (→ `profiles/<slug>/style-guide.md` + `profiles/<slug>/research/YYYY-MM-DD.md`)?

## Bước 1. Đo

```
vf style
```
Ghi `work/style/<tên>/stats.json` (thời lượng, số lần cắt, giây/cảnh, thời điểm cắt), `frames/` (1 khung/giây), `transcript.json`.
Số lần cắt có vẻ thấp so với khung hình → `vf style --threshold 0.2`; ghi rõ ngưỡng đã dùng.

## Bước 2. Xem từng video

Với MỖI video, đọc `stats.json`, xem (Read) các ảnh trong `frames/` (kỹ 3 giây đầu) và `transcript.json`. Ghi chú:
- Hook giây 0–3: mở bằng gì, chữ hook ở đâu, bao nhiêu chữ, cắt cảnh đầu lúc mấy giây.
- Nhịp: giây/cảnh trung bình, đoạn nhanh/chậm, jump cut trong cùng cảnh nói.
- Chuyển cảnh (so với luật chung: cắt thẳng mọi preset — chỉ đề xuất đổi khi có lý do mạnh).
- Chữ: vị trí, font, màu chữ/viền/nền, số từ mỗi dòng, chữ hiện từng từ không; có né mặt không.
- Motion graphic/thẻ minh hoạ: loại gì, đặt ở đâu so với mặt KOL, xuất hiện đúng lúc nói không — ghi thành ý đồ hoạ có thể làm (map sang `graphics.kind` có sẵn hoặc đề xuất component mới).
- Nhạc/SFX (chỉ mô tả kiểu), bảng màu, khung quay, CTA (giây thứ mấy, nói gì, có chữ không).

## Bước 3. Viết kết quả

- Học cho một hồ sơ: ghi `profiles/<slug>/research/YYYY-MM-DD.md` (danh sách video, ngưỡng, các ý trên, 3–5 ý nên thử ở lô sau), rồi đề xuất phần cần thêm vào `profiles/<slug>/style-guide.md`.
- Học chung: đề xuất sửa `library/style-guide.md` theo các mục hiện có (nhịp, cấu trúc, typography, vùng an toàn, thẻ đồ hoạ, âm thanh, nên/không nên).
- Viết tiếng Việt, cụ thể thành số ("cắt cảnh mỗi 1,2–1,8 s", "chữ hook 5–7 từ, 1/3 trên").
- Mục **Không bắt chước**: hình, nhạc, giọng, câu nói của video gốc; claim mà hồ sơ cấm (`profiles/<slug>/forbidden.txt`).

## Bước 4. Dừng chờ duyệt

Báo người dùng tóm tắt 5–8 dòng; **chỉ sửa style guide khi người dùng đồng ý**. File research thì ghi luôn được.
