import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import binary_erosion
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
REF='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/inputs/unzipped_A/Neru_Start_A/refs/full/'
OUT='/home/user/-/neru_n2/images/'
P2=np.load(W+'part2_final.npy').astype(np.float64)
HD=np.load(W+'v4_head.npy').astype(np.float64)
SH=np.load(W+'v4_head_shirt.npy').astype(np.float64)
def project(P,view):
    if view=='left':  return np.c_[-P[:,0],P[:,2]]
    if view=='right': return np.c_[ P[:,0],P[:,2]]
    return np.c_[P[:,1],P[:,2]]
def mask(uv,cx,cy,ppu,Wd,Ht,px0,py0,dil=1):
    px=(uv[:,0]-cx)*ppu+px0; py=py0-(uv[:,1]-cy)*ppu
    ok=(px>=0)&(px<Wd)&(py>=0)&(py<Ht)
    m=np.zeros((Ht,Wd),bool); m[py[ok].astype(int),px[ok].astype(int)]=True
    if dil>0: m=np.array(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2*dil+1)))>0
    return m
def render(view,name,zoom=None):
    uvH,uvP=project(HD,view),project(P2,view)
    if zoom is None:
        ref=Image.open(REF+{'left':'03_Left.png','right':'04_Right.png','front':'01_Front.png'}[view]).convert('RGB')
        a=np.array(ref.convert('L')); ys,xs=np.where(a<235)
        x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
        ppu=(y1-y0)/0.9; cx=project(SH,view)[:,0].mean(); cy=0.45
        Wd,Ht=ref.size; px0=(x0+x1)/2; py0=(y0+y1)/2
        base=np.array(ref).astype(float)
        canvas=(0.5*np.full_like(base,128)+0.5*base).astype(np.uint8)
    else:
        Wd=Ht=900; cx,cy,rng=zoom; ppu=Wd/rng; px0=Wd/2; py0=Ht/2
        canvas=np.full((Ht,Wd,3),128,np.uint8)
    mH=mask(uvH,cx,cy,ppu,Wd,Ht,px0,py0,3)
    mP=mask(uvP,cx,cy,ppu,Wd,Ht,px0,py0,3)
    edge=mP & ~binary_erosion(mP,iterations=2)
    canvas[mH]=np.array([226,226,234],np.uint8)
    canvas[edge]=np.array([235,25,25],np.uint8)
    Image.fromarray(canvas).save(OUT+name); print('saved',name,canvas.shape,'ppu',round(ppu,1))
render('left','n2_v4_side_left.png')
render('right','n2_v4_side_right.png')
render('front','n2_v4_front.png')
render('left','n2_v4_neck_zoom_left.png',zoom=(-0.03,0.78,0.42))
render('right','n2_v4_neck_zoom_right.png',zoom=(0.03,0.78,0.42))
