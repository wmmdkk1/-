import bpy, math, numpy as np
from mathutils import Matrix, Vector
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
parts={o.name:o for o in bpy.data.objects if o.type=='MESH'}
def bb(o):
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    return (min(v.x for v in b),min(v.y for v in b),min(v.z for v in b)),(max(v.x for v in b),max(v.y for v in b),max(v.z for v in b))
pm={n:bb(o) for n,o in parts.items()}
feet=Vector(((pm['model_part1'][0][0]+pm['model_part1'][1][0]+pm['model_part3'][0][0]+pm['model_part3'][1][0])/4,(pm['model_part1'][0][1]+pm['model_part1'][1][1]+pm['model_part3'][0][1]+pm['model_part3'][1][1])/4,0.0))
S=(0.90-1.31*0.16+0.015)/pm['model_part9'][1][2]
Rb=Matrix.Rotation(math.radians(90),4,'Z'); fm=Rb@feet
T=Matrix.Translation(-(Vector((S*fm.x,S*fm.y,0.0))))@Matrix.Diagonal((S,S,S,1))@Rb
np.save(W+'part9_final.npy',np.array([(T@v.co)[:] for v in parts['model_part9'].data.vertices],dtype=np.float32))
np.save(W+'part8_final.npy',np.array([(T@v.co)[:] for v in parts['model_part8'].data.vertices],dtype=np.float32))
print('S',S,'P9 done')
