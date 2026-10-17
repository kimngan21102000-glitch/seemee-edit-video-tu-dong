"""Hồ sơ sản phẩm: profiles/<slug>/ — mọi thứ riêng của một sản phẩm (hồ sơ, màu/preset, cam kết, hook, bài học,
gói đồ hoạ theo ngành). Phần dùng chung cho mọi sản phẩm nằm ở library/ (style guide chung, tokens.base.json, font, SFX).

Chọn hồ sơ (ưu tiên từ trên xuống):
1. `profile:` trong jobs/<lô>/brief.yaml (lệnh có tên lô tự đọc)
2. `vf --profile <slug> …` hoặc biến môi trường VF_PROFILE
3. `default_profile` trong vf.toml
4. chỉ có đúng một hồ sơ (không tính `_mau`) → dùng hồ sơ đó
"""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from vf.paths import LIBRARY, PROFILES_DIR

TEMPLATE_SLUG = "_mau"


@dataclass(frozen=True)
class Profile:
    slug: str
    dir: Path

    def _f(self, name: str) -> Path:
        return self.dir / name

    @property
    def name(self) -> str:
        """Tên hiển thị (dòng `name` trong tokens.json của hồ sơ, không có thì slug)."""
        import json

        try:
            return json.loads(self.tokens.read_text(encoding="utf-8")).get("name") or self.slug
        except (OSError, ValueError):
            return self.slug

    product = property(lambda self: self._f("product.md"))
    tokens = property(lambda self: self._f("tokens.json"))
    commitments = property(lambda self: self._f("commitments.txt"))
    forbidden = property(lambda self: self._f("forbidden.txt"))
    pending = property(lambda self: self._f("claims_pending.txt"))
    hooks = property(lambda self: self._f("hooks.md"))
    learnings = property(lambda self: self._f("learnings.md"))
    learnings_stats = property(lambda self: self._f("learnings-stats.md"))
    style_guide = property(lambda self: self._f("style-guide.md"))
    research = property(lambda self: self._f("research"))

    @property
    def brand_dirs(self) -> list[Path]:
        """Nơi tìm font/SFX/nhạc: profiles/<slug>/brand/ (nếu có) trước, rồi library/brand/ chung."""
        own = self._f("brand")
        return ([own] if own.is_dir() else []) + [LIBRARY / "brand"]


def list_profiles(include_template: bool = False) -> list[str]:
    if not PROFILES_DIR.is_dir():
        return []
    return sorted(p.name for p in PROFILES_DIR.iterdir()
                  if p.is_dir() and (p / "tokens.json").exists() and (include_template or p.name != TEMPLATE_SLUG))


def get_profile(slug: str) -> Profile:
    d = PROFILES_DIR / slug
    if not (d / "tokens.json").exists():
        have = ", ".join(list_profiles()) or "chưa có"
        raise ValueError(f"Không có hồ sơ '{slug}' (cần profiles/{slug}/tokens.json). Hồ sơ hiện có: {have}. "
                         f"Thêm sản phẩm mới: chép profiles/{TEMPLATE_SLUG} thành profiles/<slug>.")
    return Profile(slug, d)


_current: str | None = None


def set_profile(slug: str | None) -> None:
    """Đặt hồ sơ đang dùng (None = quay về cách tự chọn). Xoá cache tokens."""
    global _current
    if slug is not None:
        get_profile(slug)  # kiểm tra tồn tại
    _current = slug
    from vf.tokens import load_tokens

    load_tokens.cache_clear()


def _toml_default(config: Path = Path("vf.toml")) -> str | None:
    try:
        with open(config, "rb") as f:
            return tomllib.load(f).get("default_profile")
    except (OSError, tomllib.TOMLDecodeError):
        return None


def current_slug() -> str:
    slug = _current or os.environ.get("VF_PROFILE") or _toml_default()
    if slug:
        return slug
    have = list_profiles()
    if len(have) == 1:
        return have[0]
    raise ValueError("Chưa chọn hồ sơ sản phẩm: ghi `profile: <slug>` trong brief.yaml của lô, hoặc "
                     "`default_profile = \"<slug>\"` trong vf.toml, hoặc `vf --profile <slug> …`. "
                     f"Hồ sơ hiện có: {', '.join(have) or 'chưa có'}")


def current() -> Profile:
    return get_profile(current_slug())


def use_brief_profile(brief_path: Path) -> str | None:
    """Đọc `profile:` trong brief của lô (nếu có) và đặt làm hồ sơ đang dùng. Trả slug."""
    import yaml

    p = Path(brief_path)
    if not p.exists():
        return None
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return None
    slug = data.get("profile")
    if slug:
        set_profile(slug)
    return slug
