from vf.cache import load_cache, save_cache, variant_fingerprint
from vf.edl import Segment, TextOverlay, Variant


def _v(**kw):
    base = dict(id="a", hook_type="pain", rationale="", hook=Segment(source="s.mp4", start=0, end=2),
                segments=[Segment(source="s.mp4", start=2, end=8)])
    return Variant(**{**base, **kw})


def test_fingerprint_changes_only_with_inputs(tmp_path):
    src = tmp_path / "s.mp4"
    src.write_bytes(b"x" * 10)
    sources = {"s.mp4": src}
    ctx = {"text_free": {}, "forbidden": []}
    a = variant_fingerprint(_v(), sources, ctx)
    assert a == variant_fingerprint(_v(), sources, ctx)
    assert a != variant_fingerprint(_v(overlays=[TextOverlay(text="x", start=0, end=1)]), sources, ctx)
    assert a != variant_fingerprint(_v(), sources, {"text_free": {"s.mp4": [[0, 1]]}, "forbidden": []})
    src.write_bytes(b"y" * 20)  # nguồn đổi
    assert a != variant_fingerprint(_v(), sources, ctx)


def test_cache_roundtrip(tmp_path):
    assert load_cache(tmp_path) == {}
    save_cache(tmp_path, {"a": "123"})
    assert load_cache(tmp_path) == {"a": "123"}
