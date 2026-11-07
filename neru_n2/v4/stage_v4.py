# v4: rebuild from originals: body (A) + head aligned to original part2 by ICP (M), cut at collar overlap
import bpy, bmesh, math, numpy as np, os, json
from mathutils import Matrix, Vector
HEAD=os.environ['HEAD_BLEND']; OUT=os.environ['OUT_BLEND']; LOG=os.environ['LOG_JSON']; MP=os.environ['M_NPY']
M=np.load(MP)
log={}
parts={o.name:o for o in bpy.data.objects if o.type=='MESH'}
def bb(o):
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    return (min(v.x for v in b),min(v.y for v in b),min(v.z for v in b)),(max(v.x for v in b),max(v.y for v in b),max(v.z for v in b))
pm={n:bb(o) for n,o in parts.items()}
feet_mid=Vector(((pm['model_part1'][0][0]+pm['model_part1'][1][0]+pm['model_part3'][0][0]+pm['model_part3'][1][0])/4,(pm['model_part1'][0][1]+pm['model_part1'][1][1]+pm['model_part3'][0][1]+pm['model_part3'][1][1])/4,0.0))
shirt_top=pm['model_part9'][1][2]
F=0.16; OV=0.015
S=(0.90-1.31*F+OV)/shirt_top
Rb=Matrix.Rotation(math.radians(90),4,'Z'); fm=Rb@feet_mid
T_all=Matrix.Translation(-(Vector((S*fm.x,S*fm.y,0.0))))@Matrix.Diagonal((S,S,S,1))@Rb
# remove head + halo pieces
for n in ['model_part2','model_part6','model_part7']:
    o=bpy.data.objects[n]; me=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.meshes.remove(me)
# load head
with bpy.data.libraries.load(HEAD,link=False) as (df,dt):
    dt.objects=['geometry_0','MeshEdit original coordinates']
h=[o for o in bpy.data.objects if o.name=='geometry_0'][0]; e=[o for o in bpy.data.objects if o.name=='MeshEdit original coordinates'][0]
Wh=h.matrix_world.copy(); h.parent=None; h.matrix_world=Matrix.Identity(4); h.data.transform(Wh)
bpy.data.objects.remove(e,do_unlink=True); h.name='Head_new_PinkBraid'
bpy.context.scene.collection.objects.link(h)
# head -> H0 (final units, front +X), then ICP matrix
h.data.transform(Matrix.Diagonal((F,F,F,1)))
h.data.transform(Matrix(M.tolist()))
# cut below collar overlap (final z)
cut=shirt_top*S-OV
bm=bmesh.new(); bm.from_mesh(h.data)
kill=[v for v in bm.verts if v.co.z<cut]
bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(h.data); bm.free(); h.data.update()
log['cut_final']=cut; log['cut_removed']=len(kill); log['S']=S; log['M']=M.tolist()
# body transform
for o in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('model_part')]:
    o.data.transform(T_all); o.matrix_world=Matrix.Identity(4)
bpy.context.view_layer.update()
log['objects']={o.name:{'V':len(o.data.vertices),'tris':sum(len(p.vertices)-2 for p in o.data.polygons)} for o in bpy.data.objects if o.type=='MESH'}
bpy.ops.wm.save_as_mainfile(filepath=OUT,compress=True)
json.dump(log,open(LOG,'w'),indent=1,default=float)
print('STAGE_V4_DONE')
