import rasterio, numpy as np, pickle
from rasterio.windows import from_bounds
from scipy import ndimage as ndi
r=rasterio.open('/mnt/project-files/jordan-geology/Bender1968_250k_Aqaba-Maan_ITM.tif')
B=(186000,378000,262000,547290)
w=from_bounds(*B,r.transform); img=r.read(window=w).astype(float); T=r.window_transform(w)
img=np.stack([ndi.median_filter(c,3) for c in img])
P={'q5':(232,228,199),'q4':(218,215,198),'q3':(231,227,208),'q2p':(226,218,174),'q2':(228,221,177),
   'paper':(250,249,234),'tl4':(232,223,153),'green1':(216,232,168),'green2':(200,216,152),'green3':(184,200,140),
   'brown1':(152,136,104),'brown2':(120,104,88),'dark':(70,70,60),'grey':(170,170,160),'olive':(136,136,104),
   'red':(200,70,50),'orange':(230,130,80),'blue':(170,200,220),'pink':(230,180,160),'yellow':(230,200,90)}
names=list(P); C=np.array([P[k] for k in names],float)
X=img.reshape(3,-1).T; lab=((X[:,None,:]-C[None])**2).sum(2).argmin(1).reshape(img.shape[1:])
np.save('/tmp/claude-0/blab.npy',lab); pickle.dump((names,T),open('/tmp/claude-0/blab.pkl','wb'))
for i,n in enumerate(names): print(n, round((lab==i).mean()*100,1))
