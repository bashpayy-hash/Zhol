# raw Kling clip -> seamless 30 fps master at native size (ffv1 gbrp)
# usage: prep.py IN OUT [K=16]
import sys, subprocess, numpy as np
src, out = sys.argv[1], sys.argv[2]; K = int(sys.argv[3]) if len(sys.argv) > 3 else 16
w, h = map(int, subprocess.run(['ffprobe','-v','error','-show_entries','stream=width,height','-of','csv=p=0',src],capture_output=True,text=True).stdout.strip().split(','))
raw = subprocess.run(['ffmpeg','-v','error','-i',src,'-vf','scale=in_color_matrix=bt709:in_range=tv,format=rgb24','-f','rawvideo','-'],capture_output=True).stdout
fr = np.frombuffer(raw,np.uint8).reshape(-1,h,w,3)
fr = fr[:-1]                       # last frame duplicates the first (start = end frame)
N = len(fr); first = fr[0].astype(np.float32)
M = N*30//24
filt = ("settb=1/24,setpts=N,scale=out_color_matrix=bt709:out_range=pc,format=yuv444p,hqdn3d=0:0:3:3,"
        "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
        f"trim=end_frame={M},scale=in_color_matrix=bt709:in_range=pc,format=gbrp")
p = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r','24','-i','-','-vf',filt,'-c:v','ffv1','-level','3',out],stdin=subprocess.PIPE)
T = N-K
for i in range(N):
  f = fr[i]
  if i >= T:
    wgt = (i-T+1)/(K+1)
    f = np.clip(np.rint(f.astype(np.float32) + (first - f.astype(np.float32))*wgt),0,255).astype(np.uint8)
  p.stdin.write(f.tobytes())
p.stdin.write(fr[0].tobytes()); p.stdin.write(fr[1].tobytes())   # wrap: interpolate last -> first too (+1 lookahead)
p.stdin.close(); p.wait()
print(out, 'frames', M, 'from', N)
