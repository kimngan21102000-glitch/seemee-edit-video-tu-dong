import wave

import numpy as np

from vf.audiocut import edge_level_db, snap, snap_variant


def _wav(path, segments, sr=16000):
    """segments: [(giây, có_giọng)] → tiếng giả: sóng 220 Hz khi có giọng, im lặng khi không."""
    x = np.concatenate([(0.5 * np.sin(2 * np.pi * 220 * np.arange(int(sr * d)) / sr)) if on else np.zeros(int(sr * d))
                        for d, on in segments])
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def test_snap_moves_edge_into_nearby_silence(tmp_path):
    f = tmp_path / "a.wav"
    _wav(f, [(1.0, True), (0.2, False), (1.0, True)])  # lặng 1,0–1,2 s
    assert edge_level_db(f, 0.95) > -26  # đang có giọng
    t = snap(f, 0.95)
    assert 1.0 <= t <= 1.2 and edge_level_db(f, t) < -26


def test_snap_never_crosses_into_neighbor_word_and_mutes_stray_tail(tmp_path):
    """Feedback lo-05: snap dời mép ra ngoài lấn sang chữ kề bên ("…mua lẻ thêm gel" + "nữa") — mép không được vượt
    ranh giới chữ kề; KOL nói liền thì tắt tiếng mẩu chữ thừa, giữ hình (khoảng trống âm thanh)."""
    from vf.analyze import Word

    f = tmp_path / "a.wav"
    # chữ trước kêu tới 1,00 (mốc phiên âm ghi 0,90), ngắt hơi 1,00–1,03, chữ của đoạn 1,03–2,0, lặng 2,0–2,4
    _wav(f, [(1.0, True), (0.03, False), (0.97, True), (0.4, False)])
    words = {"a": [Word(text="nữa", start=0.5, end=0.90), Word(text="Nói", start=0.95, end=1.6),
                   Word(text="chung", start=1.6, end=2.0)]}
    vd = {"hook": {"source": "a", "start": 0.95, "end": 2.0}, "segments": [],
          "overlays": [], "graphics": [], "effects": []}
    out, _ = snap_variant(vd, {"a": f}, words)
    h = out["hook"]
    assert 1.0 <= h["start"] <= 1.03  # mép vào đúng khoảng lặng thật dù mốc phiên âm lệch (đuôi "nữa" kêu tới 1,00)
    assert edge_level_db(f, h["start"]) < -26 and not h.get("mute_head")


def test_snap_mutes_short_stray_when_no_real_silence(tmp_path):
    """Nói liền không có khoảng lặng ≥ 30 ms: giữ mép, tắt tiếng mẩu chữ kề ≤ 80 ms tới chỗ hở rõ nhất."""
    from vf.analyze import Word

    f = tmp_path / "a.wav"
    # chữ trước kêu tới 1,00, hở 20 ms (không đủ là khoảng lặng), chữ của đoạn 1,02–2,0, lặng 2,0–2,4
    _wav(f, [(1.0, True), (0.02, False), (0.98, True), (0.4, False)])
    words = {"a": [Word(text="nữa", start=0.5, end=0.95), Word(text="Nói", start=0.95, end=2.0)]}
    vd = {"hook": {"source": "a", "start": 0.95, "end": 2.0}, "segments": [],
          "overlays": [], "graphics": [], "effects": []}
    out, _ = snap_variant(vd, {"a": f}, words)
    h = out["hook"]
    assert h["start"] == 0.95 and 0.04 <= h.get("mute_head", 0) <= 0.08


def test_snap_variant_never_eats_inward_and_remaps_text(tmp_path):
    f = tmp_path / "a.wav"
    _wav(f, [(1.0, True), (0.2, False), (2.0, True), (0.2, False), (1.0, True)])  # lặng 1,0–1,2 và 3,2–3,4
    vd = {"hook": {"source": "a", "start": 0.0, "end": 0.9},
          "segments": [{"source": "a", "start": 1.25, "end": 3.15}],
          "overlays": [{"start": 1.5, "end": 2.0}], "graphics": [], "effects": []}
    out, changes = snap_variant(vd, {"a": f})
    s = out["segments"][0]
    assert s["start"] < 1.25 and s["end"] > 3.15  # chỉ nới ra chỗ lặng, không cắt vào trong
    assert changes and out["overlays"][0]["start"] > 1.5 - 0.3
