import json,numpy as np,cv2,rasterio
from rasterio.transform import from_origin
from pyproj import Transformer
P=json.load(open('poly.json')); cx=np.array(P['cx']); cy=np.array(P['cy'])
img=cv2.imread('k.jpg')[:,:,::-1]
H,W=img.shape[:2]
# frame mask (pixel space): main rect + inset rect
mask=np.zeros((H,W),np.uint8)
cv2.rectangle(mask,(1373,258),(3135,5661),255,-1); cv2.rectangle(mask,(675,4754),(3135,5661),255,-1)
tr=Transformer.from_crs(4326,2039,always_xy=True); inv=Transformer.from_crs(2039,4326,always_xy=True)
corn=[(34+36/60,29+20/60),(35+40/60,29+20/60),(35+40/60,31+20/60),(34+55/60,31+20/60)]
xs,ys=tr.transform([c[0] for c in corn],[c[1] for c in corn])
res=40.0; x0=np.floor(min(xs)/res)*res-2000; x1=np.ceil(max(xs)/res)*res+2000; y0=np.floor(min(ys)/res)*res-2000; y1=np.ceil(max(ys)/res)*res+2000
nx=int((x1-x0)/res); ny=int((y1-y0)/res)
gx,gy=np.meshgrid(x0+res*(np.arange(nx)+.5), y1-res*(np.arange(ny)+.5))
lo,la=inv.transform(gx.ravel(),gy.ravel()); lo=np.array(lo); la=np.array(la)
V=np.column_stack([np.ones_like(lo),lo,la,lo*lo,lo*la,la*la])
mx=(V@cx).reshape(ny,nx).astype(np.float32); my=(V@cy).reshape(ny,nx).astype(np.float32)
out=cv2.remap(img,mx,my,cv2.INTER_AREA if False else cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
m=cv2.remap(mask,mx,my,cv2.INTER_NEAREST,borderValue=0)
out[m==0]=0
ys_,xs_=np.where(m>0); r0,r1,c0,c1=ys_.min(),ys_.max()+1,xs_.min(),xs_.max()+1
out=out[r0:r1,c0:c1]; m=m[r0:r1,c0:c1]
T=from_origin(x0+c0*res,y1-r0*res,res,res)
prof=dict(driver='GTiff',height=out.shape[0],width=out.shape[1],count=3,dtype='uint8',crs='EPSG:2039',transform=T,compress='JPEG',photometric='YCbCr',tiled=True,blockxsize=256,blockysize=256,jpeg_quality=90)
with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True):
  with rasterio.open('Kitchener_Arabah_1883_ITM.tif','w',**prof) as d:
    d.write(np.moveaxis(out,-1,0)); d.write_mask(m); d.build_overviews([2,4,8],rasterio.enums.Resampling.average)
print(out.shape, T)
