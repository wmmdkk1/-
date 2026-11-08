import numpy as np, json
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
d=np.load(W+'new_head_raw.npz')
import math
YAW=math.radians(18.0)
R90=np.array([[0,-1,0],[1,0,0],[0,0,1.0]])
RZ=np.array([[math.cos(YAW),-math.sin(YAW),0],[math.sin(YAW),math.cos(YAW),0],[0,0,1.0]])
R_pre=RZ@R90
Rpre4=np.eye(4); Rpre4[:3,:3]=R_pre
new=np.concatenate([d[k] for k in ['model_part0','model_part1','model_part2','model_part3']]).astype(float)
new=(R_pre@new.T).T
M=np.load(W+'M_n3_icp.npy')
Mfull_pre=M@Rpre4
N=(M[:3,:3]@new.T).T+M[:3,3]
P2=np.load(W+'part2_final.npy').astype(float)
NECK=np.array([-0.035,0.0]); NECK_TOP=0.705; EMBED=0.004
u=N[(np.linalg.norm(N[:,:2]-NECK,axis=1)<0.02)]
z_u=u[:,2].min()
dz=(NECK_TOP-EMBED)-z_u
N[:,2]+=dz
M2=M.copy(); M2[2,3]+=dz
np.save(W+'M_n3_final.npy',M2@Rpre4)
def band(P,z0,z1,fn): 
    q=P[(P[:,2]>=z0)&(P[:,2]<=z1)]; return fn(q) if len(q) else np.nan
def ear(P):
    q=P[(P[:,2]>=0.75)&(P[:,2]<=0.78)]
    thr=np.quantile(np.abs(q[:,1]),0.9); e=q[np.abs(q[:,1])>=thr]
    return np.array([np.median(e[:,0]),np.median(e[:,2])])
rows={
 'chin_front_x (z .715-.735, max x)': (band(P2,0.715,0.735,lambda q:q[:,0].max()), band(N,0.715,0.735,lambda q:q[:,0].max())),
 'neck_back_top_x (z .71-.72, min x)': (band(P2,0.71,0.72,lambda q:q[:,0].min()), band(N,0.71,0.72,lambda q:q[:,0].min())),
 'skull_back_x (z .80-.86, min x)': (band(P2,0.80,0.86,lambda q:q[:,0].min()), band(N,0.80,0.86,lambda q:q[:,0].min())),
 'face_midline_y (z .75-.78, median y, front half)': (band(P2[P2[:,0]>-0.02],0.75,0.78,lambda q:np.median(q[:,1])), band(N[N[:,0]>-0.02],0.75,0.78,lambda q:np.median(q[:,1]))),
}
e0=ear(P2); e1=ear(N)
rows['ear_x (side, z .75-.78)']=(e0[0],e1[0])
rows['ear_z (side)']=(e0[1],e1[1])
print('dz applied %.4f  neck embed target %.4f  (underside at neck %.4f)'%(dz,EMBED,z_u))
out={}
for k,(a,b) in rows.items():
    print('%-48s orig %+.4f  new %+.4f  diff %+.4f mm(x1000)'%(k,a,b,(b-a)*1000)); out[k]=[float(a),float(b),float((b-a)*1000)]
print('NEW head top z %.4f ; orig top z %.4f'%(N[:,2].max(),P2[:,2].max()))
print('neck-ear x offset (new) %.4f vs neck centre %.4f'%(e1[0],NECK[0]))
json.dump(out,open(W+'table_n3.json','w'),indent=1)
