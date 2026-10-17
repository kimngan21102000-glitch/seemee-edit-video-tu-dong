# edit-video-tu-dong — Edit video quảng cáo TikTok tự động

Dựng hàng loạt video quảng cáo 9:16 từ video gốc (source KOL) cho **nhiều sản phẩm**: phân tích nguồn, phiên âm từng
chữ, viết kịch bản dựng (edl) nhiều biến thể, render bằng ffmpeg + Remotion (chữ/đồ hoạ động), QA vùng an toàn TikTok,
học từ điểm chấm. Claude Code điều khiển qua skill **`/edit-video-tu-dong`**.

Tách từ pipeline Smilee (repo `game-dev`, skill `/smilee-video` v2.6, 8 lô feedback) thành bản dùng chung:
mỗi sản phẩm là một **hồ sơ** trong `profiles/`.

| Nền tảng | Mã hoá video | Phiên âm |
|---|---|---|
| **MacBook Apple Silicon** (chip M) | `h264_videotoolbox` | `mlx-whisper` (lùi `faster-whisper` CPU int8) |
| Windows có GPU NVIDIA | `h264_nvenc` | `faster-whisper` CUDA |
| Máy khác | `libx264` (CPU) | `faster-whisper` CPU |

Tự chọn — `vf doctor` báo đang dùng gì. Ép tay: `VF_ENCODER=cpu|nvenc|videotoolbox`, `VF_TRANSCRIBER=mlx|faster`,
`VF_WHISPER_MODEL=large-v3|large-v3-turbo|medium`.

## Cấu trúc

```
vf/                 engine Python (lệnh `vf`)
remotion/           đồ hoạ động (Remotion) — src/Graphics.tsx (chung + nha khoa), src/BaloGraphics.tsx (balo)
library/            CHUNG mọi sản phẩm: style-guide.md, learnings.md, tokens.base.json, brand/ (font, SFX)
profiles/<slug>/    RIÊNG từng sản phẩm: product.md, tokens.json (màu, preset, gói đồ hoạ), commitments.txt,
                    forbidden.txt, hooks.md, learnings.md, learnings-stats.md, style-guide.md, research/
  smilee/           kit trắng răng (chuyển nguyên từ game-dev, gói đồ hoạ nha_khoa)
  balo/             balo thời trang — KHUNG, điền dần khi có source đầu tiên (gói đồ hoạ balo)
  _mau/             mẫu trống để thêm sản phẩm mới
skills/             skill Claude Code: edit-video-tu-dong, video-learnings, video-style-learning
.claude-plugin/     plugin.json + marketplace.json (cài bằng /plugin)
examples/           lô mẫu (smilee-lo-08: script sinh edl có luật cắt tiếng không lấn voice)
jobs/<lô>/          brief.yaml + edl.json của từng lô (không đẩy lên GitHub)
work/               file tạm: video chuẩn hoá, phiên âm (không đẩy lên GitHub)
scripts/            setup-mac.sh, setup-windows.ps1, face_cover_check.py
docs/               kiem-tra-tren-mac.md
```

Video nguồn/kết quả nằm trong Google Drive: `<EDIT>/source gốc/` (nguồn — **không bao giờ sửa/xoá/di chuyển**),
`<EDIT>/video tham khảo/`, `<EDIT>/out/<lô>/` (kết quả).

## Cài trên MacBook (Apple Silicon)

Cần: Google Drive for desktop (bật *Available offline* cho thư mục `EDIT`), Claude Code, tài khoản GitHub có quyền
đọc repo private này.

1. **Đăng nhập GitHub** (một lần — repo private):
   ```bash
   brew install gh
   ```
   ```bash
   gh auth login
   ```
   (chọn GitHub.com → HTTPS → Login with a web browser; `gh auth setup-git` để git dùng luôn tài khoản này.)
2. **Lấy code** vào thư mục làm việc:
   ```bash
   gh repo clone mnsd123/edit-video-tu-dong ~/edit-video-tu-dong
   ```
