# Stage A (orientation/scale) + Stage B (head swap). Runs in Blender 4.4 background.
import bpy, bmesh, math, numpy as np, sys, os, json
from mathutils import Matrix, Vector
HEAD = os.environ['HEAD_BLEND']
OUT = os.environ['OUT_BLEND']
LOG = os.environ['LOG_JSON']
log = {}

def mesh_objs(): return [o for o in bpy.data.objects if o.type=='MESH']
def raw_bbox(o):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    return (min(v.x for v in bb),min(v.y for v in bb),min(v.z for v in bb)),(max(v.x for v in bb),max(v.y for v in bb),max(v.z for v in bb))

# ---- body raw measurements
parts = {o.name:o for o in mesh_objs()}
pm = {n: raw_bbox(o) for n,o in parts.items()}
feet_mid = Vector(( (pm['model_part1'][0][0]+pm['model_part1'][1][0]+pm['model_part3'][0][0]+pm['model_part3'][1][0])/4,
                    (pm['model_part1'][0][1]+pm['model_part1'][1][1]+pm['model_part3'][0][1]+pm['model_part3'][1][1])/4, 0.0))
shirt_top_raw = pm['model_part9'][1][2]
log['body_raw'] = {'feet_mid':tuple(feet_mid), 'shirt_top_raw':shirt_top_raw,
                   'part2_center':(0.0,0.0), 'parts_zmax':{n:pm[n][1][2] for n in pm}}

# ---- final scale design (see report): head top = 0.90 final, overlap 1.5 cm below shirt top
F_HEAD = 0.16           # final units per raw head unit
OVERLAP_FINAL = 0.015
S = (0.90 - 1.31*F_HEAD + OVERLAP_FINAL) / shirt_top_raw   # body raw -> final
log['S'] = S; log['F_HEAD']=F_HEAD
s_head_raw = F_HEAD / S

# ---- remove old head (part2) + broken halo pieces (part6, part7)
for n in ['model_part2','model_part6','model_part7']:
    o = bpy.data.objects[n]
    me = o.data
    bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.meshes.remove(me)
log['removed'] = ['model_part2','model_part6','model_part7']

# ---- load replacement head geometry (apply its parent scale)
with bpy.data.libraries.load(HEAD, link=False) as (df, dt):
    dt.objects = ['geometry_0','MeshEdit original coordinates']
for o in dt.objects if False else []: pass
head = None; empty = None
for o in bpy.data.objects:
    if o.name=='geometry_0' and o.type=='MESH': head=o
    if o.name=='MeshEdit original coordinates': empty=o
if head is None: raise SystemExit('no head')
head.name = 'Head_new_PinkBraid'
# world transform of head (includes empty parent)
Wh = head.matrix_world.copy()
head.parent = None
head.matrix_world = Matrix.Identity(4)
head.data.transform(Wh)
if empty is not None:
    bpy.data.objects.remove(empty, do_unlink=True)
for c in bpy.context.scene.collection.objects:
    pass
bpy.context.scene.collection.objects.link(head)

# head raw measurements (after world transform)
co = np.array([v.co[:] for v in head.data.vertices], dtype=np.float64)
log['head_raw'] = {'n':len(co), 'min':co.min(0).tolist(), 'max':co.max(0).tolist()}

# rotate +90 about Z (front -Y -> +X), scale s_head_raw
HEAD_ROT = math.radians(float(os.environ.get('HEAD_ROT_DEG','90')))
def RotZ90(p):
    c,sn=math.cos(HEAD_ROT),math.sin(HEAD_ROT)
    return np.stack([p[:,0]*c-p[:,1]*sn, p[:,0]*sn+p[:,1]*c, p[:,2]],1)
