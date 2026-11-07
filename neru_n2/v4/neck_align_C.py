import numpy as np, json
from scipy.spatial import cKDTree
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
P2=np.load(W+'part2_final.npy').astype(np.float64)
H0=np.load(W+'head_H0.npy').astype(np.float64)
rng=np.random.default_rng(0)
def circle3(p):
    (x1,y1),(x2,y2),(x3,y3)=p
    d=2*(x1*(y2-y3)+x2*(y3-y1)+x3*(y1-y2))
    if abs(d)<1e-12: return None
    ux=((x1*x1+y1*y1)*(y2-y3)+(x2*x2+y2*y2)*(y3-y1)+(x3*x3+y3*y3)*(y1-y2))/d
    uy=((x1*x1+y1*y1)*(x3-x2)+(x2*x2+y2*y2)*(x1-x3)+(x3*x3+y3*y3)*(x2-x1))/d
    return np.array([ux,uy]), np.hypot(x1-ux,y1-uy)
def fit_ring(Q,guess,rmin,rmax,tol=0.0012,iters=4000):
    Q=Q[np.linalg.norm(Q-guess,axis=1)<rmax+0.02]
    if len(Q)<30: return None
    best=(0,None,None)
    for _ in range(iters):
        idx=rng.choice(len(Q),3,replace=False); c=circle3(Q[idx])
        if c is None: continue
        ctr,r=c
        if not (rmin<=r<=rmax) or np.linalg.norm(ctr-guess)>0.03: continue
        n=int((np.abs(np.linalg.norm(Q-ctr,axis=1)-r)<tol).sum())
        if n>best[0]: best=(n,ctr,r)
    if best[1] is None: return None
    n,ctr,r=best; inl=Q[np.abs(np.linalg.norm(Q-ctr,axis=1)-r)<tol]
    A=np.c_[2*inl,np.ones(len(inl))]; b=(inl**2).sum(1)
    s=np.linalg.lstsq(A,b,rcond=None)[0]; c2=s[:2]; r2=np.sqrt(s[2]+c2@c2)
    return c2,r2,n
def sl(P,z,dz=0.0012): return P[np.abs(P[:,2]-z)<dz][:,:2]
# P2 neck: heights above collar (0.705)
zP=[0.712,0.718,0.724,0.730,0.736]; gP=np.array([-0.03,0.0])
# H0 heights mapped with collar at -0.061 (raw -0.38*0.16) -> same offsets above collar
zH=[-0.061+(z-0.705) for z in zP]; gH=np.array([0.0,0.0])
cP=[];cH=[]
for z in zP:
    r=fit_ring(sl(P2,z),gP,0.010,0.024); 
    if r: cP.append([z,*r[0],r[1],r[2]]); print('P2 z=%.3f c=(%+.4f,%+.4f) r=%.4f n=%d'%(z,*r[0],r[1],r[2]))
for z in zH:
    r=fit_ring(sl(H0,z),gH,0.010,0.022)
    if r: cH.append([z,*r[0],r[1],r[2]]); print('H0 z=%.3f c=(%+.4f,%+.4f) r=%.4f n=%d'%(z,*r[0],r[1],r[2]))
cP=np.array(cP); cH=np.array(cH)
def axis(c):
    # line x(z), y(z) by least squares
    A=np.c_[np.ones(len(c)),c[:,0]]; bx=np.linalg.lstsq(A,c[:,1],rcond=None)[0]
    A2=np.c_[np.ones(len(c)),c[:,0]]; by=np.linalg.lstsq(A2,c[:,2],rcond=None)[0]
    return bx,by  # slopes dx/dz, dy/dz
sP=axis(np.c_[cP[:,0],cP[:,1],cP[:,2]]) if len(cP)>=3 else None
# generic: fit centre as function of z
def fitline(c):
    z=c[:,0]; x=c[:,1]; y=c[:,2]
    px=np.polyfit(z,x,1); py=np.polyfit(z,y,1); return px,py
pP=fitline(cP); pH=fitline(cH)
print('P2 neck axis: dx/dz=%.3f dy/dz=%.3f  x0(z)=%.4f y0(z)=%.4f'%(pP[0][0],pP[1][0],pP[0][1],pP[1][1]))
print('H0 neck axis: dx/dz=%.3f dy/dz=%.3f  x0(z)=%.4f y0(z)=%.4f'%(pH[0][0],pH[1][0],pH[0][1],pH[1][1]))
json.dump({'P2':cP.tolist(),'H0':cH.tolist()},open(W+'neckC_centers.json','w'),indent=1)
np.save(W+'neckC_pP.npy',np.array([pP[0],pP[1]])); np.save(W+'neckC_pH.npy',np.array([pH[0],pH[1]]))
