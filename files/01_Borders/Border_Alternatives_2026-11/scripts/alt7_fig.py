import geopandas as gpd, pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['font.family']='DejaVu Sans'
O='/mnt/project-files/border-alternatives/'
G=O+'Border_alternative_7_Sharon_line.gpkg'
seg=gpd.read_file(G,layer='alt7_sharon_line_by_source'); ar=gpd.read_file(G,layer='alt7_vs_armistice_areas')
arm=gpd.read_file('/mnt/user-data/uploads/Israel-Jordan-Arava/01_Borders/Armistice_line_hist_maps_grid_ITM.gpkg').to_crs(2039)
b94=gpd.read_file('/mnt/project-files/border-map/border1994.geojson').to_crs(2039)
df=pd.read_csv(O+'alt7_offsets_per_250m.csv')
col={'trail_sheet14_1993':'#7b2cbf','trail_sheet17_1991':'#c77dff','yahel_before_treaty':'#1d4ed8','yotvata_before_treaty':'#0ea5e9','armistice_line_gap':'#9ca3af'}
lab={'trail_sheet14_1993':'Trail map sheet 14 (Oct 1993)','trail_sheet17_1991':'Trail map sheet 17 (Nov 1991)','yahel_before_treaty':'Yahel "before treaty" map','yotvata_before_treaty':'Yotvata "before treaty" map','armistice_line_gap':'Gap filled with armistice line'}
fig=plt.figure(figsize=(15,11))
a=fig.add_axes([0.03,0.05,0.30,0.9])
arm.plot(ax=a,color='k',lw=0.8); b94.plot(ax=a,color='#dc2626',lw=0.8)
for k,c in col.items():
    s=seg[seg.source==k]
    if len(s): s.plot(ax=a,color=c,lw=2.2,label=lab[k])
a.plot([],[],color='k',lw=0.8,label='Armistice line (hist. maps)'); a.plot([],[],color='#dc2626',lw=0.8,label='1994 treaty border')
a.set_xlim(190000,250000); a.set_ylim(380000,545000); a.set_aspect('equal'); a.legend(loc='lower right',fontsize=8); a.set_title('Alternative 7 - "Sharon line" (de facto, 1980s-early 1990s)',fontsize=10); a.tick_params(labelsize=7)
b=fig.add_axes([0.40,0.55,0.57,0.38])
b.axhline(0,color='k',lw=0.8)
for k,c in col.items():
    s=df[df.source==k]; b.scatter(s.northing/1000,s.dx_vs_armistice_m,s=5,color=c)
b.plot(df.northing/1000,df.dx_vs_1994_m,color='#dc2626',lw=0.6,alpha=0.6,label='Alt 7 minus 1994 border')
b.set_xlabel('ITM northing (km)  - south (Eilat) to north (Dead Sea)'); b.set_ylabel('Alt 7 minus armistice line (m, + = east)'); b.legend(fontsize=8); b.set_ylim(-1500,1500); b.grid(alpha=.3)
for (x0,x1,y0,y1,t),pos in zip([(222000,232000,503000,515000,'Ein Yahav - Hatzeva'),(211000,220000,440000,457000,'Yahel')],[[0.40,0.05,0.27,0.42],[0.70,0.05,0.27,0.42]]):
    c=fig.add_axes(pos)
    if len(ar): ar[ar.side.str.startswith('alt7_east')].plot(ax=c,color='#fde68a')
    arm.plot(ax=c,color='k',lw=1); b94.plot(ax=c,color='#dc2626',lw=1)
    for k,cc in col.items():
        s=seg[seg.source==k]
        if len(s): s.plot(ax=c,color=cc,lw=2)
    c.set_xlim(x0,x1); c.set_ylim(y0,y1); c.set_aspect('equal'); c.set_title(t+' (yellow = east of armistice line)',fontsize=9); c.tick_params(labelsize=6)
fig.text(0.5,0.005,'PhD research of Shimon Frish, Technion (supervisors Prof. Maxim Shoshany, Prof. Aviad Shapira). All rights reserved.',ha='center',fontsize=7)
plt.savefig(O+'alt7_sharon_line.png',dpi=110)
