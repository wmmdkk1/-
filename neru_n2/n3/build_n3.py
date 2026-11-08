import bpy, bmesh, math, numpy as np, os
from mathutils import Matrix, Vector
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
OUT=os.environ.get('OUT_BLEND', W+'Neru_n3_v1.blend')
M=Matrix(np.load(W+'M_n3_final.npy').tolist())
B='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/inputs/unzipped_B/Meshy_AI_Crimson_Rebel_20261107_part-segmentation_split.blend'
bpy.ops.wm.open_mainfile(filepath=B)
# n2 stage A transform (same as stage_AB / extract_p9)
parts={o.name:o for o in bpy.data.objects if o.type=='MESH'}
def bb(o):
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    return (min(v.x for v in b),min(v.y for v in b),min(v.z for v in b)),(max(v.x for v in b),max(v.y for v in b),max(v.z for v in b))
pm={n:bb(o) for n,o in parts.items()}
feet=Vector(((pm['model_part1'][0][0]+pm['model_part1'][1][0]+pm['model_part3'][0][0]+pm['model_part3'][1][0])/4,(pm['model_part1'][0][1]+pm['model_part1'][1][1]+pm['model_part3'][0][1]+pm['model_part3'][1][1])/4,0.0))
S=(0.90-1.31*0.16+0.015)/pm['model_part9'][1][2]
Rb=Matrix.Rotation(math.radians(90),4,'Z'); fm=Rb@feet
T_all=Matrix.Translation(-(Vector((S*fm.x,S*fm.y,0.0))))@Matrix.Diagonal((S,S,S,1))@Rb
for n in ['model_part6','model_part7']:
    o=parts[n]; me=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.meshes.remove(me)
for n,o in parts.items():
    if n in ('model_part6','model_part7'): continue
    o.data.transform(T_all); o.matrix_world=Matrix.Identity(4)
# neck column: keep only below the cut (final z 0.705) and within radius 0.03 of the neck axis
NECK=(-0.035,0.0); CUT=0.705
p2=parts['model_part2']
bm=bmesh.new(); bm.from_mesh(p2.data)
kill=[v for v in bm.verts if v.co.z>=CUT or math.hypot(v.co.x-NECK[0],v.co.y-NECK[1])>0.03]
bmesh.ops.delete(bm,geom=kill,context='VERTS')
bm.edges.ensure_lookup_table()
open_edges=[e for e in bm.edges if e.is_boundary]
bmesh.ops.holes_fill(bm,edges=open_edges,sides=0)   # close the cut top end
bm.to_mesh(p2.data); bm.free(); p2.name='Neck_body'
print('NECK verts',len(p2.data.vertices),'removed',len(kill))
# remove old head pieces (part2 was replaced by Neck_body; the rest of the original head is gone)
# new head (FBX parts) -> final frame with fitted matrix
bpy.ops.import_scene.fbx(filepath=W+'../inputs/new_head/Meshy_AI__1108063026_part-segmentation.fbx', automatic_bone_orientation=False)
newobjs=[o for o in bpy.context.selected_objects if o.type=='MESH']
for o in newobjs:
    o.data.transform(M); o.matrix_world=Matrix.Identity(4)
    o.name='NewHead_'+o.name.replace('model_','')
bpy.ops.wm.save_as_mainfile(filepath=OUT,compress=True)
print('N3_SAVED',OUT,[o.name for o in newobjs])
