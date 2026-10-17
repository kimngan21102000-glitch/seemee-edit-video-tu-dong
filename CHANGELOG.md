# Lịch sử

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
