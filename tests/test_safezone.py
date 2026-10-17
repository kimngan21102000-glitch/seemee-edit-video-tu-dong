from pathlib import Path

from vf.scenes import PieceVideo
from vf.creative import auto_sfx, lint_batch, lint_variant
from vf.edl import Effect, Graphic, Segment, TextOverlay, Variant
from vf.placement import BOTTOM_MAX, TOP_MIN, fit_callout, place, safe_text_w_px, text_box
from vf.safezone import SAFE

SRC = "a.mp4"


def _v(**kw):
    base = dict(id="x", hook_type="pain", rationale="", hook=Segment(source=SRC, start=0, end=2),
                segments=[Segment(source=SRC, start=2, end=30)])
    return Variant(**{**base, **kw})


def test_safe_zone_numbers():
    assert round(SAFE.y0, 3) == 0.125 and round(SAFE.y1, 3) == 0.656
    assert SAFE.rail_w == 300 and round(SAFE.center_x(0.5, 0.6), 3) == 0.417  # nửa dưới: lệch trái
    # dưới hàng cột nút, hộp căn giữa hẹp hơn
    assert SAFE.max_centered_w(0.5, 0.6) < SAFE.max_centered_w(0.2, 0.3)
    assert SAFE.violations((0.2, 0.2, 0.8, 0.3)) == []
    assert "dưới" in SAFE.violations((0.2, 0.6, 0.8, 0.7))
    assert "phải (cột nút)" in SAFE.violations((0.1, 0.5, 0.9, 0.6))


def test_place_keeps_everything_inside_safe_zone():
    long_text = "Niềng răng xong việc đầu tiên cần làm là gì vậy mọi người ơi"
    overlays = [
        TextOverlay(text=long_text, start=0, end=2, position="bottom", style="hook"),
        TextOverlay(text="Bấm giỏ hàng", start=3, end=5, position="bottom", style="cta"),
        TextOverlay(text="Sát đáy", start=6, end=7, y=0.9, style="label"),  # y ghi tay ngoài vùng an toàn
        TextOverlay(text="RĂNG Ố VÀNG", sub="thấy rõ luôn", start=8, end=9, position="bottom", style="lower"),
    ]
    graphics = [Graphic(kind="teeth", start=10, end=12, y=0.8), Graphic(kind="shade", start=13, end=15)]
    ovs, gs, notes = place([], [], {}, overlays, graphics, faces=False)
    for o in ovs:
        w, h = text_box(o, o.max_w)
        box = (o.xc - w / 2, o.y, o.xc + w / 2, o.y + h)
        assert SAFE.violations(box) == [], (o.text, box)
        assert o.max_w <= safe_text_w_px(o.y, o.y + h) + 1
    for g in gs:
        assert TOP_MIN - 1e-6 <= g.y
    assert any("Sát đáy" in n for n in notes) and any("teeth" in n for n in notes)


def test_callout_pulled_inside():
    g = fit_callout(Graphic(kind="callout", start=0, end=1, cx=0.95, cy=0.9, rx=0.3, ry=0.1))
    assert SAFE.violations((g.cx - g.rx, g.cy - g.ry, g.cx + g.rx, g.cy + g.ry)) == []
    assert g.cy + g.ry <= BOTTOM_MAX + 1e-6


def test_auto_sfx_uses_existing_files_only(tmp_path):
    sfx = tmp_path / "sfx"
    sfx.mkdir()
    for n in ("whoosh", "pop", "tick"):
        (sfx / f"{n}.wav").write_bytes(b"")
    v = _v(effects=[Effect(kind="zoom_to", at=3.0), Effect(kind="sfx", at=7.0, asset="x.wav"),
                    Effect(kind="zoom_punch", at=7.05)],
           overlays=[TextOverlay(text="chữ", start=10, end=12)],
           graphics=[Graphic(kind="callout", start=3, end=4), Graphic(kind="counter", start=8, end=9.5),
                     Graphic(kind="shade", start=12, end=12.3), Graphic(kind="counter", start=20, end=21)])
    out = auto_sfx(v, sfx)
    # feedback lo-03: không SFX cho zoom/chữ hiện; callout thiếu marker.wav; counter 8 s quá gần SFX tay 7 s (< 2 s);
    # shade 0,3 s < 0,5 s; chỉ còn counter 20 s
    assert [(e.at, e.asset) for e in out] == [(20.0, "sfx/tick.wav")]
    assert auto_sfx(v.model_copy(update={"sfx_auto": False}), sfx) == []


