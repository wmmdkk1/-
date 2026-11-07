import bpy, bmesh, math, numpy as np, json, os
from mathutils import Vector, Matrix
OUT=os.environ['OUT_BLEND']; LOG=os.environ['LOG_JSON']
REF=json.loads(os.environ.get('REF_JSON','{}'))
head=bpy.data.objects['Head_new_PinkBraid']; sh=bpy.data.objects['model_part9']
log={}
def arr(o): return np.array([v.co[:] for v in o.data.vertices],dtype=np.float64)
Hv=arr(head); Sv=arr(sh)
# torso depth at z 0.62-0.66 (jacket/shirt body), excluding skirt region
m=(Sv[:,2]>0.62)&(Sv[:,2]<0.66)
tx=Sv[m,0]; p1,p99=np.percentile(tx,1),np.percentile(tx,99)
torso_mid=(p1+p99)/2; depth=p99-p1
xN0,yN0=-0.0326,-0.0030   # current neck centre (v3/v5 collar centre)
xN_target=torso_mid+0.05*depth
dx=xN_target-xN0
log.update(torso_x_p1=p1,torso_x_p99=p99,torso_mid=torso_mid,torso_depth=depth,dx_head=dx)
# 1) rigid lean + shift of head about neck base pivot
theta=math.radians(float(os.environ.get('LEAN_DEG','12')))
piv=Vector((xN0,yN0,0.705))
Rm=Matrix.Rotation(theta,4,'Y')
T=Matrix.Translation(piv)@Rm@Matrix.Translation(-piv)@Matrix.Translation((dx,0,0))
head.data.transform(T)
log['lean_deg']=math.degrees(theta)
# 2) neck thinning (radial, falloff) around new neck axis, zone z 0.69-0.75
Hv=arr(head); xN=xN0+dx
bm=bmesh.new(); bm.from_mesh(head.data); bm.verts.ensure_lookup_table()
k=float(os.environ.get('NECK_THIN','0.92')); cnt=0
for v in bm.verts:
    z=v.co.z
    if 0.69<=z<=0.75:
        r=math.hypot(v.co.x-xN, v.co.y-yN0)
        if r<0.045:
            w=1-(r/0.045)**2
            s=1-(1-k)*w
            v.co.x=xN+(v.co.x-xN)*s; v.co.y=yN0+(v.co.y-yN0)*s; cnt+=1
bm.to_mesh(head.data); bm.free()
log['neck_thinned_verts']=cnt
# 3) collar: back-side collar rises and comes in toward neck
bm=bmesh.new(); bm.from_mesh(sh.data)
cc=0
for v in bm.verts:
    z=v.co.z
    if 0.69<=z<=0.72:
        back=xN-v.co.x
        if back>0.01:
            w=min(back/0.05,1.0)
            v.co.x=v.co.x+0.30*w*(xN-v.co.x)
            v.co.z=v.co.z+0.015*w
            cc+=1
bm.to_mesh(sh.data); bm.free()
log['collar_moved_verts']=cc
# 4) measurements
Hv=arr(head); Sv=arr(sh)
chin=np.percentile(Hv[(Hv[:,2]>0.68)&(Hv[:,2]<0.75)][:,2],5) if True else 0
top=np.percentile(Hv[:,2],99.5)
log['head_top']=top
log['neck_zone_x']=[float(np.percentile(Hv[(Hv[:,2]>0.705)&(Hv[:,2]<0.72)][:,0],1)),float(np.percentile(Hv[(Hv[:,2]>0.705)&(Hv[:,2]<0.72)][:,0],99))]
log['shirt_top_z']=float(Sv[:,2].max()) if False else None
bpy.ops.wm.save_as_mainfile(filepath=OUT,compress=True)
json.dump(log,open(LOG,'w'),indent=1,default=float)
print('V6_DONE',json.dumps(log,default=float))