c2 = RotZ90(co)*s_head_raw
# neck centre (pre-scale band z in [-0.34,-0.30] raw, central |x|<0.2)
band = (co[:,2]>-0.34)&(co[:,2]<-0.30)&(np.abs(co[:,0])<0.2)&(np.abs(co[:,1])<0.3)
nc = RotZ90(co[band]).mean(0)*s_head_raw if band.sum()>0 else np.zeros(3)
top_post = c2[:,2].max()
target_top = 0.90/S
tx, ty = -nc[0], -nc[1]
tz = target_top - top_post
log['head_place'] = {'neck_center_post':nc.tolist(),'top_post':float(top_post),'target_top_raw':target_top,
                     'shift':[tx,ty,tz], 'band_n':int(band.sum())}
M_head = Matrix.Translation((tx,ty,tz)) @ Matrix.Diagonal((s_head_raw,s_head_raw,s_head_raw,1)) @ Matrix.Rotation(HEAD_ROT,4,'Z')
head.data.transform(M_head)
head.matrix_world = Matrix.Identity(4)

# cut neck: remove everything below the cut plane (raw z = shirt_top_raw - overlap)
cut_raw = shirt_top_raw - OVERLAP_FINAL/S
bm = bmesh.new(); bm.from_mesh(head.data)
kill = [v for v in bm.verts if v.co.z < cut_raw]
bmesh.ops.delete(bm, geom=kill, context='VERTS')
bm.to_mesh(head.data); bm.free(); head.data.update()
log['head_cut'] = {'cut_raw':cut_raw, 'removed_verts':len(kill)}

# ---- body-wide transform: rotate, scale S, feet midpoint -> origin
Rb = Matrix.Rotation(math.radians(90),4,'Z')
fm = Rb @ feet_mid
T_all = Matrix.Translation(-(Vector((S*fm.x, S*fm.y, 0.0)))) @ Matrix.Diagonal((S,S,S,1)) @ Rb
for o in mesh_objs():
    o.data.transform(T_all)
    o.matrix_world = Matrix.Identity(4)
bpy.context.view_layer.update()
# measure
allb = [raw_bbox(o) for o in mesh_objs()]
mn = (min(b[0][0] for b in allb),min(b[0][1] for b in allb),min(b[0][2] for b in allb))
mx = (max(b[1][0] for b in allb),max(b[1][1] for b in allb),max(b[1][2] for b in allb))
log['final_bbox'] = {'min':mn,'max':mx,'height':mx[2]-mn[2]}
log['objects'] = {o.name: {'V':len(o.data.vertices),'tris':sum(len(p.vertices)-2 for p in o.data.polygons),
                          'bbox_min':[round(x,4) for x in raw_bbox(o)[0]],'bbox_max':[round(x,4) for x in raw_bbox(o)[1]]} for o in mesh_objs()}
# ---- align neck to shirt collar opening (final coords)
def _arr(o): return np.array([v.co[:] for v in o.data.vertices],dtype=np.float64)
_h = head.data; _hv = np.array([v.co[:] for v in _h.vertices],dtype=np.float64)
_sv = _arr(parts['model_part9'])
_sv = np.array([ (T_all @ Vector(v))[:] for v in _sv ]) if False else None
_s_obj = bpy.data.objects['model_part9']; _sf = np.array([v.co[:] for v in _s_obj.data.vertices],dtype=np.float64)
mS = (_sf[:,2]>0.68)&(_sf[:,2]<0.71)
shirt_c = np.median(_sf[mS,:2],axis=0)
mH = (_hv[:,2]>0.695)&(_hv[:,2]<0.715)
neck_c = np.median(_hv[mH,:2],axis=0)
dxy = shirt_c - neck_c
head.data.transform(Matrix.Translation((float(dxy[0]),float(dxy[1]),0.0)))
log['neck_align'] = {'shirt_collar_center':shirt_c.tolist(),'neck_center_before':neck_c.tolist(),'shift':dxy.tolist()}
bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
json.dump(log, open(LOG,'w'), indent=1, default=float)
print("STAGE_AB_DONE", OUT)
