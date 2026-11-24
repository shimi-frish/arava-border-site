import geopandas as g, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from shapely.geometry import Point
from pyproj import Transformer
plt.rcParams['font.family']='DejaVu Sans'
O='/mnt/project-files/non-israeli-maps/'; F='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
d=rasterio.open(O+'Copernicus_DEM_GLO30_Arava_60m_UTM36.tif'); z=d.read(1); z[z<-1000]=np.nan
V=g.read_file(F,layer='valley_polygon_auto_rule').to_crs(32636)
S=g.read_file(F,layer='straight_line').to_crs(32636)
Z=g.read_file(O+'JVA_law_zone_vs_valley.gpkg',layer='jva_law_zone_500m')
x0,y0,x1,y1=V.total_bounds; pad=12000
ext=(d.bounds[0],d.bounds[2],d.bounds[1],d.bounds[3])
fig,ax=plt.subplots(figsize=(7.2,12),dpi=200)
ls=LightSource(315,40); hs=ls.hillshade(np.nan_to_num(z,nan=0),vert_exag=2,dx=60,dy=60)
ax.imshow(hs,cmap='gray',extent=ext,alpha=.85)
Z.plot(ax=ax,facecolor=(0.95,0.6,0.1,0.35),edgecolor=(0.8,0.4,0),lw=1.2)
V.plot(ax=ax,facecolor=(0.1,0.4,0.9,0.30),edgecolor=(0.05,0.2,0.7),lw=1)
S.plot(ax=ax,color='red',lw=1.4)
t=Transformer.from_crs(4326,32636,always_xy=True)
pl=[('Eilat',34.951,29.557,-1,0),('Aqaba',35.006,29.53,1,-1),('Qutr (Qatar village)',35.0925,29.8183,1,0),('Gharandal',35.18,30.03,1,0),
    ('Wadi Fidan',35.37,30.65,1,0),('Hatzeva',35.25,30.78,-1,0),('Ghor Fifa',35.45,30.93,1,0),('Dead Sea (southern basin)',35.42,31.08,1,0),('Yotvata',35.06,29.89,-1,0)]
for n,lo,la,dx,dy in pl:
    x,y=t.transform(lo,la); ax.plot(x,y,'ko',ms=3)
    ax.annotate(n,(x,y),xytext=(6*dx,6*dy),textcoords='offset points',ha='left' if dx>0 else 'right',va='center',fontsize=8,
                bbox=dict(fc='white',ec='none',alpha=.75,pad=1))
ax.set_xlim(x0-pad,x1+pad+8000); ax.set_ylim(y0-pad/2,y1+pad/2); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel('')
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
ax.legend(handles=[Patch(fc=(0.1,0.4,0.9,0.3),ec=(0.05,0.2,0.7),label='Arava valley – final delineation (mountain foot, 2026)'),
 Patch(fc=(0.95,0.6,0.1,0.35),ec=(0.8,0.4,0),label='"The Valley" by Jordanian law\n(Jordan Valley Development Law 1988, art. 2c:\nDead Sea – Qatar village, up to 500 m a.s.l.)'),
 Line2D([],[],color='red',label='Straight line Dead Sea – Eilat')],loc='lower right',fontsize=7,framealpha=.9)
ax.plot([x0-pad+3000,x0-pad+23000],[y1-4000]*2,'k',lw=3); ax.text(x0-pad+13000,y1-2500,'20 km',ha='center',fontsize=7)
ax.set_title('Arava valley vs. the Jordanian legal definition of "the Valley"',fontsize=10)
fig.text(0.5,0.01,'DEM: Copernicus GLO-30 (ESA). Law: FAOLEX jor39373. Shimon Frish, PhD research, Technion (supervisors Prof. M. Shoshany, Prof. A. Shapira). All rights reserved.',ha='center',fontsize=5.5)
plt.tight_layout(rect=(0,0.02,1,1)); fig.savefig(O+'figures/jva_law_vs_valley.png'); fig.savefig(O+'figures/jva_law_vs_valley.pdf')
