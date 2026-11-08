import bpy, math, numpy as np, os
from mathutils import Matrix, Vector
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
# ---- new head (FBX), world coords as imported
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=W+'../inputs/new_head/Meshy_AI__1108063026_part-segmentation.fbx', automatic_bone_orientation=False)
out={}
for o in bpy.data.objects:
    if o.type=='MESH':
        out[o.name]=np.array([(o.matrix_world@v.co)[:] for v in o.data.vertices],dtype=np.float32)
        print('NEW',o.name,len(o.data.vertices), tuple(round(s,3) for s in o.scale), tuple(round(r,3) for r in o.rotation_euler))
np.savez(W+'new_head_raw.npz', **out)
print('NEWDONE')
