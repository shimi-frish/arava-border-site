import rasterio,numpy as np,geopandas as g
from rasterio.merge import merge
from scipy import ndimage as nd
O='/mnt/project-files/non-israeli-maps/georef/'
V=g.read_file('/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg',layer='valley_polygon_auto_rule').to_crs(32636)
x0,y0,x1,y1=V.total_bounds; b=(x0-15000,y0-8000,x1+15000,y1+3000)
a,T=merge([rasterio.open(O+f'AMS_K502_{s}_1961_UTM36.tif') for s in ['Aqaba','Maan','Jerusalem']],bounds=b,res=25,nodata=0)
a=a.astype(float); al=a[3]>0; R,G,B=a[:3]
brown=((R-B)>35)&((R-G)>15)&(R<215)
np.save('ams_brown.npy',brown); np.save('ams_al.npy',al)
import pickle; pickle.dump((T,a.shape),open('ams_T.pkl','wb'))
for w in [21,41]:
  f=nd.uniform_filter(brown.astype(float),w); print(w,[round(np.percentile(f[al],q),3) for q in (10,25,50,75,90)])
  np.save(f'ams_frac{w}.npy',f)