def test_lint_flags_late_cta_missing_hook_text_and_silence():
    v = _v(overlays=[TextOverlay(text="Bấm giỏ hàng", start=29, end=31, style="cta")])
    notes = " | ".join(lint_variant(v))
    assert "hook" in notes and "CTA" in notes and "âm thanh" in notes and "chapter" in notes


def test_lint_clean_variant_with_all_chapters():
    chapters = ["pain", "benefit", "result", "proof", "speed", "saving", "cta"]
    segs = [Segment(source=SRC, start=2 + 7 * i, end=9 + 7 * i, chapter=c) for i, c in enumerate(chapters)]
    total = 2 + 7 * len(chapters)  # 51 s
    overlays = [TextOverlay(text="Răng vàng?", start=0.2, end=2.0)]
    overlays += [TextOverlay(text=f"ý {i}", start=t, end=t + 1.5, position="top") for i, t in enumerate(range(4, total - 4, 3))]
    overlays += [TextOverlay(text="Bấm giỏ hàng", start=0.7 * total, end=0.7 * total + 1.5, style="cta"),
                 TextOverlay(text="Bấm giỏ hàng", start=total - 2.5, end=total, style="cta")]
    v = _v(music="m.mp3", segments=segs, overlays=overlays)
    assert lint_variant(v) == []


def test_lint_v2_rules_protect_scene_and_missing_chapters():
    v = _v(music="m.mp3", segments=[Segment(source=SRC, start=2, end=3, chapter="proof", protect=True),
                                    Segment(source=SRC, start=3, end=50, chapter="cta")],
           overlays=[TextOverlay(text="Trước", start=2.1, end=3.5, position="center")])
    notes = " | ".join(lint_variant(v))
    assert "protect" in notes and "ngắn hơn 1.2" in notes and "chữ giữa khung đè cảnh protect" in notes
    assert "còn thiếu nỗi đau" in notes


def test_auto_fix_extends_short_text():
    from vf.creative import auto_fix

    v = _v(overlays=[TextOverlay(text="mảng bám ngả vàng thấy rõ luôn", start=3, end=3.5)])  # trong đoạn 2–30 s
    fixed, notes = auto_fix(v)
    assert fixed.overlays[0].end == 3 + 0.6 + 0.25 * 7 and notes  # 7 từ


def test_whip_and_paper_transitions():
    from vf.creative import chapter_cuts, transition_graphics

    v = _v(preset="vox", segments=[Segment(source=SRC, start=2, end=6, chapter="pain"),
                                   Segment(source=SRC, start=6, end=9),
                                   Segment(source=SRC, start=9, end=12, chapter="proof")])
    assert chapter_cuts(v) == [2.0, 9.0]  # hook→pain, pain→proof (đoạn không ghi chương = chương trước)
    assert transition_graphics(v) == []  # feedback lo-04: bỏ giấy lướt — chuyển cảnh làm bằng xfade (render)


def test_plan_transitions_all_presets_hard_cut():
    """Feedback lo-07: chồng mờ làm đè hình hai cảnh / hai khẩu hình → mọi preset cắt thẳng (kể cả cắt nhảy)."""
    from vf.probe import MediaInfo
    from vf.render import plan_transitions
    from vf.scenes import PieceVideo

    info = {SRC: MediaInfo(duration=100.0, width=1080, height=1920, fps=30.0, has_audio=True, codec="h264")}
    v = _v(preset="vox", segments=[Segment(source=SRC, start=2, end=6, chapter="pain"),
                                   Segment(source=SRC, start=8, end=12),
                                   Segment(source=SRC, start=20, end=26, chapter="proof")])
    vids = [PieceVideo(), PieceVideo(), PieceVideo(jump=True), PieceVideo()]
    t = plan_transitions(v, vids, info)
    assert t == [None] * 4
    for pr in ("pink", "proof", "kinetic", "gift", "routine", "reply", "ugc"):
        assert plan_transitions(v.model_copy(update={"preset": pr}), vids, info) == [None] * 4


