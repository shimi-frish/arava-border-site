import rasterio,numpy as np,geopandas as g,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from scipy import ndimage as nd
from rasterio.features import shapes
from shapely.geometry import shape
from shapely.ops import unary_union
d=rasterio.open('/mnt/project-files/non-israeli-maps/georef/K737_3049III_Aqaba_1960_UTM36.tif')
al=d.read(4)>0; f=np.load('kfrac.npy'); T=d.transform
low=(f<0.30)&al
yy,xx=np.ogrid[-25:26,-25:26]; disk=(xx**2+yy**2)<=25**2   # r=250 m
op=nd.binary_opening(low,disk)
lab,n=nd.label(op); r,c=rasterio.transform.rowcol(T,698000,3283000); comp=lab==lab[r,c]
# fill everything west of component per row (valley floor incl. sand to border)
val=np.zeros_like(comp)
for i in range(comp.shape[0]):
    j=np.where(comp[i])[0]
    if len(j): val[i,:j.max()+1]=True
val&=al
val=nd.binary_closing(val,disk)&al
geom=unary_union([shape(s) for s,v in shapes(val.astype(np.uint8),mask=val,transform=T) if v==1])
G=g.GeoDataFrame(geometry=[geom],crs=32636); G.to_file('k737_valley.gpkg')
F='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
V=g.read_file(F,layer='valley_polygon_auto_rule').to_crs(32636)
b=d.bounds
fig,ax=plt.subplots(figsize=(8,9),dpi=100)
ax.imshow(np.moveaxis(d.read(out_shape=(4,d.height//3,d.width//3)),0,-1),extent=(b.left,b.right,b.bottom,b.top))
G.boundary.plot(ax=ax,color='b',lw=1.5); V.boundary.plot(ax=ax,color='m',lw=1.5); ax.set_xlim(b.left,b.left+14000); ax.set_ylim(b.bottom,b.top)
fig.savefig('kval.png',bbox_inches='tight')
