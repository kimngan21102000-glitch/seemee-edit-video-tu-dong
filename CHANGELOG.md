# Lịch sử

## 1.1.0 — 2026-10-29 (SeeMee)
- Sao chép nguyên lịch sử từ `mnsd123/edit-video-tu-dong` thành repo riêng cho SeeMee
  (`kimngan21102000-glitch/seemee-edit-video-tu-dong`).
- Hồ sơ mới **`profiles/seemee/`** (máy uốn tóc xoăn lơi PREMIUM 2026) từ listing TikTok Shop 1730842847185046483
  (2026-10-29): `product.md`, `commitments.txt`, `style-guide.md`, `tokens.json` (`brand_label` "SEEMEE", màu tím dâu/hồng,
  preset brand · vox · proof · ugc · reply), `forbidden.txt`, `claims_pending.txt`. Chỉ gói đồ hoạ **chung** — không bật
  `nha_khoa`. `learnings.md`/`hooks.md` bắt đầu trống; `library/` (luật dựng chung, bài học chung) giữ nguyên.
- Xoá `profiles/smilee`, `profiles/balo`, `examples/smilee-lo-08`.
- Tests chuyển sang hồ sơ `seemee`; `templates/edl.example.json`, `templates/brief.yaml`, `vf.toml.example` theo SeeMee.
- README, `.claude-plugin/` (marketplace `seemee-edit-video-tu-dong`, plugin vẫn tên `edit-video-tu-dong`) theo SeeMee.
- `vf/`, `remotion/`, `scripts/`, `skills/`, `library/` không đổi.

## 1.0.0 — 2026-10-16
- Tách từ repo `game-dev` (skill `/smilee-video` v2.6, commit 4628ead) thành skill chung `/edit-video-tu-dong`.
- **Hồ sơ sản phẩm** `profiles/<slug>/` (smilee, balo khung, _mau); brief có `profile:`; `vf new --profile`, `vf profiles`,
  `vf --profile`; tokens = `library/tokens.base.json` (chung) gộp sâu `profiles/<slug>/tokens.json` (riêng).
- Preset theo hồ sơ (không cố định 8 tên); **gói đồ hoạ** chung / nha_khoa / balo, render báo lỗi khi dùng gói chưa bật;
  `graphic_defaults` của hồ sơ (tên cột so sánh…); `gel_refill` → `refill` (tên cũ vẫn đọc được).
- Gói **balo** khung: `size_fit`, `compartments`, `badge` (remotion/src/BaloGraphics.tsx).
- **Mac Apple Silicon**: mã hoá `h264_videotoolbox`, phiên âm `mlx-whisper` (lùi faster-whisper CPU int8),
  `scripts/setup-mac.sh`, `vf doctor` theo nền tảng, chuẩn hoá tên file tiếng Việt NFC (Drive trên Mac).
- Plugin Claude Code (`.claude-plugin/`): skills `edit-video-tu-dong`, `video-learnings`, `video-style-learning`.
- Style guide/learnings tách: chung ở `library/`, riêng Smilee ở `profiles/smilee/` (lịch sử Smilee:
  `profiles/smilee/CHANGELOG-smilee-video.md`).
