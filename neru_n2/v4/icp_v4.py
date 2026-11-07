import numpy as np, json
from scipy.spatial import cKDTree
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
P2=np.load(W+'part2_final.npy').astype(np.float64)
H0=np.load(W+'head_H0.npy').astype(np.float64)
rng=np.random.default_rng(1)
src=H0[H0[:,2]>=-0.062]; dst=P2[P2[:,2]>=0.705]
src=src[rng.choice(len(src),min(40000,len(src)),replace=False)]
dst=dst[rng.choice(len(dst),min(40000,len(dst)),replace=False)]
print('src',len(src),'dst',len(dst))
def umeyama(X,Y):
    mx,my=X.mean(0),Y.mean(0); Xc,Yc=X-mx,Y-my
    C=Yc.T@Xc/len(X); U,D,Vt=np.linalg.svd(C)
    Sg=np.eye(3); 
    if np.linalg.det(U)*np.linalg.det(Vt)<0: Sg[2,2]=-1
    R=U@Sg@Vt; var=(Xc**2).sum()/len(X)
    s=(D*np.diag(Sg)).sum()/var
    t=my-s*R@mx
    M=np.eye(4); M[:3,:3]=s*R; M[:3,3]=t
    return M
def kabsch(X,Y):
    mx,my=X.mean(0),Y.mean(0); C=(Y-my).T@(X-mx); U,D,Vt=np.linalg.svd(C)
    Sg=np.eye(3)
    if np.linalg.det(U@Vt)<0: Sg[2,2]=-1
    R=U@Sg@Vt; M=np.eye(4); M[:3,:3]=R; M[:3,3]=my-R@mx; return M
s0=np.sqrt(((dst-dst.mean(0))**2).sum(1).mean())/np.sqrt(((src-src.mean(0))**2).sum(1).mean())
print('initial scale from RMS radius',round(s0,4))
M=np.eye(4); M[:3,:3]*=s0; M[:3,3]=dst.mean(0)-s0*src.mean(0)
tree=cKDTree(dst)
for it in range(60):
    Xt=(M[:3,:3]@src.T).T+M[:3,3]
    d,idx=tree.query(Xt)
    keep=d<np.quantile(d,0.8)
    dM=kabsch(Xt[keep],dst[idx[keep]])
    M=dM@M
    if it%10==0 or it==59: print('it',it,'rms80',np.sqrt((d[keep]**2).mean()).round(5),'scale',np.cbrt(abs(np.linalg.det(M[:3,:3]))).round(4))
Xt=(M[:3,:3]@src.T).T+M[:3,3]; d,_=tree.query(Xt)
print('final rms(all)',np.sqrt((d**2).mean()).round(5),'median',np.median(d).round(5))
np.save(W+'icp_M.npy',M)
print('M=\n',np.array2string(M,precision=5))
