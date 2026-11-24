import sys,json,numpy as np,rasterio
sys.path.insert(0,'.'); from warp import warp
from pyproj import Transformer
src,gcp,out,lon0,lat0,lon1,lat1=sys.argv[1],sys.argv[2],sys.argv[3],*map(float,sys.argv[4:8])
g=np.array(json.load(open(gcp)))
warp(src,g[:,:2],g[:,2:],23036,out,res=10,order=3)
t=Transformer.from_crs(32636,4230,always_xy=True)
with rasterio.open(out,'r+') as d:
    a=d.read(4); r,c=np.indices(a.shape); x,y=rasterio.transform.xy(d.transform,r.ravel(),c.ravel())
    lo,la=t.transform(np.array(x),np.array(y)); m=((lo>=lon0)&(lo<=lon1)&(la>=lat0)&(la<=lat1)).reshape(a.shape)
    a[~m]=0; d.write(a,4)
