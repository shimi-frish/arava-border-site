import numpy as np, json, sys
from scipy.ndimage import uniform_filter1d
def refine(g, x, y, L, S, axis):
    # axis 'v': find vertical line x near x using strip rows y-L..y+L
    if axis=='v':
        a=255-np.asarray(g[int(y-L):int(y+L), int(x-S-40):int(x+S+40)],dtype=np.float32)
        p=np.median(a,axis=0) if False else a.mean(axis=0)
        off=int(x-S-40)
    else:
        a=255-np.asarray(g[int(y-S-40):int(y+S+40), int(x-L):int(x+L)],dtype=np.float32)
        p=a.mean(axis=1); off=int(y-S-40)
    p=p-uniform_filter1d(p,41)
    core=p[40:-40]; k=int(np.argmax(core))
    # sharpness score
    sc=core[k]/ (np.std(core)+1e-6)
    # subpixel
    if 0<k<len(core)-1:
        a_,b_,c_=core[k-1],core[k],core[k+1]; d=0.5*(a_-c_)/(a_-2*b_+c_+1e-9)
    else: d=0
    return off+40+k+d, sc
def poly_terms(u,v,o):
    return np.stack([u**i*v**j for i in range(o+1) for j in range(o+1-i)],1)
def run(i, lons, xs, lats, ys, L, S, order=2):
    g=np.load(f'g{i}.npy',mmap_mode='r')
    # initial prediction: separable
    pts=[]
    for lo,x in zip(lons,xs):
        for la,y in zip(lats,ys):
            pts.append([lo,la,x,y])
    pts=np.array(pts,float)
    for it in range(3):
        out=[]
        for lo,la,x,y in pts:
            xr,s1=refine(g,x,y,L,S,'v'); yr,s2=refine(g,x,y,L,S,'h')
            # second pass with refined other coord
            xr,s1=refine(g,xr,yr,L,S,'v'); yr,s2=refine(g,xr,yr,L,S,'h')
            out.append([lo,la,xr,yr,s1,s2])
        out=np.array(out)
        # robust fit px from lonlat
        u=(out[:,0]-out[:,0].mean()); v=(out[:,1]-out[:,1].mean())
        A=poly_terms(u,v,order); good=np.ones(len(out),bool)
        for _ in range(4):
            cx=np.linalg.lstsq(A[good],out[good,2],rcond=None)[0]; cy=np.linalg.lstsq(A[good],out[good,3],rcond=None)[0]
            r=np.hypot(A@cx-out[:,2],A@cy-out[:,3]); s=np.median(r[good])*1.4826+0.5
            good=r<max(3.5*s,6)
        pts=np.c_[out[:,:2], np.where(good,out[:,2],A@cx), np.where(good,out[:,3],A@cy)]
        S=max(25,S//2)
        print('iter',it,'good',good.sum(),'/',len(out),'rms px',np.sqrt(np.mean(r[good]**2)).round(2), 'bad',[(round(a,4),round(b,4),round(rr,1)) for a,b,rr in zip(out[~good,0],out[~good,1],r[~good])])
    return out,good,r
if __name__=='__main__':
    cfg=json.load(open(sys.argv[1]))
    out,good,r=run(**cfg)
    np.save(sys.argv[2],np.c_[out,good,r])
