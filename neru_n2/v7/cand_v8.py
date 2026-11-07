import numpy as np, json, math
from scipy.optimize import least_squares
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
lm=json.load(open(W+'landmarks_v8.json')); LB=lm['body']; LH=lm['head']
keys=['L','R','B','F']
hp=np.array([LH[k] for k in keys]); bp=np.array([LB[k] for k in keys])
pivot=np.array([(LH['B'][0]+LH['F'][0])/2, 0.0, (LH['B'][2]+LH['F'][2])/2])
def Ry(th):
    c,s=math.cos(th),math.sin(th); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def xform(p,th,dx,dz):
    # rotate about Y through pivot, then translate in x,z only (y fixed)
    q=(Ry(th)@(p-pivot).T).T+pivot
    q[:,0]+=dx; q[:,2]+=dz; return q
def resid(v):
    th,dx,dz=v
    q=xform(hp,th,dx,dz)
    # only x,z residuals (left-right kept from v5)
    return (q[:,[0,2]]-bp[:,[0,2]]).ravel()
sol=least_squares(resid,[0,0,0])
th0,dx0,dz0=sol.x
print('fit: tilt %.2f deg, dx %.4f, dz %.4f, rms_xz %.4f'%(math.degrees(th0),dx0,dz0,np.sqrt((sol.fun**2).mean())))
q=xform(hp,th0,dx0,dz0)
for k,a,b in zip(keys,q,bp): print(k,'head->',np.round(a,4),'body',np.round(b,4),'err_xz %.4f'%np.hypot(a[0]-b[0],a[2]-b[2]))
# candidates
cands=[]
for ddx in [-0.008,0,0.008]:
    for dth in [-6,0,6]:
        cands.append(dict(name=f'dx{ddx*1000:+.0f}mm_tilt{dth:+d}deg', th=th0+math.radians(dth), dx=dx0+ddx, dz=dz0))
# transform matrices for head (final frame, pivot-based)
out=[]
for c in cands:
    th,dx,dz=c['th'],c['dx'],c['dz']
    Rm=Ry(th); t=pivot-Rm@pivot+np.array([dx,0,dz])
    M=np.eye(4); M[:3,:3]=Rm; M[:3,3]=t
    out.append(dict(name=c['name'],M=M.tolist()))
json.dump(out,open(W+'cands_v8.json','w'),indent=1)
json.dump({'th0':th0,'dx0':dx0,'dz0':dz0,'pivot':pivot.tolist()},open(W+'fit_v8.json','w'),indent=1)
print('candidates',[c['name'] for c in cands])
