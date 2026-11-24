import geopandas as gpd, pandas as pd, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from shapely.geometry import Point
FV='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
G=gpd.read_file('/mnt/project-files/gmba-test/GMBA_def_v2_Arava.gpkg').to_crs(2039)
V=gpd.read_file(FV,layer='valley_polygon_auto_rule').to_crs(2039)
S=gpd.read_file(FV,layer='straight_line').to_crs(2039)
d=pd.read_csv('/mnt/project-files/gmba-test/gmba_edges_per_section.csv')
fig,(a,b)=plt.subplots(1,2,figsize=(11,10),gridspec_kw={'width_ratios':[1,1.05]})
G.iloc[[0]].plot(ax=a,color='#f3dc7a',alpha=.6,lw=0)
G.iloc[[1]].plot(ax=a,color='#c9a27e',lw=0)
O=gpd.read_file('/mnt/project-files/gmba-test/GMBA_Arava_layers.gpkg',layer='gmba_official_2021_mountains')
O.boundary.plot(ax=a,color='#5d3a1a',lw=.7,ls='--')
V.boundary.plot(ax=a,color='#6a1b9a',lw=1.3); S.plot(ax=a,color='red',lw=1)
pl=[('Eilat',34.951,29.557,-1),('Aqaba',35.006,29.53,1),('Gharandal',35.18,30.03,1),('Yotvata',35.06,29.89,-1),
    ('Wadi Fidan',35.37,30.65,1),('Hatzeva',35.25,30.78,-1),('Dead Sea',35.42,31.08,1)]
P=gpd.GeoSeries([Point(x,y) for _,x,y,_ in pl],crs=4326).to_crs(2039)
for (n,_,_,s),p in zip(pl,P):
    a.plot(p.x,p.y,'ko',ms=3); a.annotate(n,(p.x,p.y),xytext=(6*s,2),textcoords='offset points',ha='left' if s>0 else 'right',fontsize=8,
        bbox=dict(fc='white',ec='none',alpha=.75,pad=.5))
x0,y0,x1,y1=V.total_bounds; a.set_xlim(x0-25000,x1+25000); a.set_ylim(y0-8000,y1+8000); a.set_xticks([]); a.set_yticks([]); a.set_xlabel(''); a.set_ylabel(''); a.set_aspect('equal')
a.legend(handles=[Patch(color='#c9a27e',label='Mountains, GMBA v2.0'),Patch(color='#f3dc7a',alpha=.6,label='Valley according to GMBA'),
    Line2D([],[],color='#5d3a1a',lw=.7,ls='--',label='Official GMBA mountain mask 2021 (1 km)'),Line2D([],[],color='#6a1b9a',label='Final valley (this study)'),Line2D([],[],color='red',label='Straight line Dead Sea – Eilat')],loc='lower right',fontsize=7,framealpha=.9)
a.set_title('GMBA v2.0 mountains vs final valley',fontsize=10)
b.axvspan(-1,1,color='0.9'); b.axvline(0,color='k',lw=.8)
b.plot(d.E_diff_km,d.s_km,lw=1,label='East side'); b.plot(d.W_diff_km,d.s_km,lw=1,label='West side')
b.set_xlim(-6,12); b.set_ylim(0,180); b.set_ylabel('km along the valley from Eilat (north = up)')
b.set_xlabel('GMBA mountain start minus final valley edge (km); + = GMBA valley wider'); b.legend(fontsize=8)
b.set_title('Per 250 m cross-section (gap = no mountain within 25 km)',fontsize=10)
fig.text(.5,.005,'PhD research of Shimon Frish, Technion (supervisors Prof. Maxim Shoshany, Prof. Aviad Shapira). All rights reserved.',ha='center',fontsize=7,color='0.4')
plt.tight_layout(rect=(0,.015,1,1)); plt.savefig('/mnt/project-files/gmba-test/gmba_v2_vs_final_valley.png',dpi=120)
