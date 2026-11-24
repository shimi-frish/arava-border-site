import sys; sys.path.insert(0,'scripts'); sys.path.insert(0,'.'); from georef_tools import *; from gsim import similarity
J=LL.transform(35.2310,31.7767); R=LL.transform(34.2170,31.3220)
G=[(205,343,*J),(152,808,197515,383900),(28,447,*R)]
f,s,rot=similarity(G); print('m/px',s,'rot',rot)
for g,n in zip(G,['Jerusalem','Gulf tip','Rafah coast']): e,nn=f(g[0],g[1]); print(n,round(float(np.hypot(e-g[2],nn-g[3]))))
S=[(c,r,*f(c,r)) for c,r in [(0,0),(406,0),(0,838),(406,838)]]
from_gcps('/mnt/user-data/uploads/Israel-Jordan-Arava/05_Historical_Maps/A_Agreement_Border_Maps/International/מפת גבולות החלוקה 1947.png',S,'UN_Partition_Plan_1947_ITM.tif')
json.dump({'gcps':G,'names':['Jerusalem','Gulf of Aqaba tip (1994 border coast point)','Rafah coast'],'method':'similarity'},open('Partition1947_gcps.json','w'))
