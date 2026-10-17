"""Đường dẫn mặc định, tính từ gốc dự án (chạy lệnh ở thư mục nào cũng được).
Phần riêng từng sản phẩm (tokens, cam kết, hồ sơ…) đọc qua vf/profile.py."""
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "library"
PROFILES_DIR = ROOT / "profiles"
TEMPLATES = ROOT / "templates"
BRAND_DIR = LIBRARY / "brand"  # font, SFX dùng chung; hồ sơ có thể có brand/ riêng (Profile.brand_dirs)
BASE_TOKENS_PATH = LIBRARY / "tokens.base.json"
STYLE_GUIDE = LIBRARY / "style-guide.md"
CAPTION_STYLE = TEMPLATES / "caption_style.ass"
BRIEF_TEMPLATE = TEMPLATES / "brief.yaml"


def nfc(name: str) -> str:
    """Tên file tiếng Việt về dạng NFC. macOS / Google Drive for Mac có thể trả tên dạng NFD ("gốc" = "go" + dấu rời),
    nhìn giống hệt nhưng khác chuỗi so với tên gõ trong edl/brief → mọi khoá tên nguồn đều chuẩn hoá NFC."""
    return unicodedata.normalize("NFC", name)


def child(parent: Path, name: str) -> Path:
    """parent/name; nếu không có thì tìm thư mục con trùng tên sau khi chuẩn hoá NFC (Drive trên Mac)."""
    p = Path(parent) / name
    if p.exists() or not Path(parent).is_dir():
        return p
    for c in Path(parent).iterdir():
        if nfc(c.name) == nfc(name):
            return c
    return p
