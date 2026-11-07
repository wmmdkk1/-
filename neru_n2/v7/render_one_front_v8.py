import bpy, json, os, math
from mathutils import Matrix, Vector
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
i=int(os.environ['CAND_IDX']); c=json.load(open(W+'cands_v8.json'))[i]
head=bpy.data.objects['Head_new_PinkBraid']
head.data.transform(Matrix(c['M']))
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=24; scene.cycles.use_denoising=False
scene.render.resolution_x=480; scene.render.resolution_y=480; scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='Standard'
if scene.world is None: scene.world=bpy.data.worlds.new('W')
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background'); bg.inputs[0].default_value=(0.42,0.42,0.42,1); bg.inputs[1].default_value=1.0
mat=bpy.data.materials.new('pg'); mat.use_nodes=True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.80,0.80,0.82,1)
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.6
for o in bpy.data.objects:
    if o.type=='MESH': o.data.materials.clear(); o.data.materials.append(mat)
sd=bpy.data.lights.new('sun','SUN'); sd.energy=4.5; so=bpy.data.objects.new('sun',sd); scene.collection.objects.link(so); so.rotation_euler=(math.radians(35),0,math.radians(-110))
ad=bpy.data.lights.new('amb','SUN'); ad.energy=0.15; ao=bpy.data.objects.new('amb',ad); scene.collection.objects.link(ao); ao.rotation_euler=(math.radians(-30),0,math.radians(-150))
cen=Vector((-0.04,0.0,0.73)); size=0.40
cd=bpy.data.cameras.new('cam'); cd.type='ORTHO'; cd.ortho_scale=size
cam=bpy.data.objects.new('cam',cd); scene.collection.objects.link(cam); scene.camera=cam
cam.location=cen+Vector((1,0,0))*size*3
cam.rotation_euler=(cen-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=W+f'candfront_{i}.png'
bpy.ops.render.render(write_still=True)
print('ONE_DONE',i)
