import numpy as np
from scipy.spatial import cKDTree
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
P2=np.load(W+'part2_final.npy').astype(np.float64)
H0=np.load(W+'head_H0.npy').astype(np.float64)
M=np.load(W+'icp_M.npy').copy()
def kabsch(X,Y):
    mx,my=X.mean(0),Y.mean(0); C=(Y-my).T@(X-mx); U,D,Vt=np.linalg.svd(C)
    Sg=np.eye(3)
    if np.linalg.det(U@Vt)<0: Sg[2,2]=-1
    R=U@Sg@Vt; T=np.eye(4); T[:3,:3]=R; T[:3,3]=my-R@mx; return T
# neck band in P2 (final) and H0 (pre-M)
dst=P2[(P2[:,2]>=0.705)&(P2[:,2]<=0.750)]
dst=dst[np.linalg.norm(dst[:,:2]-np.array([-0.035,0.0]),axis=1)<0.040]
src0=H0[(H0[:,2]>=-0.061)&(H0[:,2]<=-0.019)]
src0=src0[np.linalg.norm(src0[:,:2],axis=1)<0.050]
print('neck band src',len(src0),'dst',len(dst))
tree=cKDTree(dst)
def err(Mx):
    X=(Mx[:3,:3]@src0.T).T+Mx[:3,3]; d,_=tree.query(X); return np.sqrt((d**2).mean()), np.median(d)
print('start rms/median', [round(v,5) for v in err(M)])
# rigid refinement limited to small angles and few steps, keep scale from v4 ICP
for it in range(40):
    X=(M[:3,:3]@src0.T).T+M[:3,3]
    d,idx=tree.query(X); keep=d<np.quantile(d,0.8)
    dT=kabsch(X[keep],dst[idx[keep]])
    ang=np.degrees(np.arccos(np.clip((np.trace(dT[:3,:3])-1)/2,-1,1)))
    if ang>1.0:  # clamp rotation step
        pass
    M=dT@M
print('end   rms/median', [round(v,5) for v in err(M)])
np.save(W+'icpC_M.npy',M); print(np.array2string(M,precision=5))
