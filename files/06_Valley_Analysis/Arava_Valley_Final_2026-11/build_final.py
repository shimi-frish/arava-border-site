import numpy as np, geopandas as gpd, pickle, pandas as pd
from shapely.geometry import LineString, Point
OUT='Arava_valley_final_2026-11-17.gpkg'
G='/mnt/project-files/lowpass-curvature/mountain_foot/Arava_valley_mountain_foot.gpkg'
p=pickle.load(open('/tmp/claude-0/cl/lines.pkl','rb')); bd=pickle.load(open('/tmp/claude-0/cl/brit.pkl','rb'))['bd']
S=np.array(p['S']);cd=np.array(p['cd']);td=np.array(p['td']);tz=np.array(p['tz']);d0=np.array(p['d0']);d1=np.array(p['d1'])
P0=np.array([691652.47,3269661.43]); P1=np.array([734161.30,3443276.83]); u=(P1-P0)/np.linalg.norm(P1-P0); n=np.array([-u[1],u[0]])
pt=lambda s,d: P0+u*s+n*d
crs=32636
a=gpd.read_file(G,layer='valley_polygon_auto_rule'); a['name']='עמק הערבה – כלל אוטומטי (שלבים 1–3)'
a.to_file(OUT,layer='valley_polygon_auto_rule',driver='GPKG')
m=gpd.read_file(G,layer='valley_polygon_mountain_foot'); m['name']='עמק הערבה – תיחום ידני'
m.to_file(OUT,layer='valley_polygon_manual',driver='GPKG')
# edges of auto valley along sections (W = max offset since + is west)
W=LineString([pt(s,d) for s,d in zip(S,d1)]); E=LineString([pt(s,d) for s,d in zip(S,d0)])
gpd.GeoDataFrame(dict(side=['W','E'],name=['שול מערבי – כלל אוטומטי','שול מזרחי – כלל אוטומטי']),geometry=[W,E],crs=crs).to_file(OUT,layer='valley_edges_auto_per_section',driver='GPKG')
L=gpd.read_file('/tmp/claude-0/cl/lines.gpkg')
gpd.GeoDataFrame(dict(name=['מרכז העמק']),geometry=[L.geometry.iloc[0]],crs=crs).to_file(OUT,layer='valley_centre_line',driver='GPKG')
gpd.GeoDataFrame(dict(name=['תלווג']),geometry=[L.geometry.iloc[1]],crs=crs).to_file(OUT,layer='thalweg_line',driver='GPKG')
df=pd.DataFrame(dict(section=np.arange(len(S))+1,s_km=S/1e3,width_km=(d1-d0)/1e3,west_edge_off_km=d1/1e3,east_edge_off_km=d0/1e3,
  centre_off_km=cd/1e3,thalweg_off_km=td/1e3,thalweg_z_m=np.round(tz,1),mandate1942_off_km=bd/1e3))
df['thalweg_minus_centre_km']=(td-cd)/1e3; df['mandate_minus_thalweg_km']=(bd-td)/1e3; df['mandate_minus_centre_km']=(bd-cd)/1e3
df=df.round(3)
sec=gpd.GeoDataFrame(df.copy(),geometry=[LineString([pt(s,a_),pt(s,b_)]) for s,a_,b_ in zip(S,d1,d0)],crs=crs)
sec.to_file(OUT,layer='cross_sections_250m',driver='GPKG')
cp=gpd.GeoDataFrame(df[['section','s_km','width_km','centre_off_km']].copy(),geometry=[Point(pt(s,d)) for s,d in zip(S,cd)],crs=crs); cp.to_file(OUT,layer='valley_centre_points',driver='GPKG')
tp=gpd.GeoDataFrame(df[['section','s_km','thalweg_off_km','thalweg_z_m']].copy(),geometry=[Point(pt(s,d)) for s,d in zip(S,td)],crs=crs); tp.to_file(OUT,layer='thalweg_points',driver='GPKG')
for l in ['mountain_foot_lines','mountain_foot_points_per_section','mountain_mask','test_cells']:
    gpd.read_file(G,layer=l).to_file(OUT,layer=l,driver='GPKG')
st=gpd.read_file('/mnt/project-files/border-map/main_streams_20km2.gpkg',layer='streams'); st.to_file(OUT,layer='main_streams_20km2',driver='GPKG')
gpd.read_file('/tmp/claude-0/bm/osm_named_streams.gpkg').to_file(OUT,layer='stream_names_osm',driver='GPKG')
gpd.GeoDataFrame(dict(name=['קו ישר אילת – ים המלח'],length_km=[178.7]),geometry=[LineString([P0,P1])],crs=crs).to_file(OUT,layer='straight_line',driver='GPKG')
df.to_csv('valley_sections_stats_2026-11-17.csv',index=False,encoding='utf-8-sig')
import pyogrio; print(pyogrio.list_layers(OUT))
print(df.describe().T[['mean','50%']])
