import numpy as np, json
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
H0=np.load(W+'head_H0.npy').astype(np.float64); P9=np.load(W+'part9_final.npy').astype(np.float64)
Mv5=np.load(W+'icp_M_v5.npy')
HF=(Mv5[:3,:3]@H0.T).T+Mv5[:3,3]          # head file, v5 placement (final units), before cut
np.save(W+'HF_v5_uncut.npy',HF.astype(np.float32))
def collar_pts(P, xc_guess, name):
    # collar band z 0.675-0.706, near neck x
    m=(P[:,2]>=0.675)&(P[:,2]<=0.706)&(np.abs(P[:,0]-xc_guess)<0.12)
    Q=P[m]
    print(name,'collar band n',len(Q),'x',Q[:,0].min().round(3) if len(Q) else None, Q[:,0].max().round(3) if len(Q) else None,'y',Q[:,1].min().round(3) if len(Q) else None,Q[:,1].max().round(3) if len(Q) else None)
    if len(Q)<50: return None
    L=Q[np.argmax(Q[:,1])]; R=Q[np.argmin(Q[:,1])]
    mid=Q[np.abs(Q[:,1])<0.02]
    B=mid[np.argmin(mid[:,0])]; F=mid[np.argmax(mid[:,0])]
    return dict(L=L.tolist(),R=R.tolist(),B=B.tolist(),F=F.tolist())
lb=collar_pts(P9, -0.03, 'BODY')
lh=collar_pts(HF, -0.03, 'HEAD')
print('BODY',json.dumps(lb)); print('HEAD',json.dumps(lh))
json.dump({'body':lb,'head':lh},open(W+'landmarks_v8.json','w'),indent=1)
