import numpy as np, json, math
from PIL import Image, ImageDraw, ImageFont
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
OUT='/home/user/-/neru_n2/images/'
H=np.load(W+'v5_head.npy').astype(np.float64)
cands=json.load(open(W+'cands_v8.json'))
lm=json.load(open(W+'landmarks_v8.json')); LB=lm['body']; LH=lm['head']
xc=(LB['B'][0]+LB['F'][0])/2
rows=[]
def metrics(P):
    ear=P[(P[:,2]>=0.735)&(P[:,2]<=0.775)]
    if len(ear)>20:
        thr=np.quantile(np.abs(ear[:,1]),0.9); e=ear[np.abs(ear[:,1])>=thr]; ear_x=np.median(e[:,0])
    else: ear_x=np.nan
    def neck(z0,z1):
        q=P[(P[:,2]>=z0)&(P[:,2]<=z1)&(np.abs(P[:,1])<0.03)&(P[:,0]>-0.10)&(P[:,0]<0.02)]
        return np.median(q[:,0]) if len(q)>10 else np.nan, np.median(q[:,2]) if len(q)>10 else np.nan
    nb_x,nb_z=neck(0.700,0.712); nt_x,nt_z=neck(0.724,0.736)
    tilt=math.degrees(math.atan2(nt_x-nb_x, nt_z-nb_z)) if not np.isnan(nt_x*nb_x) else np.nan
    band=P[(P[:,2]>=0.690)&(P[:,2]<=0.705)]
    out=((((band[:,0]-xc)/0.030)**2+(band[:,1]/0.045)**2)>1.0)
    return dict(ear_minus_neck_mm=(ear_x-nt_x)*1000, neck_tilt_deg=tilt, pierce=int(out.sum()))
for c in cands:
    M=np.array(c['M']); P=(M[:3,:3]@H.T).T+M[:3,3]
    m=metrics(P); m['name']=c['name']; rows.append(m)
    print(c['name'], {k:(round(v,2) if isinstance(v,float) else v) for k,v in m.items() if k!='name'})
json.dump(rows,open(W+'metrics_v8.json','w'),indent=1,default=float)
# 3x3 sheet: rows dx -8,0,+8 ; cols tilt -6,0,+6
F=ImageFont.load_default()
cell=480; pad=36
sheet=Image.new('RGB',(3*cell+4*10,3*(cell+60)+10),(255,255,255))
for idx,r in enumerate(rows):
    i,j=divmod(idx,3)
    im=Image.open(W+f'cand_{idx}.png').convert('RGB')
    x=10+j*(cell+10); y=10+i*(cell+60)
    d=ImageDraw.Draw(sheet)
    d.text((x+4,y),f'#{idx+1}  dx {["-8","0","+8"][i]} mm / tilt {["-6","0","+6"][j]} deg',fill=(0,0,0),font=F)
    d.text((x+4,y+14),f'ear-neck {r["ear_minus_neck_mm"]:+.1f} mm | neck tilt {r["neck_tilt_deg"]:+.1f} deg | pierce {r["pierce"]}',fill=(0,0,0),font=F)
    sheet.paste(im.resize((cell,cell)),(x,y+60-40+20))
sheet.save(OUT+'n2_v8_candidates_side.png'); print('sheet',sheet.size)
# landmark image (side projection, x-z)
fig,ax=plt.subplots(1,2,figsize=(10,5))
for a,(title,pts,lab) in zip(ax,[('head file (v5 placement)',LH,'H'),('body',LB,'B')]):
    a.scatter(H[:,0],H[:,2],s=0.2,c='0.6') if lab=='H' else None
    keys=['L','R','B','F']
    for k,n in zip(keys,range(1,5)):
        p=pts[k]; a.scatter(p[0],p[2],c='r' if lab=='B' else 'b',s=60); a.text(p[0]+0.002,p[2]+0.002,f'{n}{k}',fontsize=12)
    a.set_title(title); a.set_aspect('equal'); a.set_xlim(-0.12,0.04); a.set_ylim(0.62,0.80); a.grid(alpha=.3)
plt.tight_layout(); plt.savefig(OUT+'n2_v8_landmarks.png',dpi=90); print('landmarks saved')
