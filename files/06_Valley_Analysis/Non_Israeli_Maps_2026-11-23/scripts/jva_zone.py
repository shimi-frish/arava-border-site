# Jordan Valley Development Law 1988 (amended 2001), Art. 2(c) area 2:
# from northern edge of Dead Sea to southern boundary of Qatar village; W = Jordan's western frontier; E = 500 m a.s.l.
import numpy as np, rasterio, geopandas as g
from rasterio import features
from shapely.geometry import shape, Point, box
from shapely.ops import unary_union
F='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
OUT='/mnt/project-files/non-israeli-maps/'
d=rasterio.open('/mnt/project-files/non-israeli-maps/Copernicus_DEM_GLO30_Arava_60m_UTM36.tif'); z=d.read(1).astype(float)
crs=d.crs
V=unary_union(g.read_file(F,layer='valley_polygon_auto_rule').to_crs(crs).geometry)
B=unary_union(g.read_file('/mnt/project-files/border-map/border1994.geojson').to_crs(crs).geometry)
# Jordan side: split DEM bbox by border line
from shapely.ops import split
bb=box(*d.bounds)
parts=split(bb, B.buffer(0.01).boundary) if False else None
# use polygonize: border line extended to bbox edges
import shapely
pieces=list(shapely.ops.polygonize(unary_union([bb.boundary, B.intersection(bb)])))
east=max(pieces,key=lambda p:p.centroid.x) if len(pieces)==2 else None
print('pieces',len(pieces))
pieces=sorted(pieces,key=lambda p:-p.area)
# pick the piece(s) whose centroid is east of border at same northing
def is_east(p):
    c=p.representative_point(); 
    nearest=shapely.ops.nearest_points(B,c)[0]; return c.x>nearest.x
from shapely.geometry import Polygon
from shapely.ops import linemerge
lm=linemerge(B) if B.geom_type=='MultiLineString' else B
geoms=getattr(lm,'geoms',[lm]); ln=max(geoms,key=lambda x:x.length)
cl=ln.intersection(box(d.bounds[0]-1e5,d.bounds[1]-2e4,d.bounds[2]+1e5,d.bounds[3]+2e4))
cl=max(getattr(cl,'geoms',[cl]),key=lambda x:x.length)
co=list(cl.coords)
if co[0][1]>co[-1][1]: co=co[::-1]
E=d.bounds[2]+5e4
JO=Polygon(co+[(E,co[-1][1]),(E,co[0][1])]).buffer(0)
print('JO area',JO.area/1e6)
low=(z<500)&(z>-1000)
shapes=[shape(s) for s,v in features.shapes(low.astype('uint8'),mask=low,transform=d.transform)]
L=unary_union(shapes).buffer(0)
qatar=g.GeoSeries([Point(35.0925,29.810)],crs=4326).to_crs(crs)[0]  # Qutr village 29.8183N 35.0925E (GeoNames), south edge ~29.81
north=V.bounds[3]
clip=box(d.bounds[0],qatar.y,d.bounds[2],north)
Z=L.intersection(JO).intersection(clip)
# keep component connected to valley
Z=unary_union([p for p in getattr(Z,'geoms',[Z]) if p.intersects(V)])
Vj=V.intersection(JO).intersection(clip)
inside=Vj.intersection(Z).area/Vj.area
print('JVA zone km2',Z.area/1e6,'valley JO part (Qatar->north) km2',Vj.area/1e6,'inside',inside)
g.GeoDataFrame({'name':['JVA_law_1988_area2_500m'],'note':['Jordan side, border to 500 m contour (Copernicus GLO-30, 60 m), Qatar village (approx) to valley north line']},geometry=[Z],crs=crs).to_file(OUT+'JVA_law_zone_vs_valley.gpkg',layer='jva_law_zone_500m')
g.GeoDataFrame(geometry=[Vj],crs=crs).to_file(OUT+'JVA_law_zone_vs_valley.gpkg',layer='final_valley_jordan_part')
# east-edge gap to 500 m contour per section
c=g.read_file(F,layer='cross_sections_250m').to_crs(crs)
c=c[c.geometry.centroid.y>qatar.y]
gaps=[]
for _,r in c.iterrows():
    a=r.geometry.intersection(V); b=r.geometry.intersection(Z)
    if a.is_empty or b.is_empty: continue
    gaps.append((r.s_km,(b.bounds[2]-a.bounds[2])/1000))
gp=np.array(gaps); np.savetxt(OUT+'jva_500m_minus_valley_east_edge_km.csv',gp,delimiter=',',header='s_km,gap_km',comments='',fmt='%.2f')
print('east gap km median/5/95',np.median(gp[:,1]),np.percentile(gp[:,1],5),np.percentile(gp[:,1],95), (gp[:,1]<0).mean())
