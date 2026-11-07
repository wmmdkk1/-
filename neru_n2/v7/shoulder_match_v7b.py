import numpy as np, json
from scipy.spatial import cKDTree
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
H0=np.load(W+'head_H0.npy').astype(np.float64); P9=np.load(W+'part9_final.npy').astype(np.float64)
src=H0[(H0[:,2]>=-0.080)&(H0[:,2]<=-0.048)]; src=src[np.linalg.norm(src[:,:2]-np.median(src[:,:2],0),axis=1)<0.20]
dst=P9[(P9[:,2]>=0.640)&(P9[:,2]<=0.706)]; dst=dst[np.linalg.norm(dst[:,:2]-np.median(dst[:,:2],0),axis=1)<0.20]
rng=np.random.default_rng(0); src=src[rng.choice(len(src),min(30000,len(src)),replace=False)]; dst=dst[rng.choice(len(dst),min(30000,len(dst)),replace=False)]
tree=cKDTree(dst)
# rotation fixed to identity (rigid tilt not allowed); fit scale + translation by ICP
s=1.0; t=dst.mean(0)-src.mean(0)
for it in range(60):
    X=s*src+t; d,idx=tree.query(X); keep=d<np.quantile(d,0.7)
    A=src[keep]; B=dst[idx[keep]]
    am,bm=A.mean(0),B.mean(0)
    s=float(((B-bm)*(A-am)).sum()/((A-am)**2).sum())
    t=bm-s*am
X=s*src+t; d,_=tree.query(X)
print('scale %.4f'%s,'rms70 %.5f median %.5f'%(np.sqrt((d[d<np.quantile(d,0.7)]**2).mean()),np.median(d)))
M=np.eye(4); M[:3,:3]=s*np.eye(3); M[:3,3]=t
np.save(W+'M7_shoulder.npy',M); print(np.array2string(M,precision=5))
json.dump({'scale':s,'rot_deg':0.0,'rms70':float(np.sqrt((d[d<np.quantile(d,0.7)]**2).mean())),'median':float(np.median(d))},open(W+'M7_info.json','w'),indent=1)
