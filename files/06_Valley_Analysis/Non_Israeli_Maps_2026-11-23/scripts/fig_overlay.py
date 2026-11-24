import numpy as np, rasterio, geopandas as g, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from rasterio.merge import merge
from matplotlib.lines import Line2D
O='/mnt/project-files/non-israeli-maps/'; F='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
V=g.read_file(F,layer='valley_polygon_auto_rule').to_crs(32636); S=g.read_file(F,layer='straight_line').to_crs(32636)
def fig(tifs, out, title, src, bbox=None, size=(7.5,12.5), dpi=220):
    srcs=[rasterio.open(O+'georef/'+t) for t in tifs]
    x0,y0,x1,y1=bbox if bbox else V.total_bounds
    pad=6000; b=(x0-pad,y0-pad,x1+pad,y1+pad)
    a,tr=merge(srcs,bounds=b,res=50,nodata=0)
    rgba=np.moveaxis(a,0,-1).astype(float)/255; rgba[...,3]=(a[3]>0)
    f,ax=plt.subplots(figsize=size,dpi=dpi)
    ax.imshow(rgba,extent=(b[0],b[2],b[1],b[3]))
    V.boundary.plot(ax=ax,color='#c000c0',lw=1.6)
    S.plot(ax=ax,color='red',lw=1.2)
    ax.set_xlim(b[0],b[2]); ax.set_ylim(b[1],b[3]); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel('')
    ax.plot([b[0]+3000,b[0]+23000],[b[3]-3000]*2,'k',lw=3); ax.text(b[0]+13000,b[3]-2200,'20 km',ha='center',fontsize=7,bbox=dict(fc='white',ec='none',pad=1))
    ax.legend(handles=[Line2D([],[],color='#c000c0',lw=2,label='Arava valley – final delineation of this study (2026)'),Line2D([],[],color='red',label='Straight line Dead Sea – Eilat')],loc='lower right',fontsize=7,framealpha=.9)
    ax.set_title(title,fontsize=9)
    f.text(0.5,0.008,src+'\nOverlay: Shimon Frish, PhD research, Technion (supervisors Prof. M. Shoshany, Prof. A. Shapira). All rights reserved.',ha='center',fontsize=5,wrap=True)
    plt.tight_layout(rect=(0,0.025,1,1)); f.savefig(out+'.png'); f.savefig(out+'.pdf',dpi=200); plt.close(f)
fig(['AMS_K502_Aqaba_1961_UTM36.tif','AMS_K502_Maan_1961_UTM36.tif','AMS_K502_Jerusalem_1961_UTM36.tif'],O+'figures/valley_on_AMS_K502_1961',
    'Final Arava valley on the U.S. Army Map Service 1:250,000 (Series K502, sheets Aqaba, Ma\'an, Jerusalem, 1961)',
    'Base map: U.S. Army Map Service, Series K502, Edition 3-AMS 1961 (public domain; scan UT Austin PCL), georeferenced on the UTM grid (RMS 17-35 m).')
xb=V.total_bounds; _k=rasterio.open(O+'georef/TransJordan_250k_Kerak_1941_UTM36.tif')
fig(['TransJordan_250k_Kerak_1941_UTM36.tif'],O+'figures/valley_on_TransJordan_1941_Kerak',
    'Final Arava valley on the Trans-Jordan 1:250,000, sheet Kerak\n(Department of Lands & Surveys, Trans-Jordan, edition of June 1941)',
    'Base map: Trans-Jordan 1:250,000, Kerak, Dept. of Lands & Surveys Trans-Jordan, reproduced by Survey of Palestine 1941 (out of copyright; NLA nla.obj-233522746), georef. Palestine grid (RMS 23 m).',
    bbox=(_k.bounds.left+3000, _k.bounds.bottom+9000, xb[2]+12000, xb[3]), size=(7,9.5))
