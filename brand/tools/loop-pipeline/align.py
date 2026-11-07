import sys, subprocess, numpy as np, cv2
still_path, video, outw = sys.argv[1], sys.argv[2], None
def frames(path, idxs, w, h):
  sel='+'.join(f'eq(n\\,{i})' for i in idxs)
  raw=subprocess.run(['ffmpeg','-v','error','-i',path,'-vf',f"select='{sel}',scale=in_color_matrix=bt709:in_range=tv,format=rgb24",'-vsync','0','-f','rawvideo','-'],capture_output=True).stdout
  return np.frombuffer(raw,np.uint8).reshape(-1,h,w,3)
w,h=map(int,subprocess.run(['ffprobe','-v','error','-show_entries','stream=width,height','-of','csv=p=0',video],capture_output=True,text=True).stdout.strip().split(','))
st=cv2.cvtColor(cv2.imread(still_path,cv2.IMREAD_COLOR),cv2.COLOR_BGR2RGB)
sh,sw=st.shape[:2]
print('still',sw,sh,'video',w,h)
fr=frames(video,[0,48,96,144,191],w,h)
# initial guess: scale still to video width (stretch both axes to fill)
g=lambda a: cv2.cvtColor(a,cv2.COLOR_RGB2GRAY).astype(np.float32)/255
f0=g(fr[0])
def ecc(src_img, dst, init):
  warp=init.astype(np.float32).copy()
  crit=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,200,1e-7)
  cc,warp=cv2.findTransformECC(dst,src_img,warp,cv2.MOTION_AFFINE,crit,None,5)
  return cc,warp
# map still->video coords: x_v = a*x_s + ..., find with ECC on downscaled still warped
init=np.array([[w/sw,0,0],[0,h/sh,0]],np.float32)
# ECC requires same size: warp still into video frame with init, then refine residual affine
st_g=g(st)
cc,warp=cv2.findTransformECC(f0, cv2.warpAffine(st_g,init,(w,h),flags=cv2.INTER_AREA), np.eye(2,3,dtype=np.float32), cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,300,1e-8),None,5)
print('still->frame0 residual affine (on top of stretch):',np.round(warp,5).tolist(),'cc',round(cc,5))
for i,f in zip([48,96,144,191],fr[1:]):
  cc2,w2=cv2.findTransformECC(f0,g(f),np.eye(2,3,dtype=np.float32),cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,200,1e-7),None,5)
  print('frame',i,'vs 0 affine',np.round(w2,4).tolist(),'cc',round(cc2,5))
