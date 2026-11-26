# Alt 8 (pre-treaty official Israeli line): replace the armistice-line fill segments
# with the border traced from trail-marking sheets 19 (1998) and 20 (Aug 1996), per Shimi 2026-11-25.
# NOTE: both sheets were printed AFTER the 1994 treaty; they show essentially the 1994 border.
import numpy as np, geopandas as gpd, shapely, json, pandas as pd
from shapely.geometry import LineString, Point
from shapely.ops import polygonize, unary_union
OUT='/mnt/project-files/border-alternatives/'; G=OUT+'Border_alternative_7_Sharon_line.gpkg'
BK=OUT+'backup_before_sheets19_20_2026-11-25/Border_alternative_7_Sharon_line.gpkg'
U='/mnt/user-data/uploads/Israel-Jordan-Arava/'
arm=gpd.read_file(U+'01_Borders/Armistice_line_hist_maps_grid_ITM.gpkg').to_crs(2039)
_parts=[]
for g in arm.geometry:
    for p in getattr(shapely.line_merge(g),'geoms',[shapely.line_merge(g)]):
        c=list(p.coords); c=c if c[0][1]>c[-1][1] else c[::-1]; _parts.append(c)
_parts.sort(key=lambda c:-c[0][1]); ARM=LineString([q for c in _parts for q in c])
B94=gpd.read_file('/mnt/project-files/border-map/border1994.geojson').to_crs(2039).union_all()
old=gpd.read_file(BK,layer='alt7_sharon_line_by_source')
new=gpd.read_file('/tmp/claude-0/s19/trail_19_20_border.gpkg').to_crs(2039)
def ns(line):  # coords N->S
    c=np.array(line.coords); return c[np.argsort(-c[:,1])] if True else c
def cut(src,y1,y2):
    c=ns(src); c=c[(c[:,1]<y1)&(c[:,1]>y2)]; return LineString(c) if len(c)>1 else None
L19=new[new.source=='trail_sheet19_1998'].geometry.iloc[0]; L20=new[new.source=='trail_sheet20_1996'].geometry.iloc[0]
y19min=np.array(L19.coords)[:,1].min()
segs=[]
for _,r in old.iterrows():
    L=r.geometry; c=np.array(L.coords); ytop,ybot=c[:,1].max(),c[:,1].min()
    if r.source!='armistice_line_gap': segs.append((r.source,L)); continue
    # fill this gap from sheet 19 above its southern end, sheet 20 below; armistice where neither covers
    cover=[]
    a=cut(L19,ytop,max(ybot,y19min)); 
    if a: cover.append(('trail_sheet19_1998',a))
    if ybot<y19min:
        b=cut(L20,min(ytop,y19min),ybot)
        if b: cover.append(('trail_sheet20_1996',b))
    if not cover: segs.append((r.source,L)); continue
    yc_top=max(np.array(x.coords)[:,1].max() for _,x in cover); yc_bot=min(np.array(x.coords)[:,1].min() for _,x in cover)
    if ytop-yc_top>300: segs.append(('armistice_line_gap',cut(ARM,ytop+1,yc_top)))
    segs+=cover
    if yc_bot-ybot>300: segs.append(('armistice_line_gap',cut(ARM,yc_bot,ybot-1)))
segs=[(k,L) for k,L in segs if L is not None]
coords=[]
for k,L in segs: coords+=list(L.coords)
FULL=LineString(coords)
SRC_HE={'trail_sheet14_1993':'מפת טיולים וסימון שבילים גיליון 14 (אוקטובר 1993)','trail_sheet17_1991':'מפת טיולים וסימון שבילים גיליון 17 (נובמבר 1991)',
 'trail_sheet19_1998':'מפת טיולים וסימון שבילים גיליון 19 (1998, אחרי ההסכם)','trail_sheet20_1996':'מפת טיולים וסימון שבילים גיליון 20 (אוגוסט 1996, אחרי ההסכם)',
 'yahel_before_treaty':'מפת "הגבול ליד יהל - לפני ואחרי הסכם השלום" (קו כחול מקווקו)','yotvata_before_treaty':'מפת "הגבול ליד יטבתה - לפני ואחרי הסכם השלום" (קו כחול מקווקו)',
 'armistice_line_gap':'קו שביתת הנשק (מפות היסטוריות) - השלמה במקום שאין מקור'}
seg_gdf=gpd.GeoDataFrame({'source':[k for k,_ in segs],'source_he':[SRC_HE[k] for k,_ in segs],'length_km':[round(L.length/1000,2) for _,L in segs]},geometry=[L for _,L in segs],crs=2039)
full=gpd.GeoDataFrame({'name':['Alt 8 - official Israeli line before the treaty (trail-marking maps 1991-1998)'],'name_he':['חלופה 8 - הקו הרשמי הישראלי טרם ההסכם (מפות סימון שבילים; גיליונות 19-20 מ-1996/1998)'],'length_km':[round(FULL.length/1000,1)]},geometry=[FULL],crs=2039)
def xs(line,y):
    I=line.intersection(LineString([(150000,y),(270000,y)])); return [p.x for p in getattr(I,'geoms',[I]) if p.geom_type=='Point']
