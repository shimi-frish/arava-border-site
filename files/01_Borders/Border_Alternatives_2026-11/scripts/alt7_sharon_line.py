# Alternative 7: "Sharon line" = de facto Israel-Jordan line of the 1980s - early 1990s.
# Sources: Survey of Israel / SPNI trail-marking maps 1:50,000 sheet 14 (Oct 1993) and sheet 17 (Nov 1991) -> purple border band;
# local "before the peace treaty" maps (blue dashed) at Yahel and Yotvata; armistice line (hist maps) to fill gaps.
import numpy as np, geopandas as gpd, rasterio, shapely, json
from rasterio.features import rasterize
from scipy import ndimage as ndi
from scipy.signal import medfilt
from shapely.geometry import LineString, Point
from shapely.ops import polygonize, unary_union, substring
from pyproj import Transformer
from affine import Affine
from PIL import Image
U='/mnt/user-data/uploads/Israel-Jordan-Arava/'; S='/tmp/claude-0/s7/'
OUT='/mnt/project-files/border-alternatives/'
arm=gpd.read_file(U+'01_Borders/Armistice_line_hist_maps_grid_ITM.gpkg').to_crs(2039)
# armistice: 4 sheet pieces (with small gaps) -> one N->S LineString
_parts=[]
for g in arm.geometry:
    for p in getattr(shapely.line_merge(g),'geoms',[shapely.line_merge(g)]):
        c=list(p.coords); c=c if c[0][1]>c[-1][1] else c[::-1]; _parts.append(c)
_parts.sort(key=lambda c:-c[0][1])
ARM=LineString([q for c in _parts for q in c]); GL=[ARM]
print('armistice parts',len(_parts),'length km',round(ARM.length/1000,1))
B94=gpd.read_file('/mnt/project-files/border-map/border1994.geojson').to_crs(2039).union_all()
T28=Transformer.from_crs(28193,2039,always_xy=True); T38=Transformer.from_crs(3857,2039,always_xy=True)

def trail(s):
    d=rasterio.open(U+f'99_Archive/_tmp_trail/{s}_10m.tif'); R,G,B=d.read().astype(int)
    m=rasterize([arm.to_crs(d.crs).buffer(4000).union_all()],out_shape=R.shape,transform=d.transform)>0
    pur=(R>140)&(B>140)&(R-G>=25)&(B-G>=25)&(np.abs(R-B)<40)&m
    pur=ndi.binary_closing(pur,np.ones((5,5)))
    lab,n=ndi.label(pur); sz=ndi.sum(pur,lab,range(1,n+1)); sl=ndi.find_objects(lab)
    keep=np.zeros(n+1,bool)
    for i,(z,o) in enumerate(zip(sz,sl)):
        if (o[0].stop-o[0].start)>150 and z>800: keep[i+1]=True
    pm=keep[lab]; P=[]
    for r in range(0,R.shape[0],5):
        cols=np.where(pm[r])[0]
        if len(cols)==0: continue
        run=np.split(cols,np.where(np.diff(cols)>3)[0]+1)[-1]
        if 3<=len(run)<=40:
            x,y=d.transform*((run[0]+run[-1])/2+0.5,r+0.5); P.append((x,y))
    P=np.array(P); x,y=T28.transform(P[:,0],P[:,1])
    x=medfilt(x,7); return np.c_[x,y]