def test_manual_y_moves_off_face():
    """Feedback lo-06/lo-07: thẻ đặt y tay đè mặt KOL → tự dời tới chỗ gần nhất không che mặt."""
    from vf.placement import face_cover, graphic_box, _box

    face = (0.3, 0.3, 0.7, 0.62)  # mặt (đã nới tới dưới cằm) giữa khung
    fd = [([face], None)]
    g = Graphic(kind="versus", start=0, end=3, y=0.45, steps=["a | b"])
    w, h = graphic_box(g)
    assert face_cover(fd, _box(w, 0.45, h)[0]) > 0.02
    from vf import placement
    orig = placement._Frames
    class Fake:  # noqa: E306
        def __init__(self, *_): pass
        def analyse(self, *_): return ([face], None)
        def close(self): pass
    placement._Frames = Fake
    try:
        _, gs, _ = place([Segment(source=SRC, start=0, end=5)], [PieceVideo()], {SRC: Path("x.mp4")}, [], [g])
    finally:
        placement._Frames = orig
    y = gs[0].y
    before, after = face_cover(fd, _box(w, 0.45, h)[0]), face_cover(fd, _box(w, y, h)[0])
    assert after < before / 4  # chỗ che ít nhất (trên mặt chỉ vừa khít thẻ 360 px)
    assert SAFE.violations((gs[0].xc - w / 2, y, gs[0].xc + w / 2, y + h)) == []


def test_preset_aliases_and_ugc_has_no_auto_sfx(tmp_path):
    (tmp_path / "tick.wav").write_bytes(b"")
    v = _v(preset="beat", graphics=[Graphic(kind="counter", start=0, end=2)])
    assert v.preset == "kinetic" and auto_sfx(v, tmp_path)
    assert auto_sfx(v.model_copy(update={"preset": "ugc"}), tmp_path) == []


def test_lint_batch_duplicate_hooks():
    a, b = _v(id="a"), _v(id="b")
    c = _v(id="c", hook=Segment(source=SRC, start=10, end=12))
    assert lint_batch([a, b, c]) == {"b": ["hook trùng với a — đổi câu/khung hình mở đầu"]}


def test_auto_fix_stops_at_cut_and_text_free():
    """lo-03: chữ tự kéo dài từng vắt qua điểm cắt và đè chữ in sẵn của nguồn."""
    from vf.creative import auto_fix

    v = _v(segments=[Segment(source=SRC, start=2, end=4), Segment(source=SRC, start=10, end=20)],
           overlays=[TextOverlay(text="trà sữa cà phê uống nhiều là vàng lại", start=2.2, end=3.0),
                     TextOverlay(text="chữ", start=4.5, end=5.0)])
    fixed, notes = auto_fix(v, {SRC}, {SRC: [[0.0, 3.6], [10.0, 20.0]]})
    assert fixed.overlays[0].end == 3.6  # dừng ở hết khoảng không chữ (giờ nguồn 3.6 = output 3.6), không tới cắt 4.0
    assert any("đọc không kịp" in n for n in notes)
    assert fixed.overlays[1].end == 4.5 + 1.2


def test_lint_cuts_finds_clipped_words_and_freezes():
    from types import SimpleNamespace as W

    from vf.creative import lint_cuts
    from vf.scenes import PieceVideo

    words = {SRC: [W(text="Ai", start=9.0, end=9.3), W(text="mà", start=9.3, end=9.5),
                   W(text="Tất", start=19.9, end=20.2), W(text="nhiên", start=20.2, end=20.5)]}
    v = _v(segments=[Segment(source=SRC, start=9.3, end=12), Segment(source=SRC, start=20.0, end=22)])
    notes = " | ".join(lint_cuts(v, words, [PieceVideo(), PieceVideo(), PieceVideo(head=0.27)]))
    assert "mất chữ đầu câu" in notes and "\"Ai\"" in notes
    assert "cắt giữa từ" in notes and "Tất" in notes
    assert "đứng hình" in notes
    # đoạn nối liền đoạn trước cùng nguồn: không báo mất chữ
    v2 = _v(hook=Segment(source=SRC, start=7.0, end=9.3), segments=[Segment(source=SRC, start=9.3, end=12)])
    assert not any("mất chữ" in n for n in lint_cuts(v2, words, None))


