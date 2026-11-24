import numpy as np, rasterio, cv2, sys
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape
name=sys.argv[1]
d=rasterio.open(f'out/{name}.tif')
a=d.read().transpose(1,2,0); m=d.read_masks(1)>0
lab=np.empty(a.shape,np.float32)
CH=2000
for y in range(0,a.shape[0],CH):
    sl=slice(max(0,y-20),y+CH+20)
    b=cv2.blur(a[sl].astype(np.float32)/255,(15,15)); L=cv2.cvtColor(b,cv2.COLOR_RGB2Lab)
    o=y-max(0,y-20); lab[y:y+CH]=L[o:o+CH]
pk=(lab[...,1]>4.8)&(lab[...,2]<13.5)&(lab[...,0]>70)&m
pk=pk.astype(np.uint8)
k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15))
pk=cv2.morphologyEx(pk,cv2.MORPH_OPEN,k); pk=cv2.morphologyEx(pk,cv2.MORPH_CLOSE,k)
n,lbl,st,_=cv2.connectedComponentsWithStats(pk)
keep=np.zeros(n,bool); keep[1:]=st[1:,4]*36>200000  # >0.2 km2
pk=keep[lbl].astype(np.uint8)
geoms=[shape(g) for g,v in shapes(pk,mask=pk>0,transform=d.transform)]
gdf=gpd.GeoDataFrame({'src':[name]*len(geoms)},geometry=geoms,crs=2039)
gdf['geometry']=gdf.simplify(6); gdf['area_km2']=gdf.area/1e6
gdf.to_file(f'out/{name}_wadibeds.gpkg'); print(name,len(gdf),gdf.area_km2.sum())
