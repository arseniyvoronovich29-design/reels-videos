"""Check a finished video: duration, loudness and a contact sheet of real frames.
Usage: python verify.py <spec.py>   -> prints stats, writes final_sheet.png next to the spec
"""
import os, sys, subprocess, re, tempfile
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine as E

E.load(sys.argv[1])
d = E.S["_dir"]
mp4 = os.path.join(d, E.S["slug"] + ".mp4")
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4], capture_output=True, text=True).stdout)
vol = subprocess.run(["ffmpeg", "-hide_banner", "-i", mp4, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
mean = re.search(r"mean_volume: (-?[\d.]+)", vol).group(1)
peak = re.search(r"max_volume: (-?[\d.]+)", vol).group(1)
ts = [0.0] + [round((s["t0"] + s["t1"]) / 2, 2) for s in E.SHOTS]
tmp = tempfile.mkdtemp()
ims = []
for t in ts:
    p = os.path.join(tmp, f"{t}.png")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", mp4, "-frames:v", "1", "-vf", "scale=270:480", p])
    ims.append((t, Image.open(p).convert("RGB")))
cols = 8
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (270 * cols, 480 * rows), (40, 40, 40))
for k, (t, im) in enumerate(ims):
    sheet.paste(im, ((k % cols) * 270, (k // cols) * 480))
    ImageDraw.Draw(sheet).text(((k % cols) * 270 + 5, (k // cols) * 480 + 5), f"{t}s", fill="white")
out = os.path.join(d, "final_sheet.png")
sheet.save(out)
print(f"duration {dur:.1f}s (spec {E.T_END:.1f}s)  mean {mean} dB  peak {peak} dB  sheet {out}")
