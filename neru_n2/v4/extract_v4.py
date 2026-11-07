import bpy, math, numpy as np, os
from mathutils import Matrix, Vector
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
# body final frame transform (same as stage_AB.py)
parts={o.name:o for o in bpy.data.objects if o.type=='MESH'}
def bb(o):
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    return (min(v.x for v in b),min(v.y for v in b),min(v.z for v in b)),(max(v.x for v in b),max(v.y for v in b),max(v.z for v in b))
pm={n:bb(o) for n,o in parts.items()}
feet_mid=Vector(((pm['model_part1'][0][0]+pm['model_part1'][1][0]+pm['model_part3'][0][0]+pm['model_part3'][1][0])/4,(pm['model_part1'][0][1]+pm['model_part1'][1][1]+pm['model_part3'][0][1]+pm['model_part3'][1][1])/4,0.0))
shirt_top=pm['model_part9'][1][2]
F=0.16; OV=0.015
S=(0.90-1.31*F+OV)/shirt_top
Rb=Matrix.Rotation(math.radians(90),4,'Z')
fm=Rb@feet_mid
T_all=Matrix.Translation(-(Vector((S*fm.x,S*fm.y,0.0))))@Matrix.Diagonal((S,S,S,1))@Rb
p2=parts['model_part2']
P2=np.array([(T_all@v.co)[:] for v in p2.data.vertices])
np.save(W+'part2_final.npy',P2.astype(np.float32))
# part2 face/neck skin-ish subset not separable; keep all
# head raw world coords
with bpy.data.libraries.load('/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/inputs/unzipped_C/Meshy_AI_Pink_Braid_Dreamer_20261107_model-edit__1_.blend',link=False) as (df,dt):
    dt.objects=['geometry_0','MeshEdit original coordinates']
h=[o for o in bpy.data.objects if o.name=='geometry_0'][0]; e=[o for o in bpy.data.objects if o.name=='MeshEdit original coordinates'][0]
Wh=h.matrix_world.copy()
HR=np.array([(Wh@v.co)[:] for v in h.data.vertices])
H0=HR*F   # final units, rotation 0 (front +X), not yet positioned
np.save(W+'head_H0.npy',H0.astype(np.float32))
print('S',S,'P2 n',len(P2),'H0 n',len(H0))
print('P2 top99.5',np.percentile(P2[:,2],99.5),'H0 top99.5',np.percentile(H0[:,2],99.5))
print('P2 bbox',P2.min(0).round(4),P2.max(0).round(4))
print('H0 bbox',H0.min(0).round(4),H0.max(0).round(4))
