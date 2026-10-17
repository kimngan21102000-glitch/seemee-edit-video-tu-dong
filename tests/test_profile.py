"""Hồ sơ sản phẩm (profiles/), gói đồ hoạ, chọn bộ mã hoá / bộ phiên âm theo nền tảng."""
import json
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from vf import render, transcribe
from vf.cli import app
from vf.edl import Graphic, Segment, Variant, apply_graphic_defaults, check_profile
from vf.motion import REMOTION_DIR, load_commitments, render_overlay
from vf.profile import current_slug, get_profile, list_profiles, set_profile, use_brief_profile
from vf.tokens import default_preset, enabled_kinds, load_tokens, preset

ROOT = Path(__file__).resolve().parents[1]
needs_remotion = pytest.mark.skipif(not (REMOTION_DIR / "node_modules").exists(),
                                    reason="chưa cài remotion (cd remotion && npm i)")


def _v(graphics=(), preset_name=None, effects=()):
    return Variant(id="t", hook_type="pain", preset=preset_name, rationale="test",
                   hook=Segment(source="a.mp4", start=0, end=2), segments=[Segment(source="a.mp4", start=2, end=5)],
                   graphics=list(graphics), effects=list(effects))


def test_profiles_listed_without_template():
    have = list_profiles()
    assert {"smilee", "balo"} <= set(have) and "_mau" not in have
    assert "_mau" in list_profiles(include_template=True)


def test_smilee_tokens_merge_base_and_profile():
    t = load_tokens()
    assert t["safe_zone"]["top"] == 240 and t["timing"]["scene_min_s"] == 1.2  # phần chung
    assert t["presets"]["pink"]["box"] == "plum" and t["colors"]["plum"] == [74, 31, 61]  # phần riêng
    assert t["auto_sfx"]["teeth"] == "shimmer" and t["auto_sfx"]["wipe"] == "swipe"  # gộp sâu
    assert default_preset() == "pink"
    assert all(preset(p)["transition"] == "cut" for p in t["presets"] if not p.startswith("_"))


def test_balo_profile_has_own_presets_and_pack():
    set_profile("balo")
    assert default_preset() == "brand"
    assert {"size_fit", "compartments", "badge", "versus"} <= enabled_kinds()
    assert "teeth" not in enabled_kinds()
    assert load_commitments() == []  # khung: chưa có cam kết nào được bật


def test_check_profile_rejects_pack_not_enabled():
    set_profile("balo")
    errs = check_profile(_v([Graphic(kind="teeth", start=0, end=1)], preset_name="pink"))
    assert any("nha_khoa" in e for e in errs) and any("preset 'pink'" in e for e in errs)
    assert check_profile(_v([Graphic(kind="size_fit", start=0, end=1)], preset_name="brand")) == []
    set_profile("smilee")
    assert any("balo" in e for e in check_profile(_v([Graphic(kind="badge", start=0, end=1)])))


def test_gel_refill_alias_and_graphic_defaults():
    g = Graphic(kind="gel_refill", start=0, end=1)
    assert g.kind == "refill"
    v = apply_graphic_defaults(_v([Graphic(kind="cost_compare", start=0, end=1),
                                   Graphic(kind="versus", start=1, end=2, right_label="CÁCH MỚI"), g]))
    cc, vs, rf = v.graphics
    assert (cc.left_label, cc.right_label) == ("NHA KHOA", "SMILEE")
    assert (vs.left_label, vs.right_label) == ("CÁCH CŨ", "CÁCH MỚI")  # ghi tay thì giữ
    assert rf.label == "HẾT GEL? *MUA LẺ*"


def test_brief_profile_wins(tmp_path):
    (tmp_path / "brief.yaml").write_text("profile: balo\nplatform: tiktok\n", encoding="utf-8")
    assert use_brief_profile(tmp_path / "brief.yaml") == "balo"
    assert current_slug() == "balo"


def test_unknown_profile_message():
    with pytest.raises(ValueError, match="profiles/_mau"):
        get_profile("khong-co")


