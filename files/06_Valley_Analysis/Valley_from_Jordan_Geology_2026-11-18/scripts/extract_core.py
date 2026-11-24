import geopandas as gpd
from shapely.geometry import box, Polygon
from shapely.ops import unary_union
FV='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
g=gpd.read_file('/mnt/project-files/jordan-geology/Jordan_geology_Kempf2023_ITM.gpkg')
V=gpd.read_file(FV,layer='valley_polygon_auto_rule').to_crs(2039)
b=gpd.read_file('/mnt/project-files/border-map/border1994.geojson').to_crs(2039)
YN=V.total_bounds[3]; R=500
q=g[g.unit_code.isin(['Qs1','Qs2','Qs3','Qs4','Qs5'])]
U=unary_union(list(q.geometry.buffer(1))).buffer(-1).intersection(box(150000,370000,320000,YN))
O=U.buffer(-R).buffer(R)
Bd=unary_union(list(b.geometry)).intersection(box(150000,370000,320000,YN))
P=unary_union([p for p in getattr(O,'geoms',[O]) if p.intersects(Bd.buffer(500)) and p.area>2e6])
P=unary_union([Polygon(p.exterior,[i for i in p.interiors if Polygon(i).area>2e6]) for p in getattr(P,'geoms',[P])])
