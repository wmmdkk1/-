import bpy, bmesh, json, math, numpy as np, os
from mathutils import Matrix, Vector
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
OUT=os.environ.get('OUT_BLEND', W+'Neru_n2_v8.blend')
cands=json.load(open(W+'cands_v8.json'))
M=np.array(cands[5]['M'])   # #6 = dx 0mm, tilt +6 deg
assert cands[5]['name']=='dx+0mm_tilt+6deg', cands[5]['name']
head=bpy.data.objects['Head_new_PinkBraid']
head.data.transform(Matrix(M.tolist()))
# neck ring at z 0.690-0.700 (cut edge) -> centre and radius
bmh=bmesh.new(); bmh.from_mesh(head.data); bmh.edges.ensure_lookup_table()
bverts=set()
for e in bmh.edges:
    if e.is_boundary:
        for v in e.verts:
            if v.co.z<0.70: bverts.add(v.index)
bmh.verts.ensure_lookup_table(); ring=np.array([bmh.verts[i].co[:] for i in bverts])
bmh.free()
print('boundary ring verts',len(ring),'z',ring[:,2].min() if len(ring) else None, ring[:,2].max() if len(ring) else None)
c=ring[:,:2].mean(0); r=float(np.median(np.linalg.norm(ring[:,:2]-c,axis=1)))
print('NECK centre',c,'radius',r,'n',len(ring))
# plug: tube from z 0.695 (inside head neck) down to z 0.640 inside the shirt/tee, closed bottom
N=24
me=bpy.data.meshes.new('Neck_plug'); bm=bmesh.new()
top=[bm.verts.new((c[0]+r*math.cos(2*math.pi*i/N), c[1]+r*math.sin(2*math.pi*i/N), 0.695)) for i in range(N)]
bot=[bm.verts.new((c[0]+r*math.cos(2*math.pi*i/N), c[1]+r*math.sin(2*math.pi*i/N), 0.640)) for i in range(N)]
for i in range(N):
    j=(i+1)%N
    bm.faces.new((top[i],top[j],bot[j],bot[i]))
bm.faces.new(bot)
bm.normal_update(); bm.to_mesh(me); bm.free()
plug=bpy.data.objects.new('Neck_plug',me); bpy.context.scene.collection.objects.link(plug)
# cut edge closure: head's own open bottom at z 0.690 is now covered by plug top (overlap)
json.dump({'neck_centre':[float(c[0]),float(c[1])],'neck_radius':r,'pivot':[float(c[0]),float(c[1]),0.69]},open(W+'v8_neck.json','w'),indent=1)
bpy.ops.wm.save_as_mainfile(filepath=OUT,compress=True)
print('V8_SAVED',OUT)
