# helpers: build ITM (EPSG:2039) RGBA GeoTIFF from an image + (a) world file in some CRS or (b) GCPs pixel->ITM (affine or poly2)
import numpy as np, rasterio, json
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling, calculate_default_transform
from rasterio.control import GroundControlPoint
from affine import Affine
from PIL import Image
from pyproj import Transformer
Image.MAX_IMAGE_PIXELS=None
TO_ITM=lambda epsg: Transformer.from_crs(epsg,2039,always_xy=True)
LL=Transformer.from_crs(4326,2039,always_xy=True)
def rgba(img):
    a=np.array(Image.open(img).convert('RGBA')); return np.moveaxis(a,2,0)
def from_world(img,wf,epsg,out,res=None):
    w=[float(v) for v in open(wf).read().split()]
    A=Affine(w[0],w[2],w[4],w[1],w[3],w[5])*Affine.translation(-0.5,-0.5)
    a=rgba(img); _,h,wd=a.shape
    T,W,H=calculate_default_transform(f'EPSG:{epsg}','EPSG:2039',wd,h,*rasterio.transform.array_bounds(h,wd,A)[::-1][::-1] if False else _bounds(A,wd,h),resolution=res)
    dst=np.zeros((4,H,W),np.uint8)
    for b in range(4): reproject(a[b],dst[b],src_transform=A,src_crs=f'EPSG:{epsg}',dst_transform=T,dst_crs='EPSG:2039',resampling=Resampling.bilinear)
    _write(out,dst,T)
def _bounds(A,w,h):
    xs,ys=zip(*[A*(c,r) for c,r in [(0,0),(w,0),(0,h),(w,h)]]); return min(xs),min(ys),max(xs),max(ys)
def _write(out,dst,T):
    with rasterio.open(out,'w',driver='GTiff',height=dst.shape[1],width=dst.shape[2],count=4,dtype='uint8',crs='EPSG:2039',transform=T,compress='deflate',photometric='RGB',alpha='YES' if False else None) as o:
        o.write(dst)
        o.colorinterp=[rasterio.enums.ColorInterp.red,rasterio.enums.ColorInterp.green,rasterio.enums.ColorInterp.blue,rasterio.enums.ColorInterp.alpha]
def fit(gcps,order=1):
    # gcps: list of (col,row,E,N); returns predict fn and residuals
    P=np.array(gcps,float); c,r,E,N=P.T
    def X(c,r):
        c=np.asarray(c,float); r=np.asarray(r,float)
        cols=[np.ones_like(c),c,r]+([c*c,c*r,r*r] if order==2 else [])
        return np.stack(cols,-1)
    M=X(c,r); ce,*_=np.linalg.lstsq(M,E,rcond=None); cn,*_=np.linalg.lstsq(M,N,rcond=None)
    pe=M@ce; pn=M@cn; res=np.hypot(pe-E,pn-N)
    f=lambda c,r:(X(c,r)@ce, X(c,r)@cn)
    return f,res
def from_gcps(img,gcps,out,order=1,res_m=None):
    a=rgba(img); _,h,w=a.shape
    f,res=fit(gcps,order)
    # inverse fit ITM->pixel for warping
    P=np.array(gcps,float); inv,_=fit([(e,n,c,r) for c,r,e,n in P],order)
    bx,by=f(np.array([0,w,0,w,w/2,0,w/2,w]),np.array([0,0,h,h,0,h/2,h,h/2]))
    if res_m is None: res_m=float(np.median([np.hypot(*(np.array(f(1,0))-np.array(f(0,0)))),np.hypot(*(np.array(f(0,1))-np.array(f(0,0))))]))
    x0,x1,y0,y1=bx.min(),bx.max(),by.min(),by.max()
    W=int((x1-x0)/res_m); H=int((y1-y0)/res_m); T=from_origin(x0,y1,res_m,res_m)
    cc,rr=np.meshgrid(np.arange(W)+0.5,np.arange(H)+0.5)
    E,N=T*(cc,rr); pc,pr=inv(E.ravel(),N.ravel()); pc=pc.reshape(H,W); pr=pr.reshape(H,W)
    from scipy.ndimage import map_coordinates
    dst=np.zeros((4,H,W),np.uint8)
    for b in range(4): dst[b]=map_coordinates(a[b].astype(float),[pr-0.5,pc-0.5],order=1,cval=0).clip(0,255)
    _write(out,dst,T)
    return res
