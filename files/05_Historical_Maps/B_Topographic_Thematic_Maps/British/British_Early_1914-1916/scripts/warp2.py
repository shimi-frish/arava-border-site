import numpy as np, rasterio, sys, glob, cv2
from rasterio.transform import from_origin
from rasterio.enums import Resampling as R
from scipy.interpolate import RBFInterpolator
from pyproj import Transformer
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
i=int(sys.argv[1]); res=float(sys.argv[2]); name=sys.argv[3]
fs=sorted(glob.glob('/mnt/project-files/*.jpg'))
r=np.load(f'r{i}.npy')
T=Transformer.from_crs(4229,2039,always_xy=True)
E,N=T.transform(r[:,0],r[:,1]); G=np.c_[E,N]; P=r[:,2:4]
fwd=RBFInterpolator(P,G,kernel='thin_plate_spline'); inv=RBFInterpolator(G,P,kernel='thin_plate_spline')
src=np.asarray(Image.open(fs[i]).convert('RGB'))
H,W=src.shape[:2]
# extent from image border
t=np.linspace(0,1,50); bx=np.r_[t*W,np.full(50,W),t*W,np.zeros(50)]; by=np.r_[np.zeros(50),t*H,np.full(50,H),t*H]
b=fwd(np.c_[bx,by]); x0,x1=b[:,0].min(),b[:,0].max(); y0,y1=b[:,1].min(),b[:,1].max()
x0=np.floor(x0/res)*res; y1=np.ceil(y1/res)*res
w=int((x1-x0)/res)+1; h=int((y1-y0)/res)+1
print(name,w,h)
step=32; gx=np.arange(0,w+step,step); gy=np.arange(0,h+step,step)
XX,YY=np.meshgrid(x0+(gx+0.5)*res, y1-(gy+0.5)*res)
pp=inv(np.c_[XX.ravel(),YY.ravel()]).reshape(len(gy),len(gx),2).astype(np.float32)
mx=cv2.resize(pp[...,0],(len(gx)*step,len(gy)*step),interpolation=cv2.INTER_LINEAR)[:h,:w]
my=cv2.resize(pp[...,1],(len(gx)*step,len(gy)*step),interpolation=cv2.INTER_LINEAR)[:h,:w]
# cv2.resize aligns corners differently: correct half-step offset
# (resize maps pixel centers: out k -> in (k+0.5)/step-0.5) ; recompute exactly by using sample positions gx -> place at k=gx*... handled via shift
sh=(step-1)/2.0
M=np.float32([[1,0,sh],[0,1,sh]])
mx=cv2.warpAffine(cv2.resize(pp[...,0],(len(gx)*step,len(gy)*step),interpolation=cv2.INTER_LINEAR),M,(len(gx)*step,len(gy)*step),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP,borderMode=cv2.BORDER_REPLICATE)[:h,:w]
my=cv2.warpAffine(cv2.resize(pp[...,1],(len(gx)*step,len(gy)*step),interpolation=cv2.INTER_LINEAR),M,(len(gx)*step,len(gy)*step),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP,borderMode=cv2.BORDER_REPLICATE)[:h,:w]
# verify at a few output pixels
for (cx,cy) in [(w//3,h//3),(w//2,h//2),(2*w//3,2*h//3)]:
    ex=inv([[x0+(cx+0.5)*res, y1-(cy+0.5)*res]])[0]; print('chk',ex-[mx[cy,cx],my[cy,cx]])
dst=np.zeros((h,w,3),np.uint8); m=np.zeros((h,w),np.uint8)
CH=4096
for a in range(0,h,CH):
    dst[a:a+CH]=cv2.remap(src,mx[a:a+CH],my[a:a+CH],cv2.INTER_LINEAR if res>0 else 0,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
    ok=(mx[a:a+CH]>=0)&(mx[a:a+CH]<=W-1)&(my[a:a+CH]>=0)&(my[a:a+CH]<=H-1)
    m[a:a+CH]=ok*255
del src
tr=from_origin(x0,y1,res,res)
prof=dict(driver='GTiff',width=w,height=h,count=3,dtype='uint8',crs='EPSG:2039',transform=tr,tiled=True,blockxsize=512,blockysize=512,compress='JPEG',photometric='YCBCR',jpeg_quality=85,BIGTIFF='IF_SAFER')
with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True):
  with rasterio.open(f'out/{name}.tif','w',**prof) as d:
    d.write(dst.transpose(2,0,1)); d.write_mask(m)
    d.build_overviews([2,4,8,16,32],R.average); d.update_tags(ns='rio_overview',resampling='average')
np.save(f'out/{name}_gcps.npy',np.c_[r[:,:4],G])
print('done',name)
