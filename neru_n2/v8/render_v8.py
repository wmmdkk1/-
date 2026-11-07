import bpy, json, os, math
from mathutils import Matrix, Vector
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
SIZE=float(os.environ.get('SIZE','1.0')); TAG=os.environ.get('TAG','s100')
VIEWS=os.environ.get('VIEWS','front,left').split(',')
nk=json.load(open(W+'v8_neck.json')); piv=Vector((nk['pivot'][0],nk['pivot'][1],nk['pivot'][2]))
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=24; scene.cycles.use_denoising=False
scene.render.image_settings.file_format='PNG'; scene.view_settings.view_transform='Standard'
if scene.world is None: scene.world=bpy.data.worlds.new('W')
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background'); bg.inputs[0].default_value=(0.42,0.42,0.42,1); bg.inputs[1].default_value=1.0
mat=bpy.data.materials.new('pg'); mat.use_nodes=True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.80,0.80,0.82,1)
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.6
for o in bpy.data.objects:
    if o.type=='MESH':
        o.data.materials.clear(); o.data.materials.append(mat)
if SIZE!=1.0:
    S=Matrix.Diagonal((SIZE,SIZE,SIZE,1))
    T=Matrix.Translation(piv)@S@Matrix.Translation(-piv)
    for nm in ['Head_new_PinkBraid','Neck_plug']:
        o=bpy.data.objects[nm]; o.data.transform(T)
sd=bpy.data.lights.new('sun','SUN'); sd.energy=4.5; so=bpy.data.objects.new('sun',sd); scene.collection.objects.link(so); so.rotation_euler=(math.radians(35),0,math.radians(-110))
ad=bpy.data.lights.new('amb','SUN'); ad.energy=0.15; ao=bpy.data.objects.new('amb',ad); scene.collection.objects.link(ao); ao.rotation_euler=(math.radians(-30),0,math.radians(-150))
scene.render.resolution_x=600; scene.render.resolution_y=600
cd=bpy.data.cameras.new('cam'); cd.type='ORTHO'; cam=bpy.data.objects.new('cam',cd); scene.collection.objects.link(cam); scene.camera=cam
def shot(name, cen, rng, direction):
    cd.ortho_scale=rng
    cam.location=cen+direction.normalized()*rng*3
    cam.rotation_euler=(cen-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=W+f'{name}.png'; bpy.ops.render.render(write_still=True)
XP=Vector((1,0,0)); YP=Vector((0,1,0)); X30=Vector((1,0,0.577))
for v in VIEWS:
    if v=='front': shot(f'v8{TAG}_front', Vector((0,0,0.45)), 1.05, XP)
    if v=='left': shot(f'v8{TAG}_left', Vector((0,0,0.45)), 1.05, YP)
    if v=='neck_front': shot(f'v8{TAG}_neckfront', Vector((-0.035,0,0.68)), 0.22, XP)
    if v=='neck_top30': shot(f'v8{TAG}_necktop30', Vector((-0.035,0,0.68)), 0.22, X30)
print('RENDER_DONE',TAG)
