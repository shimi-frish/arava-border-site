import numpy as np, json, rasterio, sys
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
from pyproj import Transformer
from scipy.ndimage import map_coordinates
def design(x,y,order):
    cols=[np.ones_like(x),x,y]
    if order>=2: cols+= [x*x,x*y,y*y]
    if order>=3: cols+= [x**3,x*x*y,x*y*y,y**3]
    return np.stack(cols,-1)
def fit(src,dst,order):  # src Nx2 -> dst Nx2, normalized
    m=src.mean(0); s=src.std(0)
    D=design((src[:,0]-m[0])/s[0],(src[:,1]-m[1])/s[1],order)
    c=np.linalg.lstsq(D,dst,rcond=None)[0]
    return lambda p: design((p[...,0]-m[0])/s[0],(p[...,1]-m[1])/s[1],order)@c
def warp(img_path, gcp_world, gcp_pix, src_crs, out, res=25, order=2, bounds=None):
    im=np.asarray(Image.open(img_path).convert('RGB'))
    t=Transformer.from_crs(src_crs,32636,always_xy=True)
    wx,wy=t.transform(gcp_world[:,0],gcp_world[:,1]); W=np.c_[wx,wy]
    inv=fit(W,gcp_pix,order); fwd=fit(gcp_pix,W,order)
    r=np.hypot(*(fwd(gcp_pix)-W).T); print(out,'GCP n',len(W),'RMS m',round(float(np.sqrt((r**2).mean())),1),'max',round(float(r.max()),1))
    if bounds is None:
        x0,y0=W.min(0); x1,y1=W.max(0)
    else: x0,y0,x1,y1=bounds
    xs=np.arange(x0,x1,res)+res/2; ys=np.arange(y1,y0,-res)-res/2
    X,Y=np.meshgrid(xs,ys); P=inv(np.stack([X,Y],-1))
    outa=np.zeros((3,)+X.shape,np.uint8)
    for b in range(3): outa[b]=map_coordinates(im[...,b],[P[...,1],P[...,0]],order=1,cval=0)
    mask=(P[...,0]>0)&(P[...,0]<im.shape[1]-1)&(P[...,1]>0)&(P[...,1]<im.shape[0]-1)
    tr=rasterio.transform.from_origin(x0,y1,res,res)
    with rasterio.open(out,'w',driver='GTiff',width=X.shape[1],height=X.shape[0],count=4,dtype='uint8',crs='EPSG:32636',transform=tr,compress='deflate',tiled=True) as d:
        d.write(outa[0],1);d.write(outa[1],2);d.write(outa[2],3);d.write((mask*255).astype(np.uint8),4)
    return r