def local(img,t,shift,dark_blue=True):
    a=np.array(img.convert('RGB')).astype(int); R,G,B=a[...,0],a[...,1],a[...,2]
    blue=(B>R+25)&(B>G+20)&(R<100); blue[int(a.shape[0]*0.80):]=False
    lab,n=ndi.label(ndi.binary_dilation(blue)); sz=ndi.sum(blue,lab,range(1,n+1))
    keep=np.isin(lab,1+np.where(sz>15)[0])&blue
    rr,cc=np.where(keep); P=[]
    for r in np.unique(rr//6):
        s=(rr//6)==r; P.append((cc[s].mean()+0.5,rr[s].mean()+0.5))
    P=np.array(P); X,Y=t*(P[:,0],P[:,1]); x,y=T38.transform(X,Y)
    o=np.argsort(-y); x,y=x[o]+shift[0],y[o]+shift[1]
    return np.c_[medfilt(x,5),y]

D=U+'05_Historical_Maps/A_Agreement_Border_Maps/Israeli/'
w=[float(v) for v in open(D+'קו הגבול באיזור יטבתה.jgwx').read().split()]
src={}
src['trail_sheet14_1993']=trail('sheet14')
src['trail_sheet17_1991']=trail('sheet17')
src['yahel_before_treaty']=local(Image.open(D+'הגבול לידי יהל לפני ואחרי הסכם השלום.tif'),rasterio.open(D+'הגבול לידי יהל לפני ואחרי הסכם השלום.tif').transform,(-350,50))
src['yotvata_before_treaty']=local(Image.open(D+'קו הגבול באיזור יטבתה.jpg'),Affine(w[0],w[2],w[4],w[1],w[3],w[5])*Affine.translation(-0.5,-0.5),(0,0))
# order pieces N->S, clip overlaps (sheet14 has priority north of its southern end)
s14=src['trail_sheet14_1993']; s17=src['trail_sheet17_1991']
y14min=s14[:,1].min(); s17=s17[s17[:,1]<y14min-50]; src['trail_sheet17_1991']=s17
pieces=[]
for k in ['trail_sheet14_1993','trail_sheet17_1991','yahel_before_treaty','yotvata_before_treaty']:
    p=src[k]; p=p[np.argsort(-p[:,1])]
    L=LineString(p).simplify(15); pieces.append((k,L))
# armistice fillers between pieces + south to Eilat
def arm_between(y1,y2):  # y1>y2, piece of armistice by northing
    # sample armistice densely and cut by y
    c=np.array([g.interpolate(d).coords[0] for g in GL for d in np.arange(0,g.length,25)])
    s=(c[:,1]<y1)&(c[:,1]>y2); c=c[s]; c=c[np.argsort(-c[:,1])]
    return LineString(c) if len(c)>1 else None
segs=[]; prev_end=None
ybot,ytop=ARM.bounds[1],ARM.bounds[3]; print('ARM',ARM.length,ARM.bounds)
for i,(k,L) in enumerate(pieces):
    y0=L.coords[0][1]; y1=L.coords[-1][1]
    if prev_end is not None and prev_end-y0>1000:
        a=arm_between(prev_end,y0)
        if a: segs.append(('armistice_line_gap',a))
    elif prev_end is None and ytop-y0>300:
        a=arm_between(ytop+1,y0)
        if a: segs.append(('armistice_line_gap',a))
    segs.append((k,L)); prev_end=y1
a=arm_between(prev_end,ybot-1)
if a: segs.append(('armistice_line_gap',a))
coords=[]
for k,L in segs: coords+=list(L.coords)
FULL=LineString(coords)
SRC_HE={'trail_sheet14_1993':'מפת טיולים וסימון שבילים גיליון 14 (אוקטובר 1993)','trail_sheet17_1991':'מפת טיולים וסימון שבילים גיליון 17 (נובמבר 1991)',
        'yahel_before_treaty':'מפת "הגבול ליד יהל - לפני ואחרי הסכם השלום" (קו כחול מקווקו)','yotvata_before_treaty':'מפת "הגבול ליד יטבתה - לפני ואחרי הסכם השלום" (קו כחול מקווקו)',
        'armistice_line_gap':'קו שביתת הנשק (מפות היסטוריות) - השלמה במקום שאין מקור'}
seg_gdf=gpd.GeoDataFrame({'source':[k for k,_ in segs],'source_he':[SRC_HE[k] for k,_ in segs],'length_km':[round(L.length/1000,2) for _,L in segs]},geometry=[L for _,L in segs],crs=2039)
full=gpd.GeoDataFrame({'name':['Alt 7 - Sharon line (de facto 1980s-early 1990s)'],'name_he':['חלופה 7 - קו שרון (הקו בפועל, שנות ה-80 ותחילת ה-90)'],'length_km':[round(FULL.length/1000,1)]},geometry=[FULL],crs=2039)
# offsets vs armistice and 1994 every 250 m of northing
def xs(line,y):
    I=line.intersection(LineString([(150000,y),(270000,y)]))
    return [p.x for p in getattr(I,'geoms',[I]) if p.geom_type=='Point']
rows=[]
for y in np.arange(ybot+125,ytop,250):
    a=xs(FULL,y); b=xs(ARM,y); c=xs(B94,y)
    if not a or not b: continue
    xa=np.median(a); xb=min(b,key=lambda v:abs(v-xa)); xc=min(c,key=lambda v:abs(v-xa)) if c else np.nan
    src_=seg_gdf.geometry.distance(Point(xa,y)).idxmin()
    rows.append({'northing':int(y),'x_alt7':round(xa,1),'dx_vs_armistice_m':round(xa-xb,1),'dx_vs_1994_m':round(xa-xc,1) if c else None,'source':seg_gdf.source[src_]})
import pandas as pd
df=pd.DataFrame(rows); df.to_csv(OUT+'alt7_offsets_per_250m.csv',index=False)
# areas between alt7 and armistice
polys=list(polygonize(unary_union([FULL,ARM])))
P=[]
for p in polys:
    if p.area<20000: continue
    r=p.representative_point(); xa=xs(FULL,r.y); xb=xs(ARM,r.y)
    side='alt7_east_of_armistice (Israeli de facto gain)' if (xa and xb and np.median(xa)>np.median(xb)) else 'alt7_west_of_armistice'
    P.append({'side':side,'area_km2':round(p.area/1e6,3),'geometry':p})
pg=gpd.GeoDataFrame(P,crs=2039) if P else gpd.GeoDataFrame({'side':[],'area_km2':[]},geometry=[],crs=2039)
G=OUT+'Border_alternative_7_Sharon_line.gpkg'
full.to_file(G,layer='alt7_sharon_line',driver='GPKG')
seg_gdf.to_file(G,layer='alt7_sharon_line_by_source',driver='GPKG')
pg.to_file(G,layer='alt7_vs_armistice_areas',driver='GPKG')
tr=df[df.source.str.startswith('trail')|df.source.str.contains('before')]
summ={'length_km':round(FULL.length/1000,1),
 'share_from_period_sources_pct':round(100*seg_gdf[seg_gdf.source!='armistice_line_gap'].length.sum()/FULL.length,1),
 'by_source_km':seg_gdf.groupby('source').length_km.sum().round(1).to_dict(),
 'dx_vs_armistice_all':{'median_abs_m':round(df.dx_vs_armistice_m.abs().median()),'p90_abs_m':round(df.dx_vs_armistice_m.abs().quantile(.9)),'max_abs_m':round(df.dx_vs_armistice_m.abs().max())},
 'dx_vs_armistice_period_sources':{'median_abs_m':round(tr.dx_vs_armistice_m.abs().median()),'share_over_300m_pct':round(100*(tr.dx_vs_armistice_m.abs()>300).mean(),1),'max_east_m':round(tr.dx_vs_armistice_m.max()),'max_west_m':round(tr.dx_vs_armistice_m.min())},
 'dx_vs_1994_period_sources':{'median_abs_m':round(tr.dx_vs_1994_m.abs().median())},
 'areas_east_of_armistice_km2':round(pg[pg.side.str.startswith('alt7_east')].area_km2.sum(),2) if len(pg) else 0,
 'areas_west_of_armistice_km2':round(pg[pg.side=='alt7_west_of_armistice'].area_km2.sum(),2) if len(pg) else 0,
 'yahel_map_shift_applied_m':[-350,50]}
json.dump(summ,open(OUT+'alt7_summary.json','w'),ensure_ascii=False,indent=1); print(json.dumps(summ,ensure_ascii=False,indent=1))
print(seg_gdf[['source','length_km']])
