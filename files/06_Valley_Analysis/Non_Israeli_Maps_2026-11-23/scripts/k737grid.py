import sys, json, numpy as np
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
from pyproj import Transformer
f, corners, out = sys.argv[1], json.loads(sys.argv[2]), sys.argv[3]
c=np.array(corners,float)
t=Transformer.from_crs(4230,23036,always_xy=True)
E,N=t.transform(c[:,0],c[:,1]); W=np.c_[E,N]
A=np.c_[W,np.ones(4)]; cx=np.linalg.lstsq(A,c[:,2],rcond=None)[0]; cy=np.linalg.lstsq(A,c[:,3],rcond=None)[0]
pix=lambda e,n:(cx[0]*e+cx[1]*n+cx[2], cy[0]*e+cy[1]*n+cy[2])
im=np.asarray(Image.open(f).convert('RGB')).astype(float)
# black grid line: dark in all channels incl. blue (brown contours have low B but higher R)
dark=im.max(2)
e0,e1=W[:,0].min(),W[:,0].max(); n0,n1=W[:,1].min(),W[:,1].max()
V={};Hh={}
for e in range(int(e0//1000+1)*1000,int(e1),1000):
    pts=[]
    for n in np.linspace(n0+500,n1-500,60):
        x,y=map(int,pix(e,n)); seg=dark[y-10:y+11, x-20:x+21].mean(0); i=np.argmin(seg)
        if seg[i]<np.median(seg)-40: pts.append((x-20+i,y))
    p=np.array(pts)
    if len(p)<15: continue
    k=np.polyfit(p[:,1],p[:,0],1); m=abs(p[:,0]-np.polyval(k,p[:,1]))<3
    if m.sum()<12: continue
    V[e]=np.polyfit(p[m,1],p[m,0],1)
for n in range(int(n0//1000+1)*1000,int(n1),1000):
    pts=[]
    for e in np.linspace(e0+500,e1-500,60):
        x,y=map(int,pix(e,n)); seg=dark[y-20:y+21, x-10:x+11].mean(1); i=np.argmin(seg)
        if seg[i]<np.median(seg)-40: pts.append((x,y-20+i))
    p=np.array(pts)
    if len(p)<15: continue
    k=np.polyfit(p[:,0],p[:,1],1); m=abs(p[:,1]-np.polyval(k,p[:,0]))<3
    if m.sum()<12: continue
    Hh[n]=np.polyfit(p[m,0],p[m,1],1)
g=[]
for e,kv in V.items():
    for n,kh in Hh.items():
        y=(kh[0]*kv[1]+kh[1])/(1-kh[0]*kv[0]); x=kv[0]*y+kv[1]
        px,py=pix(e,n)
        if abs(x-px)<15 and abs(y-py)<15: g.append((e,n,x,y))
print(len(V),len(Hh),len(g))
json.dump(g,open(out,'w'))
