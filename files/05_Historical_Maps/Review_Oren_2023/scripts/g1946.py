import sys; sys.path.insert(0,'scripts'); from georef_tools import *
# similarity fit (north-up sketch) from 3 control points
G=[(408,428,197515,383900,'Pillar No.1 at shore = 1994 border coast point'),(655,658,199879,381353,'Aqaba fort (Mamluk castle)'),(183,365,195193,384321,'Umm Rashrash police post = Ink flag site')]
A=[];b=[]
for c,r,E,N,_ in G:
    A.append([c,-r,1,0]); b.append(E)   # E = a*c - b*r + tx  (rows go down -> use -r)
    A.append([-r,-c,0,1]); b.append(N)  # placeholder, replaced below
# proper similarity: [E,N] = s*R*[c,-r] + t
import numpy as np
M=[];v=[]
for c,r,E,N,_ in G:
    x,y=c,-r
    M.append([x,-y,1,0]); v.append(E)
    M.append([y, x,0,1]); v.append(N)
p,*_=np.linalg.lstsq(np.array(M,float),np.array(v,float),rcond=None)
a,bb,tx,ty=p; print('scale m/px',np.hypot(a,bb),'rot deg',np.degrees(np.arctan2(bb,a)))
pred=[(a*c-bb*(-r)+tx, bb*c+a*(-r)+ty) for c,r,E,N,_ in G]
for (c,r,E,N,n),(pe,pn) in zip(G,pred): print(n,round(np.hypot(pe-E,pn-N)))
# make 4 synthetic gcps from this similarity for from_gcps (affine exact)
S=[(c,r,a*c-bb*(-r)+tx,bb*c+a*(-r)+ty) for c,r in [(0,0),(878,0),(0,837),(878,837)]]
from_gcps('/mnt/user-data/uploads/Israel-Jordan-Arava/05_Historical_Maps/A_Agreement_Border_Maps/British_Ottoman/מפת סימון קו הגבול עם עבר הירדן בראש המפרץ – 194652.png',S,'Boundary_marking_Gulf_of_Aqaba_1946_ITM.tif',order=1)
json.dump({'control_points':G,'method':'similarity (scale+rotation+shift)'},open('Gulf_1946_gcps.json','w'),ensure_ascii=False)