def test_vf_new_writes_profile(tmp_path):
    cfg = tmp_path / "vf.toml"
    cfg.write_text(f'drive_root = "{(tmp_path / "EDIT").as_posix()}"\n', encoding="utf-8")
    r = CliRunner().invoke(app, ["new", "lo-01", "--profile", "balo", "--config", str(cfg),
                                 "--jobs-dir", str(tmp_path / "jobs")])
    assert r.exit_code == 0, r.output
    text = (tmp_path / "jobs" / "lo-01" / "brief.yaml").read_text(encoding="utf-8")
    assert "profile: balo" in text


def test_vf_profiles_lists_all():
    r = CliRunner().invoke(app, ["profiles"])
    assert r.exit_code == 0, r.output
    assert "smilee" in r.output and "balo" in r.output and "nha_khoa" in r.output


def test_encoder_videotoolbox_on_mac(monkeypatch):
    monkeypatch.setattr(render.sys, "platform", "darwin")
    monkeypatch.delenv("VF_ENCODER", raising=False)
    monkeypatch.setattr(render, "_encoder_works", lambda codec: codec == "h264_videotoolbox")
    assert render.video_encoder_args() == render.VT_ARGS
    assert not render.nvenc_available()
    monkeypatch.setattr(render, "_encoder_works", lambda codec: False)  # ffmpeg không có VideoToolbox → CPU
    assert render.video_encoder_args() == render.CPU_ARGS
    monkeypatch.setenv("VF_ENCODER", "cpu")
    monkeypatch.setattr(render, "_encoder_works", lambda codec: True)
    assert render.encoder_name() == "libx264"


def test_encoder_nvenc_on_windows(monkeypatch):
    monkeypatch.setattr(render.sys, "platform", "win32")
    monkeypatch.delenv("VF_ENCODER", raising=False)
    monkeypatch.setattr(render, "_encoder_works", lambda codec: codec == "h264_nvenc")
    assert render.video_encoder_args() == render.NVENC_ARGS
    assert not render.videotoolbox_available()


def test_transcribe_backend_choice(monkeypatch):
    monkeypatch.delenv("VF_TRANSCRIBER", raising=False)
    monkeypatch.setattr(transcribe, "is_apple_silicon", lambda: True)
    monkeypatch.setattr(transcribe, "mlx_available", lambda: True)
    assert transcribe.backend() == "mlx"
    monkeypatch.setattr(transcribe, "mlx_available", lambda: False)
    assert transcribe.backend() == "faster"  # Mac chưa cài mlx-whisper → faster-whisper CPU
    monkeypatch.setattr(transcribe, "is_apple_silicon", lambda: False)
    monkeypatch.setattr(transcribe, "mlx_available", lambda: True)
    assert transcribe.backend() == "faster"
    monkeypatch.setenv("VF_TRANSCRIBER", "mlx")
    assert transcribe.backend() == "mlx"
    assert transcribe.mlx_repo("large-v3") == "mlx-community/whisper-large-v3-mlx"
    assert transcribe.mlx_repo("org/model") == "org/model"


@needs_remotion
def test_balo_graphics_render(tmp_path):
    """3 đồ hoạ gói balo vẽ được (khung trong suốt có nội dung ở giữa thẻ)."""
    set_profile("balo")
    v = _v([Graphic(kind="size_fit", start=0, end=1.5, label="VỪA LAPTOP *15,6″*", sub="45 × 30 × 15 cm", y=0.3),
            Graphic(kind="compartments", start=1.5, end=3.2, steps=["NGĂN LAPTOP | chống sốc", "NGĂN CHAI NƯỚC"], y=0.3),
            Graphic(kind="badge", start=3.2, end=5, icon="water", label="*CHỐNG NƯỚC*", sub="vải Oxford", y=0.3)],
           preset_name="brand")
    out = render_overlay(v, ROOT / "library/style-guide.md", tmp_path / "balo.mov",
                         props_path=tmp_path / "balo.json")
    props = json.loads((tmp_path / "balo.json").read_text(encoding="utf-8"))
    assert props["preset"] == "brand" and "brand" in props["tokens"]["presets"]
    import cv2

    for t in (1.0, 2.8, 4.5):  # alpha trung bình > 0 trong từng thẻ
        png = tmp_path / f"f{t}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", str(out), "-frames:v", "1",
                        "-vf", "alphaextract", str(png)], check=True)
        assert cv2.imread(str(png), cv2.IMREAD_GRAYSCALE).mean() > 3, t
