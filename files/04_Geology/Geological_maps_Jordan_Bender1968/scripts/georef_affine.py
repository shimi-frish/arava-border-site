"""Warp a scan to ITM given a conformal affine pixel->(E,N) in a source grid CRS (e.g. Palestine Grid EPSG:28193).
args: cfg.json with scan, src_crs, aff [e0,a1,a2,n0] (E=e0+a1*px+a2*py, N=n0+a2*px-a1*py), clip [px0,py0,px1,py1], res, out, tags"""
import sys, json, numpy as np, rasterio
from PIL import Image
from pyproj import Transformer
from scipy.ndimage import map_coordinates
from rasterio.transform import from_origin
Image.MAX_IMAGE_PIXELS=None
c=json.load(open(sys.argv[1])); img=np.asarray(Image.open(c['scan']).convert('RGB'))
e0,a1,a2,n0=c['aff']; px0,py0,px1,py1=c['clip']
M=np.array([[a1,a2],[a2,-a1]]); Mi=np.linalg.inv(M)
fwd=Transformer.from_crs(c['src_crs'],'EPSG:2039',always_xy=True); inv=Transformer.from_crs('EPSG:2039',c['src_crs'],always_xy=True)
cx=[px0,px1,px0,px1]; cy=[py0,py0,py1,py1]
E=[e0+a1*x+a2*y for x,y in zip(cx,cy)]; N=[n0+a2*x-a1*y for x,y in zip(cx,cy)]
X,Y=fwd.transform(E,N); res=c['res']
xmin,xmax,ymin,ymax=min(X),max(X),min(Y),max(Y); W=int((xmax-xmin)/res)+1; H=int((ymax-ymin)/res)+1
rgb=np.zeros((3,H,W),np.uint8); mask=np.zeros((H,W),np.uint8)
for r0 in range(0,H,400):
    r1=min(H,r0+400)
    gx,gy=np.meshgrid(xmin+(np.arange(W)+.5)*res, ymax-(np.arange(r0,r1)+.5)*res)
    e,n=inv.transform(gx,gy)
    px=Mi[0,0]*(e-e0)+Mi[0,1]*(n-n0); py=Mi[1,0]*(e-e0)+Mi[1,1]*(n-n0)
    ins=(px>=px0)&(px<=px1)&(py>=py0)&(py<=py1)
    for b in range(3): rgb[b,r0:r1]=np.where(ins,map_coordinates(img[:,:,b],[py,px],order=1,mode='nearest'),0)
    mask[r0:r1]=ins*255
p=dict(driver='GTiff',width=W,height=H,count=3,dtype='uint8',crs='EPSG:2039',transform=from_origin(xmin,ymax,res,res),
       compress='JPEG',photometric='YCBCR',jpeg_quality=88,tiled=True,blockxsize=512,blockysize=512)
with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True):
    with rasterio.open(c['out'],'w',**p) as d:
        d.write(rgb); d.write_mask(mask); d.update_tags(**c.get('tags',{}))
        d.build_overviews([2,4,8,16],rasterio.enums.Resampling.average)
print('wrote',c['out'],W,H,(xmin,ymin,xmax,ymax))
