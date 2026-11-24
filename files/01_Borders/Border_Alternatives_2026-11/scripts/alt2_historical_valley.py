# Alternative 2: valley edges per historical / non-Israeli maps, per 250 m cross-section; centre line = midpoint.
import numpy as np, geopandas as gpd, pandas as pd, json
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
FV='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
X=gpd.read_file(FV,layer='cross_sections_250m'); C=gpd.read_file(FV,layer='valley_centre_points').set_index('section')
CRS=X.crs
NI='/mnt/project-files/non-israeli-maps/'
def rd(f,l=None): return gpd.read_file(f,layer=l).to_crs(CRS)
POLY={'Bender1968':rd('/mnt/project-files/valley-from-bender1968/Arava_valley_from_Bender1968.gpkg','valley_polygon_bender1968').union_all(),
      'USGS_Bender1974':rd('/mnt/project-files/valley-from-jordan-geology/Arava_valley_from_Jordan_geology.gpkg','valley_polygon_geology').union_all(),
      'AtlasJordan2013':rd(NI+'Atlas_of_Jordan_2013_depression_unit.gpkg').union_all(),
      'K737_1960':rd(NI+'Non_Israeli_maps_valley_delineations.gpkg','K737_3049III_valley_floor_mapped').union_all()}
LINE={'AMS_K502_1961':rd(NI+'Non_Israeli_maps_valley_delineations.gpkg','AMS_K502_east_mountain_front').union_all(),
      'Tourist1962':rd(NI+'Non_Israeli_maps_valley_delineations.gpkg','Tourist1962_first_contour_south').union_all(),
      'Powell2015':rd(NI+'Non_Israeli_maps_valley_delineations.gpkg','Powell2015_fig2a_mountain_foot').union_all()}
R=25000
rows=[]
for _,r in X.iterrows():
    a,b=np.array(r.geometry.coords[0]),np.array(r.geometry.coords[-1]); u=(b-a)/np.linalg.norm(b-a)
    if u[0]<0: u=-u
    c=np.array(C.loc[r.section].geometry.coords[0]); cp=Point(c)
    L=LineString([tuple(c-R*u),tuple(c+R*u)])
    out={'section':int(r.section),'s_km':r.s_km}
    for k,P in POLY.items():
        I=L.intersection(P); segs=[g for g in getattr(I,'geoms',[I]) if g.geom_type=='LineString' and g.length>0]
        dE=dW=np.nan
        if segs:
            s=min(segs,key=lambda g:g.distance(cp))
            if s.distance(cp)<3000 and s.length>500:
                t=[L.project(Point(q)) for q in s.coords]; dE=max(t)-R; dW=R-min(t)
                if dE<0 or dW<0: dE=dW=np.nan   # segment entirely on one side: not a valley crossing
        out[k+'_E']=dE; out[k+'_W']=dW
    for k,Ln in LINE.items():
        I=L.intersection(Ln); pts=[g for g in getattr(I,'geoms',[I]) if g.geom_type=='Point']
        t=[L.project(p)-R for p in pts if L.project(p)-R>0]
        out[k+'_E']=min(t) if t else np.nan
    out['cx'],out['cy'],out['ux'],out['uy']=c[0],c[1],u[0],u[1]
    rows.append(out)
D=pd.DataFrame(rows)
Ecols=[c for c in D if c.endswith('_E') and not c.startswith('hist')]; Wcols=[c for c in D if c.endswith('_W')]
D['hist_E']=D[Ecols].median(axis=1); D['hist_W']=D[Wcols].median(axis=1)
D['nE']=D[Ecols].notna().sum(axis=1); D['nW']=D[Wcols].notna().sum(axis=1)
for s in ('hist_E','hist_W'):
    D[s]=D[s].interpolate(limit_direction='both').rolling(9,center=True,min_periods=1).median()   # ~2 km running median
D['hist_centre_off']=(D.hist_E-D.hist_W)/2   # + = east of project centre point
D['hist_width_km']=(D.hist_E+D.hist_W)/1000
D.to_csv('/mnt/project-files/border-alternatives/alt2_historical_edges_per_section.csv',index=False)
P=lambda d,sg: [(x+sg*d_*ux,y+sg*d_*uy) for x,y,ux,uy,d_ in zip(D.cx,D.cy,D.ux,D.uy,d)]
east=P(D.hist_E,1); west=P(D.hist_W,-1)
poly=Polygon(east+west[::-1]).buffer(0)
cen=np.array(P(D.hist_centre_off,1)); k=9
cs=np.vstack([np.convolve(np.pad(cen[:,i],k//2,mode='edge'),np.ones(k)/k,mode='valid') for i in range(2)]).T
cl=LineString(cs)
g=gpd.GeoDataFrame({'name':['עמק הערבה לפי מפות היסטוריות ולא-ישראליות (חציון)','חלופה 2: קו מרכז העמק לפי עדויות היסטוריות']},geometry=[poly,cl],crs=CRS).to_crs(2039)
g.iloc[[0]].to_file('/tmp/claude-0/alt/alt2.gpkg',layer='historical_valley_polygon',driver='GPKG')
g.iloc[[1]].to_file('/tmp/claude-0/alt/alt2.gpkg',layer='alt2_historical_centre_line',driver='GPKG')
V=gpd.read_file(FV,layer='valley_polygon_auto_rule').to_crs(2039).union_all(); H=g.geometry.iloc[0]
cnt={k:int(D[k].notna().sum()) for k in Ecols+Wcols}
res={'area_km2':round(H.area/1e6,1),'IoU_vs_final':round(H.intersection(V).area/H.union(V).area,3),'median_width_km':round(D.hist_width_km.median(),2),
 'centre_offset_vs_project_centre_median_km':round(D.hist_centre_off.median()/1000,2),'abs_p90_km':round(D.hist_centre_off.abs().quantile(.9)/1000,2),'sections_with_source':cnt,
 'sections_nE0':int((D.nE==0).sum()),'sections_nW0':int((D.nW==0).sum())}
print(json.dumps(res,indent=1,ensure_ascii=False)); json.dump(res,open('/mnt/project-files/border-alternatives/alt2_summary.json','w'),indent=1)
