"""Bỏ qua biến thể không đổi khi render lại: dấu vân tay = edl của biến thể + phần brief ảnh hưởng tới nó
+ file nguồn dùng tới + code/thông số dựng (vf/, remotion/src/, tokens chung + hồ sơ, SFX, font, commitments).
Dấu khớp với lần render trước và file mp4 còn đó → giữ file cũ (`vf render --force` để render lại hết)."""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

from vf.edl import Variant
from vf.paths import BASE_TOKENS_PATH, CAPTION_STYLE, ROOT

CACHE_NAME = ".render_cache.json"


def _file_sig(p: Path) -> str:
    st = p.stat()
    return f"{p.name}:{st.st_size}:{int(st.st_mtime)}"


def code_fingerprint() -> str:
    """Mọi thứ ngoài edl ảnh hưởng tới hình/tiếng: đổi code hoặc thông số (chung + hồ sơ đang dùng) → mọi biến thể
    render lại."""
    from vf.profile import current_slug

    return _code_fingerprint(current_slug())


@lru_cache(maxsize=4)
def _code_fingerprint(slug: str) -> str:
    from vf.profile import get_profile

    prof = get_profile(slug)
    h = hashlib.sha256()
    files = sorted((ROOT / "vf").glob("*.py")) + sorted((ROOT / "remotion" / "src").glob("*"))
    files += [BASE_TOKENS_PATH, prof.tokens, prof.commitments, CAPTION_STYLE]
    for p in files:
        if p.is_file():
            h.update(p.name.encode())
            h.update(p.read_bytes())
    for d in prof.brand_dirs:  # SFX, font: chỉ cần tên + kích thước + thời gian sửa
        for p in sorted(d.rglob("*")):
            if p.is_file() and p.suffix.lower() in (".wav", ".mp3", ".m4a", ".ogg", ".ttf", ".otf"):
                h.update(_file_sig(p).encode())
    return h.hexdigest()


def variant_fingerprint(v: Variant, sources: dict[str, Path], brief_ctx: dict) -> str:
    """`brief_ctx`: phần brief ảnh hưởng tới biến thể (text_sources, text_free, forbidden, target…)."""
    used = sorted({p.source for p in v.pieces()} | {st.source for g in v.graphics for st in g.stills})
    payload = {
        "variant": v.model_dump(mode="json"),
        "brief": brief_ctx,
        "sources": [_file_sig(Path(sources[s])) for s in used if s in sources],
        "code": code_fingerprint(),
    }
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def load_cache(out_dir: Path) -> dict[str, str]:
    p = Path(out_dir) / CACHE_NAME
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}


def save_cache(out_dir: Path, cache: dict[str, str]) -> None:
    (Path(out_dir) / CACHE_NAME).write_text(json.dumps(cache, indent=1), encoding="utf-8")