3. **Cài môi trường** (Homebrew, ffmpeg, Python 3.11, Node, .venv, Remotion, model phiên âm ~3 GB, vf.toml):
   ```bash
   cd ~/edit-video-tu-dong && bash scripts/setup-mac.sh
   ```
   Script tự tìm `~/Library/CloudStorage/GoogleDrive-<email>/My Drive/EDIT`; không thấy thì hỏi (kéo thư mục EDIT vào
   cửa sổ Terminal). Cuối script chạy `vf doctor`.
4. **Cài plugin Claude Code** (gõ trong Claude Code):
   ```
   /plugin marketplace add mnsd123/edit-video-tu-dong
   /plugin install edit-video-tu-dong@edit-video-tu-dong
   ```
5. Mở Claude Code **ở thư mục repo** (`cd ~/edit-video-tu-dong && claude`) rồi gõ `/edit-video-tu-dong`.

Cập nhật: `git pull` trong `~/edit-video-tu-dong` (code + hồ sơ) và `/plugin marketplace update edit-video-tu-dong`
(skill). Các bước tự kiểm trên Mac: [docs/kiem-tra-tren-mac.md](docs/kiem-tra-tren-mac.md).

## Cài trên Windows

```powershell
git clone https://github.com/mnsd123/edit-video-tu-dong C:\dev\edit-video-tu-dong
cd C:\dev\edit-video-tu-dong
powershell -ExecutionPolicy Bypass -File scripts\setup-windows.ps1
```
Plugin: như bước 4 ở trên. Repo nên ở đường dẫn ngắn (lỗi `WinError 206` khi `pip install`).

## Thêm sản phẩm mới

```bash
cp -r profiles/_mau profiles/<slug>        # slug viết thường không dấu, vd son-moi
```
Điền `product.md`, `commitments.txt`, `style-guide.md`, `tokens.json` (tên, `brand_label`, màu, preset,
`graphics_packs`: `nha_khoa`, `balo`, …). Chi tiết: [profiles/_mau/README.md](profiles/_mau/README.md).
Kiểm tra `vf profiles`, rồi lô đầu tiên `vf new auto --profile <slug>`. Hoặc nói với Claude: "thêm sản phẩm mới …".

Gói đồ hoạ (`vf/tokens.py` → `GRAPHIC_PACKS`): **chung** (luôn bật: steps, versus, cost_compare, counter, live_cta,
end_card, wipe, collage, callout, kinetic, nope, refill), **nha_khoa** (teeth, whiten, shade, light_timer, bám răng),
**balo** (size_fit, compartments, badge). Ngành mới cần đồ hoạ riêng → thêm component Remotion + một gói mới.

## Quy trình một lô

Trong Claude Code: `/edit-video-tu-dong` (hoặc "có source mới", "edit lô mới cho balo"). Claude làm:

| Bước | Lệnh | Ghi chú |
|---|---|---|
| 0. Kiểm máy | `vf doctor` | |
| 1. Chọn hồ sơ, xem nguồn mới | `vf profiles`, `vf status` | hỏi "lô này cho sản phẩm nào?" nếu chưa rõ |
| 2. Tạo lô, hỏi brief | `vf new auto --profile <slug>` | brief có `profile:`; 4 biến thể mặc định |
| 3. Phân tích | `vf analyze <lô>`, `vf sheet work/<nguồn>/normalized.mp4` | chữ in sẵn, cảnh tiền, mặt KOL, nhạc nền |
| 4. Kịch bản | viết `jobs/<lô>/edl.json` | theo style guide chung + của hồ sơ |
| 5. Render | `vf snap <lô>` (chỉ nguồn sạch), `vf render <lô>` | QA, sheet, `face_cover_check.py`, phiên âm lại output |
| 6. Báo + học | `review.csv` → "Chạy video-learnings" | bài học vào hồ sơ hoặc `library/` |

Lệnh `vf` (Mac: `.venv/bin/vf`, Windows: `.venv\Scripts\vf.exe`): `doctor`, `profiles`, `status`, `new`, `analyze`,
`sheet`, `snap`, `render`, `expand`, `learn`, `style`, `make-sfx`. Chọn hồ sơ cho lệnh không có lô:
`vf --profile balo learn`.

## Kiểm thử

```bash
.venv/bin/python -m pytest -q
```
(`-m slow` chạy thêm test phiên âm thật.) Test chọn bộ mã hoá/phiên âm theo nền tảng chạy được trên mọi máy (giả lập).
