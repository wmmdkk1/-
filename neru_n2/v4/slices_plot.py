import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
P2=np.load(W+'part2_final.npy').astype(np.float64)
H0=np.load(W+'head_H0.npy').astype(np.float64)
zp=[0.700,0.712,0.724,0.736,0.748,0.760]
zh=[-0.066,-0.058,-0.050,-0.042,-0.034,-0.026]
fig,ax=plt.subplots(2,6,figsize=(18,6.4))
for i,z in enumerate(zp):
    m=np.abs(P2[:,2]-z)<0.0015; q=P2[m]
    ax[0,i].scatter(q[:,0],q[:,1],s=1,c='k'); ax[0,i].set_aspect('equal'); ax[0,i].set_xlim(-0.15,0.1); ax[0,i].set_ylim(-0.12,0.1); ax[0,i].set_title(f'P2 z={z:.3f} n={len(q)}'); ax[0,i].grid(alpha=.3)
for i,z in enumerate(zh):
    m=np.abs(H0[:,2]-z)<0.0015; q=H0[m]
    ax[1,i].scatter(q[:,0],q[:,1],s=1,c='b'); ax[1,i].set_aspect('equal'); ax[1,i].set_xlim(-0.15,0.1); ax[1,i].set_ylim(-0.12,0.1); ax[1,i].set_title(f'H0 z={z:.3f} n={len(q)}'); ax[1,i].grid(alpha=.3)
plt.tight_layout(); plt.savefig(W+'neck_slices.png',dpi=70); print('ok')
