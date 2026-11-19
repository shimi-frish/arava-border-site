import numpy as np, json
g=np.load('g.npy')
Y=lambda m: 5207-(m-1770)*45.11
X=lambda m: 774+(m-2080)*39.32
def prof_peak(p,bgwin):
    bg=np.median(bgwin); d=bg-p; i=int(np.argmax(d)); k=slice(max(i-2,0),i+3); w=np.clip(d[k]-d[k].min()*0,0,None)
    c=(np.arange(len(d))[k]*w).sum()/w.sum(); return c,d[i],np.median(np.abs(d-np.median(d)))
def vt(m,xline,side):
    y0=int(round(Y(m)))
    xl=xline-10+int(np.argmin(g[y0-80:y0+80,xline-10:xline+10].mean(0)))
    band=g[:, xl+2:xl+9] if side>0 else g[:, xl-8:xl-1]
    p=band[y0-30:y0+31].mean(1); c,s,n=prof_peak(p,band[y0-90:y0+91].mean(1))
    return xl, y0-30+c, s, n
def ht(m,yline,side):
    x0=int(round(X(m)))
    yl=yline-10+int(np.argmin(g[yline-10:yline+10,x0-80:x0+80].mean(1)))
    band=g[yl+2:yl+9,:] if side>0 else g[yl-8:yl-1,:]
    p=band[:,x0-30:x0+31].mean(0); c,s,n=prof_peak(p,band[:,x0-90:x0+91].mean(0))
    return x0-30+c, yl, s, n
out=[]
for side in (+1,-1):
  for m in range(1770,1880,10):
    xl,y,s,n=vt(m,3132,side); out.append(('R%+d'%side,2140,m,xl,y,s,n))
  for m in range(1810,1880,10):
    xl,y,s,n=vt(m,1373,side); out.append(('L%+d'%side,None,m,xl,y,s,n))
  for m in (1770,):
    xl,y,s,n=vt(m,675,side); out.append(('IL%+d'%side,None,m,xl,y,s,n))
  for m in range(2080,2140,10):
    x,yl,s,n=ht(m,5661,side); out.append(('B%+d'%side,m,1760,x,yl,s,n))
  for m in range(2110,2140,10):
    x,yl,s,n=ht(m,258,side); out.append(('T%+d'%side,m,1880,x,yl,s,n))
for o in out: print(o[0],o[1],o[2],round(o[3],1),round(o[4],1),round(o[5]),round(o[6],1))
json.dump(out,open('t2.json','w'))
