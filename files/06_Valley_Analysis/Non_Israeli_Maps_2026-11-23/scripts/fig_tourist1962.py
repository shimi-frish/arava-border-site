import numpy as np,rasterio,geopandas as g,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
O='/mnt/project-files/non-israeli-maps/'
d=rasterio.open(O+'georef/Jordan_Tourist_1962_UTM36.tif'); a=d.read(); b=d.bounds
V=g.read_file('/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg',layer='valley_polygon_auto_rule').to_crs(32636)
f,axs=plt.subplots(1,2,figsize=(9,7.4),dpi=220)
for ax,(y0,y1),tt in zip(axs,[(3262000,3352000),(3345000,3445000)],['South: Aqaba – Gharandal – Petra','North: Petra – Feinan – Safi']):
    ax.imshow(np.moveaxis(a,0,-1),extent=(b.left,b.right,b.bottom,b.top))
    V.boundary.plot(ax=ax,color='#c000c0',lw=1.5)
    ax.set_xlim(680000,755000); ax.set_ylim(y0,y1); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel(''); ax.set_title(tt,fontsize=8)
    ax.plot([742000,752000],[y0+3000]*2,'k',lw=3); ax.text(747000,y0+4500,'10 km',ha='center',fontsize=6.5,bbox=dict(fc='white',ec='none',pad=1))
axs[0].legend(handles=[Line2D([],[],color='#c000c0',lw=2,label='Arava valley – final delineation of this study')],loc='upper left',fontsize=6.5,framealpha=.9)
f.suptitle('Final Arava valley on the Hashemite Kingdom of Jordan Tourist Map 1:750,000\n(compiled and drawn by the Dept. of Lands & Surveys for the Tourism Authority, 1962; print of May 1979)',fontsize=9)
f.text(0.5,0.006,'Base map: IRCICA Library, Istanbul, map H-791 (openaccess.ircica.org/handle/123456789/21236), georeferenced on the 1° graticule (9 points, RMS 90 m; check against towns ~1-2 km).\nOverlay: Shimon Frish, PhD research, Technion (supervisors Prof. M. Shoshany, Prof. A. Shapira). All rights reserved.',ha='center',fontsize=5)
plt.tight_layout(rect=(0,0.035,1,0.93)); f.savefig(O+'figures/valley_on_Jordan_Tourist_Map_1962.png'); f.savefig(O+'figures/valley_on_Jordan_Tourist_Map_1962.pdf'); plt.close(f)
