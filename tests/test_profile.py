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
    assert have == ["seemee"] and "_mau" not in have
    assert "_mau" in list_profiles(include_template=True)


def test_seemee_tokens_merge_base_and_profile():
    t = load_tokens()
    assert t["safe_zone"]["top"] == 240 and t["timing"]["scene_min_s"] == 1.2  # phần chung
    assert t["brand_label"] == "SEEMEE"
    assert t["presets"]["brand"]["box"] == "berry" and t["colors"]["berry"] == [96, 22, 62]  # phần riêng
    assert t["auto_sfx"]["wipe"] == "swipe"  # gộp sâu: SFX chung vẫn còn
    assert default_preset() == "brand"
    assert all(preset(p)["transition"] == "cut" for p in t["presets"] if not p.startswith("_"))
    for p in t["presets"]:  # mọi màu preset tham chiếu đều có trong bảng màu
        if not p.startswith("_"):
            for k in ("box", "text", "accent", "accent2", "highlight", "stroke"):
                c = t["presets"][p].get(k)
                assert c in (None, "none") or c in t["colors"], (p, k, c)


def test_seemee_profile_no_nha_khoa_pack():
    assert load_tokens()["graphics_packs"] == []
    kinds = enabled_kinds()
    assert {"versus", "steps", "cost_compare", "end_card"} <= kinds
    assert not kinds & {"teeth", "whiten", "shade", "light", "light_timer", "size_fit", "badge"}
    shown = {c.display for c in load_commitments()}
    assert {"Bảo hành 12 tháng", "Chống bỏng", "4 mức nhiệt", "+85% độ bóng mượt"} <= shown


def test_check_profile_rejects_pack_not_enabled():
    errs = check_profile(_v([Graphic(kind="teeth", start=0, end=1)], preset_name="pink"))
    assert any("nha_khoa" in e for e in errs) and any("preset 'pink'" in e for e in errs)
    assert check_profile(_v([Graphic(kind="versus", start=0, end=1, steps=["a | b"])], preset_name="brand")) == []
    assert any("balo" in e for e in check_profile(_v([Graphic(kind="badge", start=0, end=1)])))


def test_gel_refill_alias_and_graphic_defaults():
    g = Graphic(kind="gel_refill", start=0, end=1)
    assert g.kind == "refill"
    v = apply_graphic_defaults(_v([Graphic(kind="cost_compare", start=0, end=1),
                                   Graphic(kind="versus", start=1, end=2, right_label="CÁCH MỚI"),
                                   Graphic(kind="versus", start=2, end=3)]))
    cc, vs, vs2 = v.graphics
    assert (cc.left_label, cc.right_label) == ("RA TIỆM", "SEEMEE")
    assert (vs.left_label, vs.right_label) == ("MÁY CŨ", "CÁCH MỚI")  # ghi tay thì giữ
    assert (vs2.left_label, vs2.right_label) == ("MÁY CŨ", "SEEMEE")


def test_brief_profile_wins(tmp_path):
    set_profile(None)
    (tmp_path / "brief.yaml").write_text("profile: seemee\nplatform: tiktok\n", encoding="utf-8")
    assert use_brief_profile(tmp_path / "brief.yaml") == "seemee"
    assert current_slug() == "seemee"


def test_unknown_profile_message():
    with pytest.raises(ValueError, match="profiles/_mau"):
        get_profile("khong-co")


def test_vf_new_writes_profile(tmp_path):
    cfg = tmp_path / "vf.toml"
    cfg.write_text(f'drive_root = "{(tmp_path / "EDIT").as_posix()}"\n', encoding="utf-8")
    r = CliRunner().invoke(app, ["new", "lo-01", "--profile", "seemee", "--config", str(cfg),
                                 "--jobs-dir", str(tmp_path / "jobs")])
    assert r.exit_code == 0, r.output
    text = (tmp_path / "jobs" / "lo-01" / "brief.yaml").read_text(encoding="utf-8")
    assert "profile: seemee" in text


def test_vf_profiles_lists_all():
    r = CliRunner().invoke(app, ["profiles"])
    assert r.exit_code == 0, r.output
    assert "seemee" in r.output and "SeeMee" in r.output and "nha_khoa" not in r.output


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
def test_seemee_graphics_render(tmp_path):
    """Đồ hoạ gói chung vẽ được với preset brand của SeeMee (khung trong suốt có nội dung ở giữa thẻ)."""
    v = apply_graphic_defaults(_v([
        Graphic(kind="versus", start=0, end=1.6, steps=["bỏng tay | *chống bỏng gấp 2*"], y=0.3),
        Graphic(kind="steps", start=1.6, end=3.2, steps=["CHỐNG BỎNG", "THẺ CÀI GẤP 1,5", "BÓNG MƯỢT +85%"], y=0.3),
        Graphic(kind="end_card", start=3.2, end=5, label="BẢO HÀNH *12 THÁNG*", y=0.3)],
        preset_name="brand"))
    out = render_overlay(v, ROOT / "library/style-guide.md", tmp_path / "seemee.mov",
                         props_path=tmp_path / "seemee.json")
    props = json.loads((tmp_path / "seemee.json").read_text(encoding="utf-8"))
    assert props["preset"] == "brand" and props["tokens"]["brand_label"] == "SEEMEE"
    import cv2

    for t in (1.0, 2.8, 4.5):  # alpha trung bình > 0 trong từng thẻ
        png = tmp_path / f"f{t}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", str(out), "-frames:v", "1",
                        "-vf", "alphaextract", str(png)], check=True)
        assert cv2.imread(str(png), cv2.IMREAD_GRAYSCALE).mean() > 3, t
