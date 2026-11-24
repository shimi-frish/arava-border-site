import geopandas as g, numpy as np, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from PIL import Image
O='/mnt/project-files/non-israeli-maps/'; F='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
V=g.read_file(F,layer='valley_polygon_auto_rule').to_crs(32636); S=g.read_file(F,layer='straight_line').to_crs(32636)
A=g.read_file(O+'Atlas_of_Jordan_2013_depression_unit.gpkg')
d=rasterio.open(O+'Copernicus_DEM_GLO30_Arava_60m_UTM36.tif'); z=d.read(1); z[z<-1000]=np.nan
fig,(ax0,ax)=plt.subplots(1,2,figsize=(11,10),dpi=200,gridspec_kw={'width_ratios':[1,1]})
src=Image.open('/mnt/user-data/uploads/Downloads/AtlasJordan_4859_img-1.jpg').convert('RGB').crop((0,560,420,1260))
ax0.imshow(src); ax0.set_axis_off(); ax0.set_title('(a) Atlas of Jordan (Ifpo 2013), fig. I.2 – detail\n"Jordan Five Main Morphological Units" (H. Al-Bilbisi; DEM by RJGC)',fontsize=8)
ls=LightSource(315,40); hs=ls.hillshade(np.nan_to_num(z,nan=0),vert_exag=2,dx=60,dy=60)
ax.imshow(hs,cmap='gray',extent=(d.bounds[0],d.bounds[2],d.bounds[1],d.bounds[3]),alpha=.8)
A.plot(ax=ax,facecolor=(0.9,0.2,0.1,0.18),edgecolor=(0.8,0.1,0.05),lw=1.2)
V.plot(ax=ax,facecolor=(0.1,0.4,0.9,0.25),edgecolor=(0.05,0.2,0.7),lw=1)
S.plot(ax=ax,color='red',lw=1)
x0,y0,x1,y1=V.total_bounds; ax.set_xlim(x0-15000,x1+15000); ax.set_ylim(y0-4000,y1+4000); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel('')
ax.plot([x0-12000,x0+8000],[y1,y1],'k',lw=3); ax.text(x0-2000,y1+1200,'20 km',ha='center',fontsize=7)
ax.legend(handles=[Patch(fc=(0.1,0.4,0.9,0.25),ec=(0.05,0.2,0.7),label='Final valley, this study (2,729 km²)'),Patch(fc=(0.9,0.2,0.1,0.18),ec=(0.8,0.1,0.05),label='"Wadi Araba – Dead Sea – Jordan River Depression"\nunit, digitised from (a) (2,960 km²)'),Line2D([],[],color='red',label='Straight line Dead Sea – Eilat')],loc='lower right',fontsize=6.5,framealpha=.9)
ax.set_title('(b) Comparison (86% of the final valley lies inside the unit; IoU 0.70)',fontsize=8)
fig.text(0.5,0.01,'(a) © Presses de l\'Ifpo 2013, research use. (b) Digitisation & overlay: Shimon Frish, PhD research, Technion (supervisors Prof. M. Shoshany, Prof. A. Shapira). All rights reserved.',ha='center',fontsize=6)
plt.tight_layout(rect=(0,0.02,1,1)); fig.savefig(O+'figures/atlas_of_jordan_unit_vs_valley.png'); fig.savefig(O+'figures/atlas_of_jordan_unit_vs_valley.pdf')
