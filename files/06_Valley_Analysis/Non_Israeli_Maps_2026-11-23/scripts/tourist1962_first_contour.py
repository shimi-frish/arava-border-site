# First orange contour east of the 1994 border on the Jordan tourist map (DLS 1962, print 1979; IRCICA H-791)
import sys,numpy as np,geopandas as g,rasterio
sys.path.insert(0,'/mnt/project-files/non-israeli-maps/scripts'); from warp import fit
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
from pyproj import Transformer
from shapely.geometry import LineString
from shapely.ops import unary_union
from scipy import ndimage as nd
O='/mnt/project-files/non-israeli-maps/'
X0,Y0,X1,Y1=800,6400,4400,13800
im=Image.open(O+'src/Jordan_Tourist_Map_DLS_1962_print1979_IRCICA_H-791.jpeg').crop((X0,Y0,X1,Y1))
a=np.asarray(im).astype(int); R,G,B=a[...,0],a[...,1],a[...,2]
orange=(R-B>55)&(R>180)&(G<R-25)&(G>=145)&(G<=185)
# remove isolated specks
orange=nd.binary_opening(orange,np.ones((2,2)))
road=((R-G>55)&(G<135))|(a.max(2)<110)   # red road fill and black casings/dashes/text
road=nd.binary_dilation(road,iterations=10)
orange&=~road
orange=nd.binary_dilation(orange,iterations=2)
gp=np.array([[35,32,344,1019],[36,32,1072,1019],[37,32,1817,1013],[35,31,344,1858],[36,31,1074,1860],[37,31,1817,1853],[35,30,344,2701],[36,30,1073,2706],[37,30,1817,2700]],float)
t=Transformer.from_crs(4326,32636,always_xy=True); ti=Transformer.from_crs(32636,4326,always_xy=True)
wx,wy=t.transform(gp[:,0],gp[:,1]); inv=fit(np.c_[wx,wy],gp[:,2:]*4+1.5,2)
V=unary_union(g.read_file('/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg',layer='valley_polygon_auto_rule').to_crs(32636).geometry)
Bd=unary_union(g.read_file('/mnt/project-files/border-map/border1994.geojson').to_crs(32636).geometry)
dem=rasterio.open(O+'Copernicus_DEM_GLO30_Arava_60m_UTM36.tif')
rows=[]
for y in np.arange(V.bounds[1]+500,V.bounds[3]-500,250):
    L=LineString([(V.bounds[0]-20000,y),(V.bounds[2]+25000,y)])
    bi=Bd.intersection(L); vi=V.intersection(L)
    if bi.is_empty or vi.is_empty: continue
    xb=bi.bounds[2]
    xs=np.arange(xb+800,xb+30000,30.0)
    P=inv(np.c_[xs,np.full_like(xs,y)])
    c=(P[:,0]-X0).astype(int); r=(P[:,1]-Y0).astype(int)
    ok=(c>=0)&(c<orange.shape[1])&(r>=0)&(r<orange.shape[0])
    hit=np.zeros(len(xs),bool); hit[ok]=orange[r[ok],c[ok]]
    j=np.where(hit)[0]
    if not len(j): continue
    xe=xs[j[0]]; z=list(dem.sample([(xe,y)]))[0][0]
    rows.append((y,xb,xe,vi.bounds[2],z))
r=np.array(rows); np.save('/tmp/claude-0/dl/tour_edge.npy',r)
d=(r[:,2]-r[:,3])/1000
print(len(r),'median',np.median(d).round(2),'p10',np.percentile(d,10).round(2),'p90',np.percentile(d,90).round(2),'east',(d>0).mean().round(2),'west>1',(d<-1).mean().round(3),'abs<1',(abs(d)<1).mean().round(2),'abs<2',(abs(d)<2).mean().round(2))
print('DEM elev at contour: median',np.median(r[:,4]).round(),'p25',np.percentile(r[:,4],25).round(),'p75',np.percentile(r[:,4],75).round())
for lo in range(3270000,3440000,20000):
    m=(r[:,0]>=lo)&(r[:,0]<lo+20000)
    if m.sum(): print(lo,m.sum(),np.median(d[m]).round(2),np.median(r[m,4]).round())
