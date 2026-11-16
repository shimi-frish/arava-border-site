import sys, json, os, numpy as np
sys.path.insert(0, os.path.expanduser('~/gc'))
from rd import open_mm
D=os.path.expanduser('~/mnt/Israel-Jordan-Arava/05_Historical_Maps/Historical_Maps1/')
G=os.path.expanduser('~/mnt/Israel-Jordan-Arava/05_Historical_Maps/_grid_check/')
FS={'zofar69':'0001_FL44748971_modified.tif','menuha69':'0001_FL44749077_modified.tif','yafruk69':'0001_FL44749060_modified.tif','amatzyahu69':'גליון נחל אמציהו -1969 - 50,000.tif','sedom61':'0001_FL266344297_modified.tif','sedom61mm':'0001_FL266344297_modified_modified.tif','arava58':'גליון נחל הערבה - 1958 -100,000.tif','eilat55':'גליון אילת - 1955 - 100,000.tif','adin49':'גליון עין עדין - 1949 - 100,000.tif','yahav48':'גליון עין יהב - 1948 - 100,000.tif','omer48':'גליון אל עומר - 1948 -100,000.tif'}
NS=json.load(open(G+'nodes.json'))
def peak(prof, c0):
    i=int(np.argmax(prof)); 
    if 0<i<len(prof)-1:
        a,b,c=prof[i-1],prof[i],prof[i+1]; d=(a-c)/(2*(a-2*b+c)) if (a-2*b+c)!=0 else 0
    else: d=0
    return i+d
def line_pos(win, axis, hw):
    # axis=0 -> vertical line: profile over columns; split rows into 4 strips
    dk=255.0-win.max(axis=2)
    if axis==1: dk=dk.T
    n=dk.shape[0]; strips=np.array_split(np.arange(n),4)
    ps=[]; con=[]
    for s in strips:
        # skip the central part near the crossing line
        prof=dk[s].mean(axis=0)
        p=peak(prof,hw); ps.append(p); con.append(prof.max()-np.median(prof))
    ps=np.array(ps)
    ok=(np.ptp(ps)<=4) and min(con)>25
    return float(np.median(ps)), ok, float(min(con))
res={}
for k in sys.argv[1:]:
    a,gt,e=open_mm(D+FS[k]); H,W=a.shape[:2]
    px=NS[k]['px']; hw=int(round(350/px))
    rows=[]
    for E_,N_,c,r in NS[k]['nodes']:
        ci,ri=int(round(c)),int(round(r))
        if ri-hw<0 or ci-hw<0 or ri+hw>=H or ci+hw>=W: continue
        win=np.asarray(a[ri-hw:ri+hw+1, ci-hw:ci+hw+1]).astype(np.float32)
        # vertical line (constant E) -> column position
        vc,vok,vcon=line_pos(win,0,hw)
        hr,hok,hcon=line_pos(win,1,hw)
        rows.append([E_,N_,c,r,ci-hw+vc,ri-hw+hr,int(vok),int(hok),round(vcon,1),round(hcon,1)])
    res[k]=rows
    print(k,len(rows),sum(1 for x in rows if x[6] and x[7]),flush=True)
json.dump(res,open(G+'det_'+'_'.join(sys.argv[1:])+'.json','w'))
