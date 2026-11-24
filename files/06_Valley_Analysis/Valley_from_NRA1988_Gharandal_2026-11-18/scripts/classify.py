import rasterio, numpy as np
from rasterio.enums import Resampling
from scipy import ndimage as ndi
r=rasterio.open('/mnt/project-files/jordan-geology/NRA50k_3050III_Wadi_Gharandal_1988_ITM.tif')
f=2; img=r.read(out_shape=(3,r.height//f,r.width//f),resampling=Resampling.average).astype(float)
T=r.transform*r.transform.scale(r.width/(r.width//f),r.height/(r.height//f))
img=np.stack([ndi.median_filter(c,3) for c in img])
P={'Al':(254,252,175),'Alf':(253,233,71),'Als':(254,253,44),'Plg':(254,238,117),'Pls':(221,206,115),'LM':(237,172,54),
   'WG':(253,221,7),'AAS':(211,194,17),'MCM':(144,161,48),'URC':(250,154,46),'WSL':(188,225,153),'DC':(178,113,80),
   'paper':(251,251,238),'black':(60,60,60),'grey':(170,170,170),'RG':(200,225,120),'ASL':(90,170,160),'KS':(60,140,70),'red':(190,40,40)}
names=list(P); C=np.array([P[k] for k in names],float)
X=img.reshape(3,-1).T
d=((X[:,None,:]-C[None,:,:])**2).sum(2); lab=d.argmin(1).reshape(img.shape[1:])
np.save('/tmp/claude-0/lab.npy',lab); 
import pickle; pickle.dump((names,T,img.shape),open('/tmp/claude-0/lab.pkl','wb'))
for i,n in enumerate(names): print(n, round((lab==i).mean()*100,1))
