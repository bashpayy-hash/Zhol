"""Turn a Higgsfield image-to-video clip into a seamless, light-stable loop for the site.

    python scripts/scene_loop.py RAW.mp4 site/assets/img/scenes/NAME

writes NAME-1280.mp4/.webm, NAME-720.mp4/.webm and NAME-poster.webp (4:3).

Why each step (the owner saw these go wrong before, see VISION.md 3.7 and brand/MASCOT.md §6):
- the clip is generated with the same first and last frame; its last frame repeats the first, so it is
  dropped, and the last 16 frames ease into frame 0, so the loop has no hitch at the seam;
- RGB <-> YUV conversions use the BT.709 matrix and the files are tagged BT.709 with the sRGB curve,
  otherwise browsers show the video darker and warmer than the poster and the light jumps at start;
- the poster is frame 0 of the processed loop, not the original still, for the same reason.
- on the page the poster is a plain <img>, and the loop's frames are painted on a <canvas> over it
  (site/assets/scene.js): a visible <video> goes through the driver's overlay and its light differs from
  the picture's; check that poster and frame 0 match (PSNR 36 dB or more) before publishing a new loop.
Needs ffmpeg with libx264 and libvpx-vp9, and numpy + Pillow.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

W, H = 1280, 960
BLEND = 16
TAGS = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "iec61966-2-1", "-color_range", "tv"]


def decode(raw: Path) -> np.ndarray:
    cmd = ["ffmpeg", "-v", "error", "-i", str(raw),
           "-vf", f"scale=-2:{H}:in_color_matrix=bt709:in_range=tv:flags=lanczos,crop={W}:{H}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    data = subprocess.run(cmd, check=True, capture_output=True).stdout
    return np.frombuffer(data, dtype=np.uint8).reshape(-1, H, W, 3)


def loop(frames: np.ndarray) -> np.ndarray:
    f = frames[:-1].copy()                       # the last frame repeats the first
    n = len(f)
    first = f[0].astype(np.float32)
    for k in range(BLEND):
        i = n - BLEND + k
        t = (k + 1) / (BLEND + 1)
        w = t * t * (3 - 2 * t)                  # smoothstep: no visible start or end of the blend
        f[i] = np.clip(f[i].astype(np.float32) * (1 - w) + first * w + 0.5, 0, 255).astype(np.uint8)
    return f


def encode(frames: np.ndarray, out: Path, fps: str) -> None:
    raw = frames.tobytes()
    for size in (1280, 720):
        scale = f"scale={size}:-2:flags=lanczos," if size != W else ""
        vf = f"{scale}scale=out_color_matrix=bt709:out_range=tv,format=yuv420p"
        base = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", fps, "-i", "-", "-vf", vf, "-an"]
        mp4 = base + ["-c:v", "libx264", "-preset", "slow", "-crf", "22" if size == 1280 else "24", "-profile:v", "high",
                      "-movflags", "+faststart", *TAGS, f"{out}-{size}.mp4"]
        webm = base + ["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "36" if size == 1280 else "38", "-row-mt", "1",
                       "-deadline", "good", "-cpu-used", "2", *TAGS, f"{out}-{size}.webm"]
        for cmd in (mp4, webm):
            subprocess.run(cmd, input=raw, check=True)


def main(raw: str, out: str) -> None:
    raw_p, out_p = Path(raw), Path(out)
    fps = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                          "-of", "csv=p=0", str(raw_p)], check=True, capture_output=True, text=True).stdout.strip()
    frames = loop(decode(raw_p))
    encode(frames, out_p, fps)
    Image.fromarray(frames[0]).save(f"{out_p}-poster.webp", quality=82, method=6)
    seam = np.abs(frames[-1].astype(np.float32) - frames[0].astype(np.float32)).mean()
    step = np.mean([np.abs(frames[i + 1].astype(np.float32) - frames[i].astype(np.float32)).mean() for i in range(0, len(frames) - 1, 8)])
    print(f"{out_p.name}: {len(frames)} frames at {fps} fps, seam {seam:.2f} vs typical step {step:.2f}")
    for p in sorted(out_p.parent.glob(out_p.name + "-*")):
        print(f"  {p.name} {p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
