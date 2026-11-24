# Alternative 4: thalweg per historical maps = least-cost route along the drainage drawn on AMS K502 1:250,000 (1961, 3 sheets)
# plus the large wadi beds of the 1914-15 British 1:125,000 Sinai sheets, inside the historical valley (alternative 2).
import numpy as np, rasterio, geopandas as gpd, json
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
import rasterio.features as rf
from scipy import ndimage as ndi
from skimage.graph import route_through_array
from shapely.geometry import LineString, Point
FV='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
CRS='EPSG:32636'
H=gpd.read_file('/mnt/project-files/border-alternatives/Border_alternatives_2_4_historical.gpkg',layer='historical_valley_polygon').to_crs(CRS).geometry.iloc[0]
T=gpd.read_file(FV,layer='thalweg_line').to_crs(CRS).geometry.iloc[0]
x0,y0,x1,y1=H.buffer(3000).bounds; px=50
W,Hh=int((x1-x0)/px),int((y1-y0)/px); tr=from_origin(x0,y1,px,px)
rgb=np.zeros((3,Hh,W),'float32'); have=np.zeros((Hh,W),bool)
for s in ['Aqaba','Maan','Jerusalem']:
    with rasterio.open(f'/mnt/project-files/non-israeli-maps/georef/AMS_K502_{s}_1961_UTM36.tif') as r:
        a=np.zeros((4,Hh,W),'float32')
        for b in range(4): reproject(rasterio.band(r,b+1),a[b],dst_transform=tr,dst_crs=CRS,resampling=Resampling.average)
        m=(a[3]>128)&~have; rgb[:,m]=a[:3,m]; have|=m
R,G,B=rgb
blue=(B>R+25)&(B>G+12)&have
# remove UTM grid lines: long straight runs along rows/columns
lab=blue.copy()
for ax in (0,1):
    run=ndi.uniform_filter1d(blue.astype(float),size=61,axis=ax)>0.9
    lab&=~ndi.binary_dilation(run,iterations=1)
blue=lab
# drop blue drawn alongside main roads (pipeline/aqueduct symbols run parallel to road 90): long dark road lines, 300 m buffer
dark=(R<95)&(G<95)&(B<110)&have
lab_,n_=ndi.label(ndi.binary_dilation(dark,iterations=1))
sl=ndi.find_objects(lab_)
big=np.zeros(n_+1,bool)
for i,o in enumerate(sl,1):
    if o is not None and max(o[0].stop-o[0].start,o[1].stop-o[1].start)*px>3000: big[i]=True
road=big[lab_]
blue&=~ndi.binary_dilation(road,iterations=6)
beds=rf.rasterize([(g,1) for g in gpd.read_file('/mnt/project-files/british-early-maps/Large_wadi_beds_1915_125k.gpkg').to_crs(CRS).geometry],out_shape=(Hh,W),transform=tr).astype(bool)
inside=rf.rasterize([(H.buffer(500),1)],out_shape=(Hh,W),transform=tr).astype(bool)
chan=ndi.binary_dilation(blue|beds,iterations=1)
cost=np.where(chan,1.0,12.0); cost[~inside]=1e6
def rc(p): c,r=~tr*(p.x,p.y); return int(r),int(c)
ps,pe=Point(T.coords[0]),Point(T.coords[-1])
path,c=route_through_array(cost,rc(ps),rc(pe),fully_connected=True,geometric=True)
xy=[tr*(cc+.5,rr+.5) for rr,cc in path]
L=LineString(xy).simplify(60)
k=7; a=np.array(L.coords); sm=np.vstack([a[0]]+[a[max(0,i-k//2):i+k//2+1].mean(0) for i in range(1,len(a)-1)]+[a[-1]])
L=LineString(sm)
onchan=np.mean([chan[r,c_] for r,c_ in path])
gpd.GeoDataFrame({'name':['חלופה 4: קו התלווג לפי עדויות היסטוריות (AMS K502 1961 ומפות 1915)']},geometry=[L],crs=CRS).to_crs(2039).to_file('/tmp/claude-0/alt/alt4.gpkg',layer='alt4_historical_thalweg_line',driver='GPKG')
with rasterio.open('/tmp/claude-0/alt/k502_blue.tif','w',driver='GTiff',height=Hh,width=W,count=1,dtype='uint8',crs=CRS,transform=tr,compress='deflate') as d: d.write((chan*1+beds*1).astype('uint8'),1)
print(json.dumps({'length_km':round(L.length/1000,1),'share_on_drawn_channel':round(float(onchan),3)}))
