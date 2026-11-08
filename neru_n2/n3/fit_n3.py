import numpy as np, json
from scipy.spatial import cKDTree
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
d=np.load(W+'new_head_raw.npz')
import math
YAW=math.radians(18.0)
R90=np.array([[0,-1,0],[1,0,0],[0,0,1.0]])
RZ=np.array([[math.cos(YAW),-math.sin(YAW),0],[math.sin(YAW),math.cos(YAW),0],[0,0,1.0]])
R90=RZ@R90
src=np.concatenate([d[k] for k in ['model_part0','model_part1','model_part2','model_part3']]).astype(float)
src=(R90@src.T).T
P2=np.load(W+'part2_final.npy').astype(float)
dst=P2[P2[:,2]>=0.705]
rng=np.random.default_rng(3)
S=src[rng.choice(len(src),60000,replace=False)]; D=dst[rng.choice(len(dst),60000,replace=False)]
def kabsch_s(X,Y):
    mx,my=X.mean(0),Y.mean(0); Xc,Yc=X-mx,Y-my
    C=Yc.T@Xc/len(X); U,Sv,Vt=np.linalg.svd(C); Sg=np.eye(3)
    if np.linalg.det(U@Vt)<0: Sg[2,2]=-1
    R=U@Sg@Vt; var=(Xc**2).sum()/len(X); s=(Sv*np.diag(Sg)).sum()/var
    t=my-s*R@mx; M=np.eye(4); M[:3,:3]=s*R; M[:3,3]=t; return M
s0=np.sqrt(((D-D.mean(0))**2).sum(1).mean())/np.sqrt(((S-S.mean(0))**2).sum(1).mean())
M=np.eye(4); M[:3,:3]*=s0; M[:3,3]=D.mean(0)-s0*S.mean(0)
tree=cKDTree(D)
print('init scale %.4f'%s0)
for it in range(60):
    X=(M[:3,:3]@S.T).T+M[:3,3]; dd,idx=tree.query(X); keep=dd<np.quantile(dd,0.7)
    M=kabsch_s(X[keep],D[idx[keep]])@M
    # clamp overall scale to a sane range around the initial estimate
    sc=np.cbrt(abs(np.linalg.det(M[:3,:3])))
    if sc<0.5*s0 or sc>2.0*s0:
        M[:3,:3]*= (np.clip(sc,0.5*s0,2.0*s0)/sc)
X=(M[:3,:3]@S.T).T+M[:3,3]; dd,_=tree.query(X)
sc=np.cbrt(abs(np.linalg.det(M[:3,:3])))
print('final scale %.4f  rms70 %.5f median %.5f'%(sc,np.sqrt((dd[dd<np.quantile(dd,0.7)]**2).mean()),np.median(dd)))
np.save(W+'M_n3_icp.npy',M)
print(np.array2string(M,precision=5))
