# Mẫu hồ sơ sản phẩm

Thêm sản phẩm mới:

1. Chép cả thư mục: `cp -r profiles/_mau profiles/<slug>` (slug viết thường không dấu, vd `balo`, `son-moi`).
2. Điền `product.md` (hồ sơ sản phẩm — nguyên liệu cho hook, chữ, CTA), `commitments.txt` (cam kết tự highlight),
   `hooks.md` (ý hook ban đầu), `style-guide.md` (luật riêng: cảnh tiền của ngành, đồ hoạ nên dùng, điều cấm).
3. `tokens.json`: tên, `brand_label`, màu, preset (giữ ít nhất `brand`, `vox`, `ugc`), `graphics_packs` theo ngành
   (`nha_khoa`, `balo`… — xem `vf/tokens.py`). Chỉ ghi phần khác `library/tokens.base.json`.
4. Font/SFX/nhạc riêng (tuỳ chọn): `profiles/<slug>/brand/` (fonts/, sfx/) — không có thì dùng `library/brand/`.
5. Kiểm tra: `vf profiles` thấy hồ sơ mới; lô mới: `vf new auto --profile <slug>`.

`learnings.md`, `learnings-stats.md`, `research/` do skill `video-learnings` / nghiên cứu điền dần.
