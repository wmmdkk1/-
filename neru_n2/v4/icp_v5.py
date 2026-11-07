import numpy as np
from scipy.spatial import cKDTree
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
P2=np.load(W+'part2_final.npy').astype(np.float64)
H0=np.load(W+'head_H0.npy').astype(np.float64)
R90=np.eye(4); R90[:3,:3]=np.array([[0,-1,0],[1,0,0],[0,0,1.0]])
H0r=(R90[:3,:3]@H0.T).T
rng=np.random.default_rng(1)
src=H0r[H0r[:,2]>=-0.062]; dst=P2[P2[:,2]>=0.705]
src=src[rng.choice(len(src),40000,replace=False)]; dst=dst[rng.choice(len(dst),40000,replace=False)]
def kabsch(X,Y):
    mx,my=X.mean(0),Y.mean(0); C=(Y-my).T@(X-mx); U,D,Vt=np.linalg.svd(C)
    Sg=np.eye(3)
    if np.linalg.det(U@Vt)<0: Sg[2,2]=-1
    R=U@Sg@Vt; M=np.eye(4); M[:3,:3]=R; M[:3,3]=my-R@mx; return M
s0=np.sqrt(((dst-dst.mean(0))**2).sum(1).mean())/np.sqrt(((src-src.mean(0))**2).sum(1).mean())
M=np.eye(4); M[:3,:3]*=s0; M[:3,3]=dst.mean(0)-s0*src.mean(0)
tree=cKDTree(dst)
for it in range(60):
    X=(M[:3,:3]@src.T).T+M[:3,3]; d,idx=tree.query(X); keep=d<np.quantile(d,0.8)
    M=kabsch(X[keep],dst[idx[keep]])@M
X=(M[:3,:3]@src.T).T+M[:3,3]; d,_=tree.query(X)
print('scale',round(s0,4),'rms80',round(float(np.sqrt((d[d<np.quantile(d,0.8)]**2).mean())),5),'median',round(float(np.median(d)),5))
Mt=M@R90
np.save(W+'icp_M_v5.npy',Mt)
Rr=Mt[:3,:3]; print(np.array2string(Mt,precision=5))
