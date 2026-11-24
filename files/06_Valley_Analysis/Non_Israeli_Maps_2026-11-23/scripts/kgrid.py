from PIL import Image; import numpy as np, json
a=np.asarray(Image.open('/tmp/claude-0/maps/TransJordan_250k_Kerak_1941.jpg').convert('L')).astype(float)
H,W=a.shape
x200,px=942,304.2; y1000,py=4142,-303.9
def refine_v(x0, ys):
    pts=[]
    for y in ys:
        seg=a[y-40:y+40, int(x0)-25:int(x0)+26].mean(0); i=np.argmin(seg)
        if seg[i]<np.median(seg)-25: pts.append((x0-25+i,y))
    return pts
def refine_h(y0, xs):
    pts=[]
    for x in xs:
        seg=a[int(y0)-25:int(y0)+26, x-40:x+40].mean(1); i=np.argmin(seg)
        if seg[i]<np.median(seg)-25: pts.append((x,y0-25+i))
    return pts
V={};Hh={}
for E in range(180,301,10):
    x0=x200+(E-200)/10*px
    if not 200<x0<W-150: continue
    p=np.array(refine_v(x0, range(600,4300,120)))
    if len(p)<10: continue
    k=np.polyfit(p[:,1],p[:,0],1); r=p[:,0]-np.polyval(k,p[:,1]); m=abs(r)<4
    k=np.polyfit(p[m,1],p[m,0],1); V[E]=k; print('E',E,len(p),m.sum(),np.round(k,4))
for N in range(990,1121,10):
    y0=y1000+(N-1000)/10*py
    if not 300<y0<H-300: continue
    p=np.array(refine_h(y0, range(500,4100,120)))
    if len(p)<10: continue
    k=np.polyfit(p[:,0],p[:,1],1); r=p[:,1]-np.polyval(k,p[:,0]); m=abs(r)<4
    k=np.polyfit(p[m,0],p[m,1],1); Hh[N]=k; print('N',N,len(p),m.sum(),np.round(k,4))
g=[]
for E,kv in V.items():
    for N,kh in Hh.items():
        y=(kh[0]*kv[1]+kh[1])/(1-kh[0]*kv[0]); x=kv[0]*y+kv[1]; g.append((E*1000,N*1000,x,y))
g=np.array(g)
A=np.c_[g[:,2],g[:,3],np.ones(len(g))]
cx,_,_,_=np.linalg.lstsq(A,g[:,0],rcond=None); cy,_,_,_=np.linalg.lstsq(A,g[:,1],rcond=None)
res=np.hypot(A@cx-g[:,0],A@cy-g[:,1]); print('n',len(g),'affine RMS m',res.std(), np.sqrt((res**2).mean()), res.max())
json.dump(g.tolist(),open('/tmp/claude-0/kerak_gcps.json','w'))
