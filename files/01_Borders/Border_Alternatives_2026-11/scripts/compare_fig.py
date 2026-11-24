import numpy as np, geopandas as gpd, pandas as pd, json, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from shapely.geometry import LineString, Point
FV='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'; O='/mnt/project-files/border-alternatives/'
X=gpd.read_file(FV,layer='cross_sections_250m'); C=gpd.read_file(FV,layer='valley_centre_points').set_index('section'); CRS=X.crs
lines={'alt2':gpd.read_file(O+'Border_alternatives_2_4_historical.gpkg',layer='alt2_historical_centre_line').to_crs(CRS).geometry.iloc[0],
 'alt3':gpd.read_file(FV,layer='valley_centre_line').to_crs(CRS).geometry.iloc[0],
 'alt4':gpd.read_file(O+'Border_alternatives_2_4_historical.gpkg',layer='alt4_historical_thalweg_line').to_crs(CRS).geometry.iloc[0],
 'alt5':gpd.read_file(FV,layer='thalweg_line').to_crs(CRS).geometry.iloc[0],
 'alt1':gpd.read_file('/mnt/project-files/border-alternatives/src/Mandate_border_1942_digitized.gpkg').to_crs(CRS).union_all() if False else None}
rows=[]
for _,r in X.iterrows():
    a,b=np.array(r.geometry.coords[0]),np.array(r.geometry.coords[-1]); u=(b-a)/np.linalg.norm(b-a)
    if u[0]<0: u=-u
    c=np.array(C.loc[r.section].geometry.coords[0]); L=LineString([tuple(c-30000*u),tuple(c+30000*u)])
    o={'section':int(r.section),'s_km':r.s_km}
    for k,g in lines.items():
        if g is None: continue
        I=L.intersection(g); pts=[p for p in getattr(I,'geoms',[I]) if p.geom_type=='Point']
        o[k]=(min([L.project(p)-30000 for p in pts],key=abs)/1000) if pts else np.nan   # km, + = east of project centre point
    rows.append(o)
D=pd.DataFrame(rows); D['alt2_minus_alt3']=D.alt2-D.alt3; D['alt4_minus_alt5']=D.alt4-D.alt5; D['alt4_minus_alt2']=D.alt4-D.alt2
D.to_csv(O+'alternatives_offsets_per_section.csv',index=False)
st=lambda v: {'median_km':round(v.median(),2),'median_abs_km':round(v.abs().median(),2),'within_1km_pct':round(100*(v.abs()<=1).mean(),1),'max_abs_km':round(v.abs().max(),2),'east_pct':round(100*(v>0).mean(),1)}
S={k:st(D[k].dropna()) for k in ['alt2_minus_alt3','alt4_minus_alt5','alt4_minus_alt2']}
for a_,b_ in [(0,60),(60,120),(120,180)]:
    x=D[(D.s_km>=a_)&(D.s_km<b_)]; S[f'km{a_}-{b_}']={k:round(x[k].median(),2) for k in ['alt2_minus_alt3','alt4_minus_alt5']}
json.dump(S,open(O+'alternatives_comparison.json','w'),indent=1); print(json.dumps(S,indent=1))
# figure
E=2039
Hv=gpd.read_file(O+'Border_alternatives_2_4_historical.gpkg',layer='historical_valley_polygon').to_crs(E)
V=gpd.read_file(FV,layer='valley_polygon_auto_rule').to_crs(E); St=gpd.read_file(FV,layer='straight_line').to_crs(E)
fig,(a,b)=plt.subplots(1,2,figsize=(11,10),gridspec_kw={'width_ratios':[1,1.05]})
Hv.plot(ax=a,color='#e9dcb5',lw=0); V.boundary.plot(ax=a,color='#6a1b9a',lw=.8,ls=':'); St.plot(ax=a,color='red',lw=.8)
sty={'alt2':('#1b7a3a','-',1.6,'Alt. 2: valley centre, historical maps'),'alt3':('#1f5fbf','-',1.0,'Alt. 3: valley centre, SRTM'),
     'alt4':('#d95f02','-',1.6,'Alt. 4: thalweg, historical maps'),'alt5':('#56b4e9','--',1.0,'Alt. 5: thalweg, SRTM')}
for k,(c_,ls,lw,lab) in sty.items(): gpd.GeoSeries([lines[k]],crs=CRS).to_crs(E).plot(ax=a,color=c_,ls=ls,lw=lw)
pl=[('Eilat',34.951,29.557,-1),('Aqaba',35.006,29.53,1),('Gharandal',35.18,30.03,1),('Yotvata',35.06,29.89,-1),('Wadi Fidan',35.37,30.65,1),('Hatzeva',35.25,30.78,-1),('Dead Sea',35.42,31.08,1)]
P=gpd.GeoSeries([Point(x,y) for _,x,y,_ in pl],crs=4326).to_crs(E)
for (n,_,_,s),p in zip(pl,P):
    a.plot(p.x,p.y,'ko',ms=3); a.annotate(n,(p.x,p.y),xytext=(6*s,2),textcoords='offset points',ha='left' if s>0 else 'right',fontsize=8,bbox=dict(fc='white',ec='none',alpha=.75,pad=.5))
x0,y0,x1,y1=Hv.total_bounds; a.set_xlim(x0-12000,x1+12000); a.set_ylim(y0-5000,y1+5000); a.set_xticks([]); a.set_yticks([]); a.set_xlabel(''); a.set_ylabel(''); a.set_aspect('equal')
a.legend(handles=[Patch(color='#e9dcb5',label='Valley per historical / non-Israeli maps'),Line2D([],[],color='#6a1b9a',ls=':',label='Final valley (SRTM, this study)')]+
   [Line2D([],[],color=c_,ls=ls,lw=lw,label=lab) for c_,ls,lw,lab in sty.values()]+[Line2D([],[],color='red',lw=.8,label='Straight line Dead Sea – Eilat')],loc='lower right',fontsize=7,framealpha=.9)
a.set_title('Border alternatives 2–5',fontsize=10)
b.axvspan(-1,1,color='0.9'); b.axvline(0,color='k',lw=.8)
b.plot(D.alt2_minus_alt3,D.s_km,color='#1b7a3a',lw=1,label='Alt. 2 minus Alt. 3 (centre lines)')
b.plot(D.alt4_minus_alt5,D.s_km,color='#d95f02',lw=1,label='Alt. 4 minus Alt. 5 (thalwegs)')
b.set_ylim(0,180); b.set_xlim(-8,8); b.set_ylabel('km along the valley from Eilat (north = up)'); b.set_xlabel('Distance between lines (km); + = historical line further east')
b.legend(fontsize=8,loc='upper right'); b.set_title('Per 250 m cross-section',fontsize=10)
fig.text(.5,.005,'PhD research of Shimon Frish, Technion (supervisors Prof. Maxim Shoshany, Prof. Aviad Shapira). All rights reserved.',ha='center',fontsize=7,color='0.4')
plt.tight_layout(rect=(0,.015,1,1)); plt.savefig(O+'border_alternatives_2-5_historical_vs_SRTM.png',dpi=120)
