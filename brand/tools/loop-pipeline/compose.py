# Composite a loop over its sharp still: static areas come from the still, the
# moving areas (found from per-pixel temporal std) from the video.
# usage: compose.py SRC STILL OUT OW OH NAME [--decode FILTER] [--blur MASKPNG SIGMA] [--thr 1.5] [--grow 15]
import sys, subprocess, argparse, numpy as np, cv2
ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('still'); ap.add_argument('out'); ap.add_argument('ow', type=int); ap.add_argument('oh', type=int); ap.add_argument('name')
ap.add_argument('--decode', default='format=rgb24')
ap.add_argument('--blur', nargs=2, default=None)
ap.add_argument('--thr', type=float, default=1.5)
ap.add_argument('--grow', type=int, default=15)
ap.add_argument('--feather', type=float, default=7)
ap.add_argument('--sharpen', type=float, default=-1)
ap.add_argument('--keep', default=None, help='extra mask png (white = video) added to the motion mask')
ap.add_argument('--only', default=None, help='normalised boxes x0,y0,x1,y1;... outside which the still wins (Kling wobble)')
a = ap.parse_args()
w, h = map(int, subprocess.run(['ffprobe','-v','error','-show_entries','stream=width,height','-of','csv=p=0',a.src],capture_output=True,text=True).stdout.strip().split(','))
def read_frames():
  p = subprocess.Popen(['ffmpeg','-v','error','-i',a.src,'-vf',a.decode,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
  n = w*h*3
  while True:
    b = p.stdout.read(n)
    if len(b) < n: break
    yield np.frombuffer(b,np.uint8).reshape(h,w,3)
  p.wait()
# 1. motion map at quarter size
lw, lh = w//4, h//4
small = []; f0 = None
for i, f in enumerate(read_frames()):
  if i == 0: f0 = f.copy()
  small.append(cv2.resize(cv2.cvtColor(f, cv2.COLOR_RGB2GRAY), (lw, lh), interpolation=cv2.INTER_AREA).astype(np.float32))
N = len(small); st = np.stack(small).std(0)
print(a.name, 'frames', N, 'std pct 50/90/99/max', [round(float(np.percentile(st,q)),2) for q in (50,90,99)], round(float(st.max()),2))
binm = (st > a.thr).astype(np.uint8)
binm = cv2.morphologyEx(binm, cv2.MORPH_OPEN, np.ones((2,2),np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(binm)
keep = np.zeros_like(binm)
for k in range(1, n):
  if stats[k, cv2.CC_STAT_AREA] >= 12: keep[lab == k] = 1
keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
keep = cv2.dilate(keep, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*a.grow+1,2*a.grow+1)))
mlow = cv2.GaussianBlur(keep.astype(np.float32), (0,0), a.feather)
mlow = np.clip(mlow*1.25, 0, 1)
print(a.name, 'mask coverage %.1f%%' % (100*mlow.mean()))
# 2. geometry: still (stretched to video size) vs frame 0
still = cv2.cvtColor(cv2.imread(a.still, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
sv = cv2.resize(still, (w, h), interpolation=cv2.INTER_AREA)
g = lambda im: cv2.cvtColor(im, cv2.COLOR_RGB2GRAY).astype(np.float32)/255
_, R = cv2.findTransformECC(g(f0), g(sv), np.eye(2,3,dtype=np.float32), cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,300,1e-8), None, 5)
R3 = np.vstack([R,[0,0,1]]).astype(np.float64); T = np.diag([a.ow/w, a.oh/h, 1.0])
M = (T @ R3)[:2]          # video px -> output px
print(a.name, 'R', np.round(R,5).tolist())
so = cv2.resize(still, (a.ow, a.oh), interpolation=cv2.INTER_AREA if a.ow < still.shape[1] else cv2.INTER_LANCZOS4).astype(np.float32)
mo = cv2.warpAffine(cv2.resize(mlow, (w, h), interpolation=cv2.INTER_LINEAR), M, (a.ow, a.oh), flags=cv2.INTER_LINEAR)
if a.keep:
  extra = cv2.imread(a.keep, cv2.IMREAD_GRAYSCALE).astype(np.float32)/255
  mo = np.maximum(mo, cv2.resize(extra, (a.ow, a.oh), interpolation=cv2.INTER_LINEAR))
if a.only:
  box = np.zeros((a.oh, a.ow), np.float32)
  for b in a.only.split(';'):
    x0,y0,x1,y1 = [float(t) for t in b.split(',')]
    box[int(y0*a.oh):int(y1*a.oh), int(x0*a.ow):int(x1*a.ow)] = 1
  mo = mo * cv2.GaussianBlur(box, (0,0), a.ow/60)
  print(a.name, 'mask coverage after --only %.1f%%' % (100*mo.mean()))
mo3 = mo[...,None]
warp = lambda f: cv2.warpAffine(f, M, (a.ow, a.oh), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
v0 = warp(f0)
core = mo > 0.5
off = (so[core] - v0[core]).mean(0) if core.any() else np.zeros(3)
print(a.name, 'colour offset', np.round(off,2).tolist())
lap = lambda im: float(cv2.Laplacian(cv2.cvtColor(np.clip(im,0,255).astype(np.uint8), cv2.COLOR_RGB2GRAY), cv2.CV_32F)[core].var()) if core.any() else 0
def sharpen(im, amt): return im + amt*(im - cv2.GaussianBlur(im, (0,0), 1.2)) if amt > 0 else im
target = lap(so); amt = a.sharpen
if amt < 0:
  best = min([0, .25, .5, .75, 1.0], key=lambda k: abs(lap(sharpen(v0+off, k)) - target))
  amt = best
print(a.name, 'lapvar still %.1f video %.1f -> sharpen %.2f -> %.1f' % (target, lap(v0+off), amt, lap(sharpen(v0+off, amt))))
blur = None
if a.blur:
  bm = cv2.imread(a.blur[0], cv2.IMREAD_GRAYSCALE).astype(np.float32)/255
  blur = (cv2.resize(bm, (a.ow, a.oh), interpolation=cv2.INTER_LINEAR)[...,None], float(a.blur[1]))
enc = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{a.ow}x{a.oh}','-r','30','-i','-','-c:v','ffv1','-level','3','-pix_fmt','gbrp',a.out], stdin=subprocess.PIPE)
for i, f in enumerate(read_frames()):
  v = sharpen(warp(f) + off, amt)
  o = so*(1-mo3) + v*mo3
  if blur is not None:
    o = o*(1-blur[0]) + cv2.GaussianBlur(o, (0,0), blur[1])*blur[0]
  o = np.clip(np.rint(o), 0, 255).astype(np.uint8)
  if i == 0: cv2.imwrite(a.out.rsplit('.',1)[0]+'_f0.png', cv2.cvtColor(o, cv2.COLOR_RGB2BGR))
  enc.stdin.write(o.tobytes())
enc.stdin.close(); enc.wait()
cv2.imwrite(a.out.rsplit('.',1)[0]+'_mask.png', (mo*255).astype(np.uint8))
print(a.name, 'written', a.out)
