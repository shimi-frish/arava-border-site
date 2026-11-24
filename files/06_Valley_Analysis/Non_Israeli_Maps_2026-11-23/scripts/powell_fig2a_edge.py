import numpy as np, geopandas as g
from PIL import Image
from pyproj import Transformer
from shapely.geometry import LineString
from scipy import ndimage as nd
a=np.asarray(Image.open('pw2a.png').convert('RGB')).astype(int); R,G,B=a[...,0],a[...,1],a[...,2]
# outcrop colours: pinks/purples/orange: R high, G lower than R by >25 ; exclude blue sea (B>R) and red fault line (G<60 & B<60 thin)
mask=(R-G>25)&(R>120)&~((G<70)&(B<70))
mask=nd.binary_opening(mask,np.ones((5,5)))
mask=nd.binary_fill_holes(nd.binary_closing(mask,np.ones((7,7))))
lon=lambda x:35+(x-216)/494*0.25; lat=lambda y:29.75-(y-724)/536*0.25
t=Transformer.from_crs(4326,32636,always_xy=True)
V=g.read_file('/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg',layer='valley_polygon_auto_rule').to_crs(32636).union_all()
rows=[]
for y in range(80,1150,4):
    xs=np.where(mask[y,150:])[0]
    if not len(xs): continue
    x=xs[0]+150; E,N=t.transform(lon(x),lat(y))
    L=LineString([(E-40000,N),(E+40000,N)]); vi=V.intersection(L)
    if vi.is_empty: continue
    rows.append((lat(y),E,vi.bounds[2]))
r=np.array(rows); d=(r[:,1]-r[:,2])/1000
print(len(r),'lat',r[:,0].min().round(3),r[:,0].max().round(3))
print('median km',np.median(d).round(2),'p10',np.percentile(d,10).round(2),'p90',np.percentile(d,90).round(2),'abs<1',(abs(d)<1).mean().round(2),'abs<2',(abs(d)<2).mean().round(2),'east',(d>0).mean().round(2))
for lo in np.arange(29.5,30.0,0.05):
    m=(r[:,0]>=lo)&(r[:,0]<lo+0.05)
    if m.sum(): print(round(lo,2),m.sum(),np.median(d[m]).round(2))
Image.fromarray((mask*255).astype(np.uint8)).resize((335,505)).save('pwmask.png')
# --- figure: Powell fig 2a mountain foot vs final valley, on AMS K502 Aqaba
import rasterio,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from rasterio.merge import merge
from matplotlib.lines import Line2D
O='/mnt/project-files/non-israeli-maps/'
pts=[]
for y in range(80,1150,4):
    xs=np.where(mask[y,150:])[0]
    if len(xs) and lat(y)<=30.0: pts.append(t.transform(lon(xs[0]+150),lat(y)))
P=np.array(pts)
g.GeoDataFrame({'source':['Powell, Abed & Jarrar 2015 fig 2a (after McCourt & Ibrahim 1990, NRA)'],'method':['west edge of basement outcrops = mountain foot; graticule georef ~1-2 km']},geometry=[LineString(P)],crs=32636).to_file(O+'Non_Israeli_maps_valley_delineations.gpkg',layer='Powell2015_fig2a_mountain_foot')
Vg=g.read_file('/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg',layer='valley_polygon_auto_rule').to_crs(32636)
b=(686000,3262000,722000,3330000)
a,T=merge([rasterio.open(O+'georef/AMS_K502_Aqaba_1961_UTM36.tif'),rasterio.open(O+'georef/AMS_K502_Maan_1961_UTM36.tif')],bounds=b,res=25,nodata=0)
f,ax=plt.subplots(figsize=(5.6,10),dpi=220)
rgba=np.moveaxis(a,0,-1).astype(float)/255; rgba[...,:3]=0.55*rgba[...,:3]+0.45
ax.imshow(rgba,extent=(b[0],b[2],b[1],b[3]))
Vg.boundary.plot(ax=ax,color='#c000c0',lw=1.6); ax.plot(P[:,0],P[:,1],color='#e07000',lw=2)
for nm,(lo,la) in {'Aqaba':(35.006,29.53)}.items():
    x,y=t.transform(lo,la); ax.plot(x,y,'ks',ms=3); ax.text(x+600,y,nm,fontsize=7,va='center',bbox=dict(fc='white',ec='none',pad=.5))
ax.set_xlim(b[0],b[2]); ax.set_ylim(b[1],b[3]); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel('')
ax.plot([b[0]+2000,b[0]+12000],[b[1]+2500]*2,'k',lw=3); ax.text(b[0]+7000,b[1]+3300,'10 km',ha='center',fontsize=7,bbox=dict(fc='white',ec='none',pad=1))
ax.legend(handles=[Line2D([],[],color='#e07000',lw=2,label='Mountain foot: west edge of basement outcrops\n(Powell, Abed & Jarrar 2015, fig. 2a)'),Line2D([],[],color='#c000c0',lw=2,label='Arava valley – final delineation of this study')],loc='upper left',fontsize=6,framealpha=.92)
ax.set_title('Mountain foot from a Jordanian-authored geological map vs. final valley\n(Aqaba – 30°N)',fontsize=8.5)
f.text(0.5,0.006,'Background: AMS K502 1:250,000 (1961, public domain). Outcrop edge digitised from Powell et al. 2015, GeoArabia 20(1), fig. 2a (after McCourt & Ibrahim 1990, NRA Jordan); positional accuracy ~1-2 km.\nAnalysis: Shimon Frish, PhD research, Technion (supervisors Prof. M. Shoshany, Prof. A. Shapira). All rights reserved.',ha='center',fontsize=4.4,wrap=True)
plt.tight_layout(rect=(0,0.03,1,1)); f.savefig(O+'figures/Powell2015_mountain_foot_vs_valley.png'); f.savefig(O+'figures/Powell2015_mountain_foot_vs_valley.pdf'); plt.close(f)
