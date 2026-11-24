# Official GMBA mountain mask (release 4, 2021, Körner et al. 2011 rule: 3x3 range >= 200 m on EarthEnv GMTED 1 km), Arava crop
import numpy as np, rasterio, geopandas as gpd, rasterio.features as rf, json
from rasterio.transform import from_origin
from shapely.geometry import shape
from shapely.ops import unary_union
h=open('/mnt/project-files/gmba-test/official_v1_2021/arava_crop_mask_hex.txt').read().strip()
b=np.array([int(c) for c in ''.join(format(int(x,16),'04b') for x in h)[:38437]],dtype='uint8').reshape(289,133)
res=1/120; T=from_origin(-180+25764*res,84-6276*res,res,res)
out='/mnt/project-files/gmba-test/official_v1_2021/GMBA_2021_MntnMask_EarthEnv_30s_V2_Arava_crop.tif'
with rasterio.open(out,'w',driver='GTiff',height=289,width=133,count=1,dtype='uint8',crs='EPSG:4326',transform=T,compress='deflate') as d: d.write(b,1)
M=unary_union([shape(g) for g,v in rf.shapes(b,mask=b==1,transform=T)])
Mg=gpd.GeoSeries([M],crs=4326).to_crs(2039)
FV='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
V=gpd.read_file(FV,layer='valley_polygon_auto_rule').to_crs(2039).union_all()
S=gpd.read_file(FV,layer='straight_line').to_crs(2039).geometry.iloc[0]
G=gpd.read_file('/mnt/project-files/gmba-test/GMBA_def_v2_Arava.gpkg').to_crs(2039)
box=S.buffer(20000)
nonm=box.difference(Mg.iloc[0])
parts=[p for p in getattr(nonm,'geoms',[nonm]) if p.intersects(S)]
Vo=unary_union(parts)
iou=V.intersection(Vo).area/V.union(Vo).area
r={'official_v1_valley_km2':round(Vo.area/1e6,1),'IoU_vs_final':round(iou,3),'final_inside_pct':round(100*V.intersection(Vo).area/V.area,1),
   'final_valley_overlapping_official_mountain_km2':round(V.intersection(Mg.iloc[0]).area/1e6,1),
   'v2_mine_vs_official_v1_IoU_mountain_in_box':round(G.geometry.iloc[1].intersection(box).intersection(Mg.iloc[0]).area/G.geometry.iloc[1].intersection(box).union(Mg.iloc[0].intersection(box)).area,3)}
print(json.dumps(r,indent=1)); json.dump(r,open('/mnt/project-files/gmba-test/official_v1_2021/official_v1_vs_final.json','w'),indent=1)
gpd.GeoDataFrame({'name':['GMBA official 2021 mountain mask (Arava crop)','Valley per official GMBA mask']},geometry=[Mg.iloc[0].intersection(box.buffer(15000)),Vo],crs=2039).to_file('/mnt/project-files/gmba-test/official_v1_2021/official_mask_tmp.gpkg')
