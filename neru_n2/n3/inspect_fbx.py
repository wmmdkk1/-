import bpy, numpy as np
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/inputs/new_head/Meshy_AI__1108063026_part-segmentation.fbx', automatic_bone_orientation=False)
print('UNITS', bpy.context.scene.unit_settings.scale_length)
tot=0
for o in sorted(bpy.data.objects,key=lambda x:x.name):
    if o.type=='MESH':
        me=o.data
        P=np.array([(o.matrix_world@v.co)[:] for v in me.vertices]) if len(me.vertices) else np.zeros((0,3))
        tris=sum(len(p.vertices)-2 for p in me.polygons); tot+=tris
        if len(P):
            print('MESH',o.name,'V',len(P),'tris',tris,'min',P.min(0).round(4).tolist(),'max',P.max(0).round(4).tolist(),'scale',tuple(round(s,4) for s in o.scale),'rot',tuple(round(r,3) for r in o.rotation_euler),'parent',o.parent.name if o.parent else None)
    else:
        print('OBJ',o.type,o.name,'parent',o.parent.name if o.parent else None,'scale',tuple(round(s,4) for s in o.scale))
print('TOTAL_TRIS',tot)
