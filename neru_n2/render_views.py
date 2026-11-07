# usage: blender -b file.blend --python render_views.py -- <outprefix> <res> [views]
import bpy, sys, math, os
from mathutils import Vector
argv = sys.argv[sys.argv.index('--')+1:]
outprefix = argv[0]; res = int(argv[1]) if len(argv) > 1 else 400
views = argv[2].split(',') if len(argv) > 2 else ['front','back','left','right','top']
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'; scene.cycles.samples = int(os.environ.get('SAMPLES','16')); scene.cycles.use_denoising = False
scene.render.resolution_x = res; scene.render.resolution_y = res; scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'Standard'
scene.world = scene.world or bpy.data.worlds.new('W')
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get('Background')
if bg: bg.inputs[0].default_value = (1,1,1,1); bg.inputs[1].default_value = 1.0
mesh_objs = [o for o in bpy.context.scene.objects if o.type == 'MESH' and not o.hide_render]
mat = bpy.data.materials.new('preview_grey'); mat.use_nodes = True
bsdf = mat.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (0.78,0.78,0.80,1)
bsdf.inputs['Roughness'].default_value = 0.6
for o in mesh_objs:
    o.data.materials.clear(); o.data.materials.append(mat)
# bbox
pts = []
for o in mesh_objs:
    pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
mn = Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
mx = Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
center = (mn+mx)/2; size = max((mx-mn).x,(mx-mn).y,(mx-mn).z)
if os.environ.get('ZOOM_Z'):
    center = Vector((float(os.environ.get('ZOOM_X','0')), float(os.environ.get('ZOOM_Y','0')), float(os.environ['ZOOM_Z']))); size = float(os.environ['ZOOM_SIZE'])
dirs = {
 'front': Vector((0,-1,0)),   # camera at -Y looking +Y
 'back': Vector((0,1,0)),
 'left': Vector((0,1,0)),     # placeholder, replaced below
 'right': Vector((0,-1,0)),
 'top': Vector((0,0,1)),
 'bottom': Vector((0,0,-1)),
 'plusX': Vector((1,0,0)),
 'minusX': Vector((-1,0,0)),
}
# semantic: front = +X facing (after orientation) ; we use raw dirs given explicitly
cam_data = bpy.data.cameras.new('cam'); cam_data.type='ORTHO'; cam_data.ortho_scale = size*1.15
cam = bpy.data.objects.new('cam', cam_data); scene.collection.objects.link(cam); scene.camera = cam
sun_data = bpy.data.lights.new('sun', 'SUN'); sun_data.energy = 3.0
sun = bpy.data.objects.new('sun', sun_data); scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(45), 0, math.radians(30))
amb = bpy.data.lights.new('amb','SUN'); amb.energy = 1.2
ambo = bpy.data.objects.new('amb', amb); scene.collection.objects.link(ambo); ambo.rotation_euler=(math.radians(-30),0,math.radians(-150))
for name in views:
    # project convention: character front = +X, left = +Y, up = +Z
    d = {'front':Vector((1,0,0)),'back':Vector((-1,0,0)),'left':Vector((0,1,0)),'right':Vector((0,-1,0)),
         'top':Vector((0,0,1)),'bottom':Vector((0,0,-1))}[name]
    cam.location = center + d*size*3
    cam.rotation_euler = (center - cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath = f"{outprefix}_{name}.png"
    bpy.ops.render.render(write_still=True)
    print("VIEW", name, scene.render.filepath, "center", tuple(round(v,4) for v in center), "size", round(size,4))
