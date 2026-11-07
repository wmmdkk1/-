import numpy as np, math, json
from scipy.spatial import cKDTree
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
H0=np.load(W+'head_H0.npy').astype(np.float64)
P9=np.load(W+'part9_final.npy').astype(np.float64)
# source: head-file shoulder top + shirt collar (below neck base, above bust bottom), H0 units
src=H0[(H0[:,2]>=-0.080)&(H0[:,2]<=-0.048)]
src=src[np.linalg.norm(src[:,:2]-np.median(src[:,:2],axis=0),axis=1)<0.20]
# target: body shoulder top + shirt collar (final units)
dst=P9[(P9[:,2]>=0.640)&(P9[:,2]<=0.706)]
dst=dst[np.linalg.norm(dst[:,:2]-np.median(dst[:,:2],axis=0),axis=1)<0.20]
rng=np.random.default_rng(0)
src=src[rng.choice(len(src),min(30000,len(src)),replace=False)]
dst=dst[rng.choice(len(dst),min(30000,len(dst)),replace=False)]
print('src',len(src),'dst',len(dst))
MAXROT=math.radians(10)
def rot_clamp(R,maxang):
    rv=np.array([R[2,1]-R[1,2],R[0,2]-R[2,0],R[1,0]-R[0,1]])
    ang=np.arccos(np.clip((np.trace(R)-1)/2,-1,1))
    if ang<=maxang: return R
    # scale the rotation angle down to maxang (axis-angle via Rodrigues on axis)
    from scipy.spatial.transform import Rotation as Rot
    r=Rot.from_matrix(R).as_rotvec(); n=np.linalg.norm(r)
    return Rot.from_rotvec(r/n*maxang).as_matrix()
def kabsch(X,Y):
    mx,my=X.mean(0),Y.mean(0); C=(Y-my).T@(X-mx); U,D,Vt=np.linalg.svd(C)
    Sg=np.eye(3)
    if np.linalg.det(U@Vt)<0: Sg[2,2]=-1
    R=U@Sg@Vt; return R, my-R@mx
s=np.sqrt(((dst-dst.mean(0))**2).sum(1).mean())/np.sqrt(((src-src.mean(0))**2).sum(1).mean())
s0=s
R=np.eye(3); t=dst.mean(0)-s*src.mean(0)
tree=cKDTree(dst)
for it in range(80):
    X=(s*(R@src.T)).T+t
    d,idx=tree.query(X); keep=d<np.quantile(d,0.7)
    Rk,tk=kabsch(src[keep],dst[idx[keep]])   # rotation/translation for scaled-src -> dst (approx)
    Rk=rot_clamp(Rk,MAXROT*0.25)            # small steps, total clamped below
    Rn=Rk@R
    if np.degrees(np.arccos(np.clip((np.trace(Rn)-1)/2,-1,1)))>10: Rn=rot_clamp(Rn,MAXROT)
    R=Rn
    t=dst[idx[keep]].mean(0)-s*(R@src[keep].T).T.mean(0)
    # update scale clamped to +-6%
    Xs=(R@src[keep].T).T; s_new=((dst[idx[keep]]-dst[idx[keep]].mean(0))*(Xs-Xs.mean(0))).sum()/((Xs-Xs.mean(0))**2).sum()
    s=float(np.clip(s_new,s0*0.6,s0*1.4))
X=(s*(R@src.T)).T+t; d,_=tree.query(X)
ang=math.degrees(math.acos(np.clip((np.trace(R)-1)/2,-1,1)))
print('scale %.4f (init %.4f, ratio %.3f)'%(s,s0,s/s0),'rot total deg %.2f'%ang,'rms(keep70) %.5f median %.5f'%(np.sqrt((d[d<np.quantile(d,0.7)]**2).mean()),np.median(d)))
M=np.eye(4); M[:3,:3]=s*R; M[:3,3]=t
np.save(W+'M7_shoulder.npy',M); print(np.array2string(M,precision=5))
json.dump({'scale':s,'scale_init':s0,'rot_deg':ang,'rms70':float(np.sqrt((d[d<np.quantile(d,0.7)]**2).mean())),'median':float(np.median(d))},open(W+'M7_info.json','w'),indent=1)