def test_new_motion_steps_and_live_cta_placed_safe_and_count_as_cta():
    """Motion mới sau lo-03: thẻ các bước + CTA bấm vào live nằm trong vùng an toàn; live_cta tính là CTA."""
    from vf.placement import graphic_box

    gs_in = [Graphic(kind="steps", start=0, end=4, steps=["BÔI GEL | lớp mỏng", "ĐÈN XANH | 10 phút"]),
             Graphic(kind="live_cta", start=5, end=8, label="BẤM VÀO LIVE"),
             Graphic(kind="shade", start=9, end=11, days=7)]
    _, gs, _ = place([], [], {}, [], gs_in, faces=False)
    for g in gs:
        w, h = graphic_box(g)
        assert SAFE.violations((g.xc - w / 2, g.y, g.xc + w / 2, g.y + h)) == [], g.kind
    v = _v(music="m.mp3", graphics=[Graphic(kind="live_cta", start=18, end=21), Graphic(kind="live_cta", start=27.5, end=30)])
    assert not any(n.startswith("CTA") for n in lint_variant(v))


def test_lo05_motion_placed_safe_and_compact_steps_is_short():
    """Motion lo-05: miếng dán gạch chéo, cột chi phí, bút gel, thẻ bước gọn (nửa dưới) nằm trong vùng an toàn."""
    from vf.placement import graphic_box

    gs_in = [Graphic(kind="nope", start=0, end=4, label="*Ê BUỐT*"),
             Graphic(kind="cost_compare", start=5, end=8, label="CHỈ *1/3*"),
             Graphic(kind="gel_refill", start=9, end=11, label="HẾT GEL? *MUA LẺ*", sub="không mua lại máy"),
             Graphic(kind="steps", start=12, end=20, compact=True, y=0.6, times=[0.2, 1.9, 4.9, 11.8],
                     steps=["ĐÁNH RĂNG", "BÔI GEL", "NGẬM · BẬT NÚT", "MÁY TỰ NGẮT"])]
    _, gs, _ = place([], [], {}, [], gs_in, faces=False)
    for g in gs:
        w, h = graphic_box(g)
        assert SAFE.violations((g.xc - w / 2, g.y, g.xc + w / 2, g.y + h)) == [], g.kind
    steps = gs[-1]
    assert graphic_box(steps)[1] * 1920 < 300 and steps.y + graphic_box(steps)[1] <= SAFE.y1 + 1e-6


def test_lint_content_order_extra_before_cta():
    """Feedback lo-04: tiện ích phụ (du lịch) để sau hiệu quả/bằng chứng, ngay trước CTA."""
    bad = _v(music="m.mp3", segments=[Segment(source=SRC, start=2, end=20, chapter="extra"),
                                      Segment(source=SRC, start=20, end=40, chapter="proof"),
                                      Segment(source=SRC, start=40, end=50, chapter="cta")])
    notes = " | ".join(lint_variant(bad))
    assert "tiện ích phụ" in notes
    late = _v(music="m.mp3", segments=[Segment(source=SRC, start=2, end=40, chapter="pain"),
                                       Segment(source=SRC, start=40, end=50, chapter="proof")])
    assert any("xuất hiện muộn" in n for n in lint_variant(late))
    good = _v(music="m.mp3", segments=[Segment(source=SRC, start=2, end=20, chapter="proof"),
                                       Segment(source=SRC, start=20, end=40, chapter="extra"),
                                       Segment(source=SRC, start=40, end=50, chapter="cta")])
    assert not any(n.startswith("thứ tự") for n in lint_variant(good))
