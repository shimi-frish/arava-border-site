# Georeference the 1949 Israel-Jordan armistice map (Survey of Palestine 1:250,000 North+South sheets, 1946 print)
# GCPs: 557 auto-detected Palestine-grid intersections (10 km), EPSG:28191; thin-plate spline -> ITM (EPSG:2039)
import numpy as np, rasterio, sys, json
from rasterio.transform import from_origin
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates
from pyproj import Transformer
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
SRC, GCP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
g=np.load(GCP)                           # E_km, N_km(label; south values already negative), px, py, ...
P=np.c_[g[:,0]*1000, g[:,1]*1000]          # Palestine grid metres
rbf_x=RBFInterpolator(P, g[:,2], kernel='thin_plate_spline', smoothing=5.0)
rbf_y=RBFInterpolator(P, g[:,3], kernel='thin_plate_spline', smoothing=5.0)
# leave-one-out style check: residual of fit
res=np.hypot(rbf_x(P)-g[:,2], rbf_y(P)-g[:,3]); print('fit residual px rms', np.sqrt((res**2).mean()).round(2))
img=np.asarray(Image.open(SRC).convert('RGB'))
t=Transformer.from_crs(28191,2039,always_xy=True); ti=Transformer.from_crs(2039,28191,always_xy=True)
cx,cy=t.transform([80000,220000,80000,220000],[-120000,-120000,300000,300000])
RES=40.0
x0=np.floor(min(cx)/RES)*RES; x1=np.ceil(max(cx)/RES)*RES; y0=np.floor(min(cy)/RES)*RES; y1=np.ceil(max(cy)/RES)*RES
W=int((x1-x0)/RES); H=int((y1-y0)/RES); print('out',W,H)
# coarse grid of mapping (every 25 px) then bilinear upsample
step=25
gx=np.arange(0,W+step,step); gy=np.arange(0,H+step,step)
GX,GY=np.meshgrid(x0+(gx+0.5)*RES, y1-(gy+0.5)*RES)
pe,pn=ti.transform(GX.ravel(),GY.ravel())
Q=np.c_[pe,pn]
mx=rbf_x(Q).reshape(GX.shape); my=rbf_y(Q).reshape(GX.shape)
inside=((pe>=80000)&(pe<=220000)&(pn>=-120000)&(pn<=300000)).reshape(GX.shape).astype(float)
rr,cc=np.mgrid[0:H,0:W]
fr=rr/step; fc=cc/step
MX=map_coordinates(mx,[fr,fc],order=1); MY=map_coordinates(my,[fr,fc],order=1); IN=map_coordinates(inside,[fr,fc],order=1)>0.5
out=np.zeros((4,H,W),np.uint8)
for b in range(3): out[b]=map_coordinates(img[...,b],[MY,MX],order=1,cval=0)
out[3]=np.where(IN,255,0)
for b in range(3): out[b][~IN]=0
with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True):
    with rasterio.open(OUT,'w',driver='GTiff',width=W,height=H,count=3,dtype='uint8',crs='EPSG:2039',
        transform=from_origin(x0,y1,RES,RES),compress='JPEG',jpeg_quality=88,photometric='YCBCR',tiled=True,blockxsize=256,blockysize=256) as d:
        d.write(out[:3]); d.write_mask(out[3]>0)
json.dump({'n_gcps':int(len(g)),'fit_rms_px':float(np.sqrt((res**2).mean())),'res_m':RES,'bounds_itm':[x0,y0,x1,y1]},open(OUT+'.info.json','w'),indent=1)
print('ok')
