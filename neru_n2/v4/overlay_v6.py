import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion
W='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/work/'
REF='/tmp/claude-0/-home-user--/7aed085c-97bc-50f2-a30d-b8c2ccb6abe2/scratchpad/inputs/unzipped_A/Neru_Start_A/refs/full/'
OUT='/home/user/-/neru_n2/images/'
def bbox_mask(im, bg, thr):
    a=np.array(im.convert('RGB')).astype(int); d=np.abs(a-np.array(bg)).sum(2); m=d>thr
    ys,xs=np.where(m); return m,(xs.min(),xs.max(),ys.min(),ys.max())
def side(view, refname, out):
    ref=Image.open(REF+refname).convert('RGB')
    rm,(rx0,rx1,ry0,ry1)=bbox_mask(ref,(255,255,255),60)
    mdl=Image.open(W+f'v6full_{view}.png').convert('RGB')
    mm,(mx0,mx1,my0,my1)=bbox_mask(mdl,(107,107,107),30)
    # scale model so its figure height matches ref figure height
    s=(ry1-ry0)/(my1-my0)
    mdl2=mdl.resize((int(mdl.width*s),int(mdl.height*s)),Image.LANCZOS)
    mm2=np.array(Image.fromarray((mm*255).astype(np.uint8)).resize(mdl2.size))>0
    # place: model figure bbox -> ref figure bbox (align horizontal centres too)
    ox=int(round((rx0+rx1)/2 - ((mx0+mx1)/2)*s)); oy=int(round(ry0 - my0*s))
    canvas=Image.new('RGB',ref.size,(255,255,255))
    canvas.paste(mdl2,(ox,oy))
    # model silhouette mask on ref canvas
    full=np.zeros((ref.height,ref.width),bool)
    ys,xs=np.where(mm2); 
    yy=ys+oy; xx=xs+ox; ok=(yy>=0)&(yy<ref.height)&(xx>=0)&(xx<ref.width)
    full[yy[ok],xx[ok]]=True
    edge=full & ~binary_erosion(full,iterations=2)
    base=np.array(ref).astype(float)*0.55+255*0.45
    base[edge]=[230,30,30]
    Image.fromarray(base.astype(np.uint8)).save(OUT+out)
    # model-only panel on grey for shading check
    Image.fromarray(np.array(canvas)).save(W+'v6_model_'+view+'.png')
    print('saved',out,'scale',round(s,3),'ox',ox,'oy',oy)
side('left','03_Left.png','n2_v6_overlay_left_ref.png')
side('right','04_Right.png','n2_v6_overlay_right_ref.png')
