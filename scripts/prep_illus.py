"""Prepare generated illustrations for the site.

- shift the light paper tones of each image to the site paper colour (#f1ede3, the rendered paper),
  weighting by luminance so teal, ink and red stay as generated;
- optionally feather the edges into transparency so the picture sits on the page paper;
- export WebP at a sensible width.

usage: python3 prep_illus.py SRC DST WIDTH [feather|frame|raw] [TARGET_HEX]

TARGET_HEX is the colour the background is shifted to: f6f3ea (paper, default) or d2decc (sage).
With "feather" on a dark image, the background is left as is and only the edges fade.
"""
import sys
import numpy as np
from PIL import Image

PAPER = np.array([241, 237, 227], dtype=np.float32)   # the paper as rendered, with its grain


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def main(src, dst, width, mode, target=None):
    paper = PAPER if not target else np.array([int(target[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.float32)
    h, w, _ = a.shape
    # background estimate: median of a border band
    band = max(6, int(min(h, w) * 0.02))
    border = np.concatenate([a[:band].reshape(-1, 3), a[-band:].reshape(-1, 3),
                             a[:, :band].reshape(-1, 3), a[:, -band:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]) / 255.0
    bg_lum = (0.2126 * bg[0] + 0.7152 * bg[1] + 0.0722 * bg[2]) / 255.0
    wgt = smoothstep(bg_lum - 0.28, bg_lum - 0.02, lum)[..., None]
    dark_bg = bg_lum < 0.4
    out = a if (mode == "raw" or dark_bg) else np.clip(a + (paper - bg) * wgt, 0, 255)
    img = Image.fromarray(out.astype(np.uint8))
    if mode == "feather":
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        fx = np.minimum(xx, w - 1 - xx) / (w * 0.07)
        fy = np.minimum(yy, h - 1 - yy) / (h * 0.07)
        alpha = smoothstep(0, 1, np.minimum(fx, fy))
        img = img.convert("RGBA")
        img.putalpha(Image.fromarray((alpha * 255).astype(np.uint8)))
    nh = round(h * width / w)
    img = img.resize((width, nh), Image.LANCZOS)
    img.save(dst, "WEBP", quality=80, method=6)
    print(dst, img.size, "bg was", bg.round().tolist())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4] if len(sys.argv) > 4 else "frame",
         sys.argv[5] if len(sys.argv) > 5 else None)
