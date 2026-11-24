import rasterio,numpy as np,geopandas as g,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from scipy import ndimage as nd
d=rasterio.open('/mnt/project-files/non-israeli-maps/georef/K737_3049III_Aqaba_1960_UTM36.tif')
a=d.read().astype(float); al=a[3]>0
R,G,B=a[:3]; brown=((R-B)>40)&(R<200)   # brown ink (contours, hill shade, rock hachure)
f=nd.uniform_filter(brown.astype(float),31)  # 310 m window
np.save('kfrac.npy',f)
for q in [10,25,50,75,90]: print(q,np.percentile(f[al],q))
F='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
V=g.read_file(F,layer='valley_polygon_auto_rule').to_crs(32636)
b=d.bounds; fig,ax=plt.subplots(1,1,figsize=(8,9),dpi=100)
ax.imshow(np.where(al,f,np.nan),extent=(b.left,b.right,b.bottom,b.top),cmap='viridis'); V.boundary.plot(ax=ax,color='r'); ax.set_xlim(b.left,b.left+14000); ax.set_ylim(b.bottom,b.top)
fig.savefig('kfrac.png',bbox_inches='tight')
