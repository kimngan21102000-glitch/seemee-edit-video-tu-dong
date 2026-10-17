"""Dò đồ hoạ/chữ thêm vào che mặt KOL (feedback lo-06/lo-07, 2026-10-16).

Cứ `--every` giây: lấy khung NGUỒN sạch tại thời điểm đó (quy đổi qua các đoạn trong edl), dò mặt (OpenCV Haar), rồi đọc
lớp đồ hoạ trong suốt đã render (`work/_render/<lô>/<id>_overlay.mov`) — phần đặc (alpha ≥ 50 %) phủ lên vùng mặt
(mắt → cằm, không tính tóc) bao nhiêu %. In các khoảng bị che kèm tên thẻ/chữ đang hiện.

    Mac:     .venv/bin/python scripts/face_cover_check.py lo-07 [--every 0.5] [--min 0.08]
    Windows: .venv\\Scripts\\python scripts\\face_cover_check.py lo-07
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
W, H = 270, 480


def _faces(img_bgr, front, profile):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    out = []
    for casc, flip in ((front, False), (profile, False), (profile, True)):
        g = cv2.flip(gray, 1) if flip else gray
        for (x, y, w, h) in casc.detectMultiScale(g, 1.1, 5, minSize=(24, 24)):
            if flip:
                x = W - x - w
            # vùng mặt cần thấy: trán dưới → cằm (không tính tóc), rộng đúng khuôn mặt
            out.append((x, int(y + 0.15 * h), x + w, int(y + 1.15 * h)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lo")
    ap.add_argument("--every", type=float, default=0.5)
    ap.add_argument("--min", type=float, default=0.08, help="tỉ lệ mặt bị che tối thiểu để báo")
    ap.add_argument("--only")
    a = ap.parse_args()
    edl = json.loads((ROOT / "jobs" / a.lo / "edl.json").read_text(encoding="utf-8"))
    front = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    profile = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
    report = {}
    for v in edl["variants"]:
        if a.only and v["id"] != a.only:
            continue
        ov = ROOT / "work" / "_render" / a.lo / f"{v['id']}_overlay.mov"
        props = json.loads((ov.with_suffix(".json")).read_text(encoding="utf-8")) if ov.with_suffix(".json").exists() else {}
        items = [(g["start"], g["end"], g["kind"] + (f" '{g.get('label', '')}'" if g.get("label") else ""))
                 for g in props.get("graphics", []) if g["kind"] != "paper_swipe"]
        items += [(o["start"], o["end"], f"chữ '{o['text']}'") for o in props.get("overlays", [])]
        pieces = [v["hook"]] + v["segments"]
        caps = {}
        tmp = Path(tempfile.mkdtemp())
        # alpha của lớp đồ hoạ, 1 khung / every giây
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(ov), "-vf", f"fps={1 / a.every},scale={W}:{H}",
                        "-pix_fmt", "rgba", str(tmp / "a_%05d.png")], check=True)
        hits = []
        acc = 0.0
        t = 0.0
        k = 1
        total = sum(p["end"] - p["start"] for p in pieces)
        while t < total - 0.05:
            # quy đổi giờ output → giờ nguồn
            acc, src_t, src = 0.0, None, None
            for p in pieces:
                d = p["end"] - p["start"]
                if t < acc + d:
                    src_t, src = p["start"] + (t - acc), p["source"]
                    break
                acc += d
            png = tmp / f"a_{k:05d}.png"
            if src is not None and png.exists():
                cap = caps.get(src) or caps.setdefault(src, cv2.VideoCapture(str(ROOT / "work" / src / "normalized.mp4")))
                cap.set(cv2.CAP_PROP_POS_MSEC, src_t * 1000)
                ok, frame = cap.read()
                alpha = cv2.imread(str(png), cv2.IMREAD_UNCHANGED)
                if ok and alpha is not None and alpha.shape[2] == 4:
                    frame = cv2.resize(frame, (W, H))
                    solid = alpha[:, :, 3] >= 128
                    for (x0, y0, x1, y1) in _faces(frame, front, profile):
                        area = max(1, (x1 - x0) * (y1 - y0))
                        cov = float(solid[y0:y1, x0:x1].sum()) / area
                        if cov >= a.min:
                            names = [n for s, e, n in items if s - 0.05 <= t <= e + 0.05] or ["(không rõ)"]
                            hits.append((round(t, 1), round(cov, 2), ", ".join(names), round(y0 / H, 2), round(y1 / H, 2)))
                            break
            t += a.every
            k += 1
        for c in caps.values():
            c.release()
        # gom theo thẻ
        groups = {}
        for t_, cov, names, fy0, fy1 in hits:
            g = groups.setdefault(names, [t_, t_, 0.0, fy0, fy1])
            g[1] = t_
            g[2] = max(g[2], cov)
        report[v["id"]] = [{"item": n, "from": g[0], "to": g[1], "max_cover": g[2], "face_y": [g[3], g[4]]}
                           for n, g in groups.items()]
        print(f"== {v['id']}")
        for r in report[v["id"]]:
            print(f"   {r['from']:5.1f}–{r['to']:5.1f} s  che {r['max_cover']:.0%} mặt (mặt y {r['face_y'][0]:.2f}–{r['face_y'][1]:.2f}): {r['item']}")
    (ROOT / "work" / "_render" / a.lo / "face_cover.json").write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                                                    encoding="utf-8")


if __name__ == "__main__":
    main()
