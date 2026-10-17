#!/usr/bin/env bash
# Cài edit-video-tu-dong trên MacBook Apple Silicon (chạy 1 lần, chạy lại cũng được).
# Cách chạy, tại thư mục repo:
#   bash scripts/setup-mac.sh
# Tuỳ chọn:
#   DRIVE_ROOT="$HOME/Library/CloudStorage/GoogleDrive-ban@gmail.com/My Drive/EDIT" bash scripts/setup-mac.sh
#   VF_WHISPER_MODEL=large-v3-turbo bash scripts/setup-mac.sh   (model phiên âm nhỏ/nhanh hơn; mặc định large-v3)
set -euo pipefail
cd "$(dirname "$0")/.."

step() { printf '\n\033[36m==> %s\033[0m\n' "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Script này cho macOS. Windows: powershell -ExecutionPolicy Bypass -File scripts\\setup-windows.ps1"; exit 1
fi
if [[ "$(uname -m)" != "arm64" ]]; then
  echo "CẢNH BÁO: máy không phải Apple Silicon (chip M) — vẫn cài được nhưng phiên âm/mã hoá chạy CPU, chậm."
fi

step "1/6 Homebrew"
if ! have brew; then
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [[ -x $b ]] && eval "$($b shellenv)"; done
fi
if ! have brew; then
  echo "   Cài Homebrew (sẽ hỏi mật khẩu máy Mac)…"
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
  # để mở Terminal lần sau vẫn có brew
  grep -q 'brew shellenv' "$HOME/.zprofile" 2>/dev/null || echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> "$HOME/.zprofile"
fi
echo "   $(brew --version | head -1)"

step "2/6 ffmpeg, Python 3.11, Node"
for f in ffmpeg python@3.11 node; do
  if brew list --formula "$f" >/dev/null 2>&1; then echo "   có sẵn: $f"; else echo "   cài: $f"; brew install "$f"; fi
done
PY="$(brew --prefix python@3.11)/bin/python3.11"
if ffmpeg -hide_banner -encoders 2>/dev/null | grep -q h264_videotoolbox; then
  echo "   ffmpeg có h264_videotoolbox (mã hoá bằng chip Apple)"
else
  echo "   CẢNH BÁO: ffmpeg thiếu h264_videotoolbox — sẽ mã hoá bằng CPU"
fi

step "3/6 Môi trường Python (.venv) + thư viện (mlx-whisper, faster-whisper, OpenCV…)"
[[ -x .venv/bin/python ]] || "$PY" -m venv .venv
.venv/bin/python -m pip install --upgrade pip -q
.venv/bin/python -m pip install -e ".[dev]" -q

step "4/6 Remotion (chữ / đồ hoạ động)"
(cd remotion && npm ci --no-audit --no-fund || npm install --no-audit --no-fund)

step "5/6 Tìm thư mục EDIT trong Google Drive → vf.toml"
if [[ -f vf.toml ]]; then
  echo "   đã có vf.toml (giữ nguyên): $(grep drive_root vf.toml)"
else
  ROOT="${DRIVE_ROOT:-}"
  if [[ -z "$ROOT" ]]; then
    shopt -s nullglob
    for d in "$HOME"/Library/CloudStorage/GoogleDrive-*/*/EDIT "$HOME"/Library/CloudStorage/GoogleDrive-*/*/*/EDIT; do
      # "source gốc" có thể nằm dạng NFC hoặc NFD — so bằng ls + python
      if .venv/bin/python - "$d" <<'PY'
import sys, unicodedata
from pathlib import Path
d = Path(sys.argv[1])
sys.exit(0 if any(unicodedata.normalize("NFC", c.name) == "source gốc" for c in d.iterdir()) else 1)
PY
      then ROOT="$d"; break; fi
    done
  fi
  if [[ -z "$ROOT" ]]; then
    echo "   Không tự tìm thấy. Mở Google Drive for desktop, bật 'Available offline' cho thư mục EDIT."
    read -r -p "   Dán đường dẫn thư mục EDIT (kéo thư mục vào cửa sổ Terminal): " ROOT
    # kéo thư mục vào Terminal cho ra "…/My\ Drive/EDIT " → bỏ "\" trước dấu cách, khoảng trắng cuối, "/" cuối
    bs="$(printf '\134')"  # dấu "\"
    ROOT="${ROOT%"${ROOT##*[![:space:]]}"}"; ROOT="${ROOT//"$bs "/ }"; ROOT="${ROOT%/}"
  fi
  printf 'drive_root = "%s"\n\n# hồ sơ mặc định khi brief không ghi profile (smilee | balo | …)\n# default_profile = "smilee"\n' "$ROOT" > vf.toml
  echo "   đã ghi vf.toml: drive_root = $ROOT"
fi

step "6/6 Tải model phiên âm (một lần, ~3 GB với large-v3)"
.venv/bin/python - <<'PY'
import os
from vf.transcribe import backend, mlx_repo, DEFAULT_MODEL
if backend() == "mlx":
    from huggingface_hub import snapshot_download
    repo = mlx_repo(DEFAULT_MODEL)
    print(f"   mlx-whisper: {repo}")
    snapshot_download(repo)
else:
    print(f"   faster-whisper: {DEFAULT_MODEL} (CPU int8)")
    from faster_whisper import WhisperModel
    WhisperModel(DEFAULT_MODEL, device="cpu", compute_type="int8")
print("   xong")
PY

echo
.venv/bin/vf doctor || true
cat <<'TXT'

Xong. Mỗi lần làm việc: mở Terminal ở thư mục repo, gõ `claude`, rồi `/edit-video-tu-dong`.
Lệnh vf: .venv/bin/vf (hoặc `source .venv/bin/activate` rồi gõ vf).
Kiểm tra từng bước: docs/kiem-tra-tren-mac.md
TXT
