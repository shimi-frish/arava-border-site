import numpy as np,rasterio,geopandas as g,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from shapely.geometry import LineString
O='/mnt/project-files/non-israeli-maps/'
F='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
V=g.read_file(F,layer='valley_polygon_auto_rule').to_crs(32636)
K=g.read_file('/tmp/claude-0/dl/k737_valley.gpkg').to_crs(32636)
r=np.load('/tmp/claude-0/dl/ams_edge_s.npy')  # y, x_border, x_raw, x_ourEast, x_smooth
# GIS layers
out=O+'Non_Israeli_maps_valley_delineations.gpkg'
K.assign(source='AMS K737 1:50,000 sheet 3049 III Aqaba (1960)',method='mountain foot = edge of dense brown contour/rock shading (310 m window, fraction<0.30, opening 250 m)').to_file(out,layer='K737_3049III_valley_floor_mapped')
seg=[];cur=[r[0]]
for p in r[1:]:
    if p[0]-cur[-1][0]>300: seg.append(cur);cur=[]
    cur.append(p)
seg.append(cur)
lines=[LineString([(q[4],q[0]) for q in s]) for s in seg if len(s)>1]
g.GeoDataFrame({'source':['AMS K502 1:250,000 (1961)']*len(lines),'method':['first 1.5 km of continuous dense contours east of 1994 border; 3 km running median']*len(lines)},geometry=lines,crs=32636).to_file(out,layer='AMS_K502_east_mountain_front')
# Fig A: K737
d=rasterio.open(O+'georef/K737_3049III_Aqaba_1960_UTM36.tif'); b=d.bounds
a=d.read(out_shape=(4,d.height//2,d.width//2))
x0,x1=b.left,b.left+15000
f,ax=plt.subplots(figsize=(6.2,10.5),dpi=220)
ax.imshow(np.moveaxis(a,0,-1),extent=(b.left,b.right,b.bottom,b.top))
K.boundary.plot(ax=ax,color='#0050ff',lw=1.6); V.boundary.plot(ax=ax,color='#c000c0',lw=1.6)
ax.set_xlim(x0,x1); ax.set_ylim(b.bottom,b.top); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel('')
ax.plot([x1-6000,x1-1000],[b.bottom+1500]*2,'k',lw=3); ax.text(x1-3500,b.bottom+1900,'5 km',ha='center',fontsize=7,bbox=dict(fc='white',ec='none',pad=1))
ax.legend(handles=[Line2D([],[],color='#0050ff',lw=2,label='Valley floor as mapped on K737 (edge = mountain foot)'),Line2D([],[],color='#c000c0',lw=2,label='Arava valley – final delineation of this study')],loc='upper right',fontsize=6.5,framealpha=.9)
ax.set_title("Jordan 1:50,000, sheet 3049 III 'Aqaba (AMS Series K737, 1960)\nmapped valley floor vs. final valley",fontsize=8.5)
f.text(0.5,0.006,'Base map: U.S. Army Map Service, Series K737 Edition 1-AMS, 1960 (public domain; scan UC Berkeley Library), georeferenced on the 1 km UTM grid (700 points, RMS 12 m).\nAnalysis: Shimon Frish, PhD research, Technion (supervisors Prof. M. Shoshany, Prof. A. Shapira). All rights reserved.',ha='center',fontsize=4.6,wrap=True)
plt.tight_layout(rect=(0,0.03,1,1)); f.savefig(O+'figures/K737_Aqaba_1960_mapped_valley_vs_final.png'); f.savefig(O+'figures/K737_Aqaba_1960_mapped_valley_vs_final.pdf'); plt.close(f)
# Fig B: AMS front distance along valley
dd=(r[:,4]-r[:,3])/1000; y=(r[:,0]-3260000)/1000
gap=np.where(np.diff(r[:,0])>300)[0]
dd=np.insert(dd,gap+1,np.nan); y=np.insert(y,gap+1,(y[gap]+y[gap+1])/2)
f,ax=plt.subplots(figsize=(7.5,3.6),dpi=220)
ax.axhline(0,color='#c000c0',lw=1.4,label='East edge of final valley (this study)')
ax.fill_between(y,0,dd,where=np.nan_to_num(dd,nan=-1)>=0,color='#7fb0ff',alpha=.6,label='AMS 1961 mountain front EAST of our edge (map valley wider)')
ax.fill_between(y,0,dd,where=np.nan_to_num(dd,nan=1)<0,color='#ff9a7f',alpha=.8,label='AMS 1961 mountain front WEST of our edge')
ax.plot(y,dd,color='#0050ff',lw=.8)
for yy,t in [(3270,'Aqaba'),(3337,'Gharandal'),(3360,'W. Musa / Petra lat.'),(3392,'Feinan'),(3432,'Ghor Feifa')]:
    ax.annotate(t,(yy-3260,-3.6),fontsize=6.5,ha='center',rotation=0)
ax.set_xlabel('Northing (km north of UTM 3,260,000 m)',fontsize=7.5); ax.set_ylabel('Distance from our east edge (km)',fontsize=7.5); ax.tick_params(labelsize=7)
ax.set_ylim(-4.2,max(9,np.nanmax(dd)+.5)); ax.legend(fontsize=6,loc='upper left',framealpha=.9)
ax.set_title('Mountain front east of the Arava on AMS K502 1:250,000 (1961) vs. east edge of final valley',fontsize=8.5)
f.text(0.5,0.005,'Front = start of 1.5 km of continuous dense contours east of the 1994 border (3 km running median). Analysis: Shimon Frish, PhD research, Technion. All rights reserved.',ha='center',fontsize=5)
plt.tight_layout(rect=(0,0.03,1,1)); f.savefig(O+'figures/AMS_K502_mountain_front_vs_east_edge.png'); f.savefig(O+'figures/AMS_K502_mountain_front_vs_east_edge.pdf'); plt.close(f)