ybot,ytop=ARM.bounds[1],ARM.bounds[3]; rows=[]
for y in np.arange(ybot+125,ytop,250):
    a=xs(FULL,y); b=xs(ARM,y); c=xs(B94,y)
    if not a or not b: continue
    xa=np.median(a); xb=min(b,key=lambda v:abs(v-xa)); xc=min(c,key=lambda v:abs(v-xa)) if c else np.nan
    s=seg_gdf.geometry.distance(Point(xa,y)).idxmin()
    rows.append({'northing':int(y),'x_alt7':round(xa,1),'dx_vs_armistice_m':round(xa-xb,1),'dx_vs_1994_m':round(xa-xc,1) if c else None,'source':seg_gdf.source[s]})
df=pd.DataFrame(rows); df.to_csv(OUT+'alt7_offsets_per_250m.csv',index=False)
P=[]
for p in polygonize(unary_union([FULL,ARM])):
    if p.area<20000: continue
    r=p.representative_point(); xa=xs(FULL,r.y); xb=xs(ARM,r.y)
    side='alt7_east_of_armistice (Israeli de facto gain)' if (xa and xb and np.median(xa)>np.median(xb)) else 'alt7_west_of_armistice'
    P.append({'side':side,'area_km2':round(p.area/1e6,3),'geometry':p})
pg=gpd.GeoDataFrame(P,crs=2039)
full.to_file(G,layer='alt7_sharon_line',driver='GPKG',mode='w')
seg_gdf.to_file(G,layer='alt7_sharon_line_by_source',driver='GPKG')
pg.to_file(G,layer='alt7_vs_armistice_areas',driver='GPKG')
pre=df[df.source.isin(['trail_sheet14_1993','trail_sheet17_1991','yahel_before_treaty','yotvata_before_treaty'])]
post=df[df.source.isin(['trail_sheet19_1998','trail_sheet20_1996'])]
L=seg_gdf.length
summ={'length_km':round(FULL.length/1000,1),
 'share_pre_treaty_sources_pct':round(100*L[seg_gdf.source.isin(pre.source.unique())].sum()/FULL.length,1),
 'share_post_treaty_sheets_19_20_pct':round(100*L[seg_gdf.source.str.contains('19_1998|20_1996')].sum()/FULL.length,1),
 'share_armistice_fill_pct':round(100*L[seg_gdf.source=='armistice_line_gap'].sum()/FULL.length,1),
 'by_source_km':seg_gdf.groupby('source').length_km.sum().round(1).to_dict(),
 'dx_vs_armistice_all':{'median_abs_m':round(df.dx_vs_armistice_m.abs().median()),'p90_abs_m':round(df.dx_vs_armistice_m.abs().quantile(.9)),'max_abs_m':round(df.dx_vs_armistice_m.abs().max())},
 'dx_vs_armistice_pre_treaty':{'median_abs_m':round(pre.dx_vs_armistice_m.abs().median()),'max_east_m':round(pre.dx_vs_armistice_m.max()),'max_west_m':round(pre.dx_vs_armistice_m.min())},
 'dx_vs_armistice_sheets_19_20':{'median_abs_m':round(post.dx_vs_armistice_m.abs().median()),'p90_abs_m':round(post.dx_vs_armistice_m.abs().quantile(.9)),'max_east_m':round(post.dx_vs_armistice_m.max()),'max_west_m':round(post.dx_vs_armistice_m.min()),'share_east_pct':round(100*(post.dx_vs_armistice_m>0).mean(),1)},
 'dx_vs_1994_all':{'median_abs_m':round(df.dx_vs_1994_m.abs().median())},
 'dx_vs_1994_sheets_19_20':{'median_abs_m':round(post.dx_vs_1994_m.abs().median())},
 'areas_east_of_armistice_km2':round(pg[pg.side.str.startswith('alt7_east')].area_km2.sum(),2),
 'areas_west_of_armistice_km2':round(pg[pg.side=='alt7_west_of_armistice'].area_km2.sum(),2),
 'note':'sheets 19 (1998) and 20 (Aug 1996) post-date the 1994 treaty; used at the researcher request instead of the armistice-line fill'}
json.dump(summ,open(OUT+'alt7_summary.json','w'),ensure_ascii=False,indent=1); print(json.dumps(summ,ensure_ascii=False,indent=1))
print(seg_gdf[['source','length_km']])
