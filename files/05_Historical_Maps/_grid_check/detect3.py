# Region-growing grid-intersection detection: predicts each node with an affine correction
# fitted to already-found nodes, so large systematic misfits (scale/rotation) are followed.
import sys, json, os, numpy as np
sys.path.insert(0, os.path.expanduser('~/gc'))
from rd import open_mm
exec(open(os.path.expanduser('~/mnt/Israel-Jordan-Arava/05_Historical_Maps/_grid_check/detect.py')).read().split('res={}')[0])
res={}
for k in sys.argv[1:]:
    a,gt,e=open_mm(D+FS[k]); H,W=a.shape[:2]
    px=NS[k]['px']; hw=int(round(300/px))
    nodes=np.array(NS[k]['nodes'],float)
    cen=np.median(nodes[:,2:4],axis=0)
    order=np.argsort(np.hypot(nodes[:,2]-cen[0],nodes[:,3]-cen[1]))
    acc=[]; rows=[]
    def predict(c,r):
        if len(acc)<4:
            if not acc: return c,r
            d=np.array(acc); return c+np.median(d[:,2]-d[:,0]), r+np.median(d[:,3]-d[:,1])
        d=np.array(acc); A=np.c_[np.ones(len(d)),d[:,0],d[:,1]]
        # weight nearer nodes more (local fit)
        w=1/(1+np.hypot(d[:,0]-c,d[:,1]-r)/(3000/px))
        cx=np.linalg.lstsq(A*w[:,None],d[:,2]*w,rcond=None)[0]; cy=np.linalg.lstsq(A*w[:,None],d[:,3]*w,rcond=None)[0]
        return cx@[1,c,r], cy@[1,c,r]
    SEED={'sedom61':(175*8,176.7*8,1.0574,376.7*8,399*8,1.0394)}
    sd=SEED.get(k)
    for i in order:
        E_,N_,c0,r0=nodes[i]
        c,r=(sd[0]+sd[2]*(c0-sd[1]), sd[3]+sd[5]*(r0-sd[4])) if sd else (c0,r0)
        pc,pr=predict(c,r); ci,ri=int(round(pc)),int(round(pr))
        if ri-hw<0 or ci-hw<0 or ri+hw>=H or ci+hw>=W: continue
        win=np.asarray(a[ri-hw:ri+hw+1, ci-hw:ci+hw+1]).astype(np.float32)
        vc,vok,vcon=line_pos(win,0,hw); hr,hok,hcon=line_pos(win,1,hw)
        fc,fr=ci-hw+vc, ri-hw+hr
        if vok and hok and np.hypot(fc-pc,fr-pr)*px<200:
            acc.append([c,r,fc,fr]); rows.append([E_,N_,c0,r0,fc,fr,1,1,vcon,hcon])
    res[k]=rows
    print(k,len(nodes),len(rows),flush=True)
G2=os.path.expanduser('~/mnt/Israel-Jordan-Arava/05_Historical_Maps/_grid_check/')
for k,v in res.items(): json.dump(v,open(G2+'det2_'+k+'.json','w'))
