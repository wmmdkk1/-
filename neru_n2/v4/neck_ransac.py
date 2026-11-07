import numpy as np, json
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
def ransac_circle(Q, rmin=0.008, rmax=0.024, tol=0.0015, iters=3000):
    best=(0,None,None)
    if len(Q)<3: return None
    for _ in range(iters):
        idx=rng.choice(len(Q),3,replace=False)
        c=circle3(Q[idx])
        if c is None: continue
        ctr,r=c
        if not (rmin<=r<=rmax): continue
        d=np.abs(np.linalg.norm(Q-ctr,axis=1)-r)
        n=int((d<tol).sum())
        if n>best[0]: best=(n,ctr,r)
    if best[1] is None: return None
    n,ctr,r=best
    d=np.abs(np.linalg.norm(Q-ctr,axis=1)-r); inl=Q[d<tol]
    # refine by least squares circle on inliers
    A=np.c_[2*inl, np.ones(len(inl))]; b=(inl**2).sum(1)
    sol=np.linalg.lstsq(A,b,rcond=None)[0]; ctr2=sol[:2]; r2=np.sqrt(sol[2]+ctr2@ctr2)
    return ctr2, r2, n
def slice_pts(P,z,dz=0.0015,guess=(0,0),rad=0.06):
    m=np.abs(P[:,2]-z)<dz
    Q=P[m][:,:2]
    q=Q[np.linalg.norm(Q-np.array(guess),axis=1)<rad]
    return q
out={}
def run(name,P,zs,guess):
    out[name]=[]
    for z in zs:
        q=slice_pts(P,z,guess=guess)
        r=ransac_circle(q) if len(q)>20 else None
        if r is None: print(name,'z=%.4f  no circle (n=%d)'%(z,len(q))); continue
        ctr,rad,n=r
        print('%s z=%.4f center=(%+.4f,%+.4f) r=%.4f inliers=%d pts=%d'%(name,z,ctr[0],ctr[1],rad,n,len(q)))
        out[name].append([z,ctr[0],ctr[1],rad,n])
# P2 neck: collar 0.705 -> sample above collar
run('P2',P2,[0.712,0.724,0.736,0.748],(0.0,0.0))
run('H0',H0,[-0.056,-0.046,-0.036,-0.026],(0.0,0.0))
json.dump(out,open(W+'neck_ransac.json','w'),indent=1)
