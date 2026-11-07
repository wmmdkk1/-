import numpy as np, sys
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
P2=np.load(W+'part2_final.npy').astype(np.float64)
def stats(P,name):
    def band(z0,z1): return P[(P[:,2]>=z0)&(P[:,2]<z1)]
    j=band(0.715,0.74); n=band(0.72,0.74); sk=band(0.80,0.86); top=P[P[:,2]>0.88]
    print(f"{name:10s} jaw(z.715-.74) xmax={j[:,0].max():+.4f} | neck(z.72-.74) xmax={n[:,0].max():+.4f} xmin={n[:,0].min():+.4f} ymin={n[:,1].min():+.4f} ymax={n[:,1].max():+.4f} | skull(z.80-.86) xmin={sk[:,0].min():+.4f} xmax={sk[:,0].max():+.4f} | top zmax={P[:,2].max():.4f}")
stats(P2,'P2(orig)')
for f in sys.argv[1:]:
    stats(np.load(W+f).astype(np.float64), f)
