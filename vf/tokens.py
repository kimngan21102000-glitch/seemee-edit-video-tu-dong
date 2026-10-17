"""Thông số thiết kế: library/tokens.base.json (chung: khung, vùng an toàn, cỡ chữ, thời gian, âm thanh, font)
gộp sâu với profiles/<slug>/tokens.json (riêng: màu, preset, gói đồ hoạ, SFX theo đồ hoạ ngành, mặc định đồ hoạ).
Python đọc ở đây; Remotion nhận qua props `tokens`."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from vf.paths import BASE_TOKENS_PATH, BRAND_DIR

# gói đồ hoạ → các `graphics.kind`; hồ sơ bật gói trong tokens.json → "graphics_packs" ("chung" luôn bật)
GRAPHIC_PACKS: dict[str, set[str]] = {
    "chung": {"counter", "callout", "collage", "wipe", "kinetic", "end_card", "paper_swipe", "steps",
              "live_cta", "nope", "cost_compare", "refill", "versus"},
    "nha_khoa": {"teeth", "whiten", "shade", "light", "light_timer"},  # + effects zoom_to track "teeth"
    "balo": {"size_fit", "compartments", "badge"},
}
GRAPHIC_ALIASES = {"gel_refill": "refill"}  # tên cũ (Smilee ≤ v2.6)


def _merge(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in b.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def _read(p: Path) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def base_tokens() -> dict:
    if not BASE_TOKENS_PATH.exists():
        raise FileNotFoundError(f"Thiếu {BASE_TOKENS_PATH}")
    return _read(BASE_TOKENS_PATH)


@lru_cache(maxsize=8)
def _load(slug: str | None, path: str | None) -> dict:
    if path is not None:
        return _merge(base_tokens(), _read(Path(path)))
    from vf.profile import get_profile

    return _merge(base_tokens(), _read(get_profile(slug).tokens))


def load_tokens(path: Path | None = None) -> dict:
    """Tokens đã gộp của hồ sơ đang dùng (hoặc của file `path` gộp lên phần chung)."""
    if path is not None:
        return _load(None, str(path))
    from vf.profile import current_slug

    return _load(current_slug(), None)


load_tokens.cache_clear = _load.cache_clear  # type: ignore[attr-defined]


def preset_names() -> list[str]:
    return [k for k in load_tokens()["presets"] if not k.startswith("_")]


def default_preset() -> str:
    names = preset_names()
    d = load_tokens().get("default_preset")
    return d if d in names else names[0]


def preset(name: str | None) -> dict:
    """Thông số preset (thiếu/không có → preset mặc định của hồ sơ)."""
    presets = {k: v for k, v in load_tokens()["presets"].items() if not k.startswith("_")}
    return presets.get(name or default_preset(), presets[default_preset()])


def enabled_kinds() -> set[str]:
    """Các `graphics.kind` hồ sơ được dùng."""
    packs = {"chung", *load_tokens().get("graphics_packs", [])}
    return set().union(*(GRAPHIC_PACKS.get(p, set()) for p in packs))


def pack_of(kind: str) -> str | None:
    return next((p for p, kinds in GRAPHIC_PACKS.items() if kind in kinds), None)


def font_file(role: str = "main", brand: Path | None = None) -> Path | None:
    """File font đầu tiên có thật theo thứ tự ưu tiên trong tokens.fonts[role] — tìm trong `brand`, brand/ của hồ sơ,
    rồi library/brand."""
    dirs = [Path(brand)] if brand else []
    try:
        from vf.profile import current

        dirs += current().brand_dirs
    except ValueError:
        pass
    dirs.append(BRAND_DIR)
    for rel in load_tokens().get("fonts", {}).get(role, []):
        for d in dirs:
            p = d / rel
            if p.exists():
                return p
    return None
