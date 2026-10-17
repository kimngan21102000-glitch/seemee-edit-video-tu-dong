"""Chạy SAU build_edl.py (lô này KHÔNG chạy vf snap — nhạc nền làm snap kéo mép lấn chữ kế): đoạn nào kéo tiếng qua điểm chuyển cảnh ≤ 0,5 s cuối (để KOL nói hết chữ) thì hình
dừng ở điểm chuyển cảnh (`video_end`), khúc hình cuối render làm chậm phủ phần tiếng thêm — feedback lo-08."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = Path(__file__).with_name("edl.json")  # mẫu: sửa edl cạnh file này (chép cả thư mục vào jobs/<lô>/ để dùng)
e = json.loads(p.read_text(encoding="utf-8"))
cuts = {}
for v in e["variants"]:
    for seg in [v["hook"]] + v["segments"]:
        src = seg["source"]
        sc = cuts.setdefault(src, json.loads((ROOT / "work" / src / "scenes.json").read_text(encoding="utf-8")))
        inside = [c for c in sc if seg["start"] + 0.5 < c < seg["end"] and seg["end"] - c <= 0.5]  # mẩu cảnh sau ≤ 0,5 s = lóe
        seg.pop("video_end", None)
        if inside:
            seg["video_end"] = round(inside[0] - 0.02, 3)
            print(f"{v['id']}: {seg['start']:.2f}–{seg['end']:.2f} → hình dừng {seg['video_end']:.2f}, "
                  f"làm chậm phủ {seg['end'] - seg['video_end']:.2f} s tiếng")
p.write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
