import sys; sys.path.insert(0,'scripts'); from georef_tools import *
D='/mnt/user-data/uploads/Israel-Jordan-Arava/05_Historical_Maps/A_Agreement_Border_Maps/Israeli/'
from_world(D+'מובלעת צופר.jpg',D+'מובלעת צופר.jgwx',3857,'zofar_ITM.tif')
from_world(D+'קו הגבול באיזור פארן.jpg',D+'קו הגבול באיזור פארן.jgwx',3857,'paran_ITM.tif')
import geopandas as gpd,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from rasterio.plot import show
b=gpd.read_file('/mnt/project-files/border-map/border1994.geojson').to_crs(2039)
fig,ax=plt.subplots(1,2,figsize=(18,9))
for a,f in zip(ax,['zofar_ITM.tif','paran_ITM.tif']):
    d=rasterio.open(f); show(d,ax=a); b.plot(ax=a,color='cyan',lw=1.2); a.set_xlim(d.bounds.left,d.bounds.right);a.set_ylim(d.bounds.bottom,d.bounds.top); print(f,d.bounds,d.res)
plt.savefig('chk.png',dpi=60)
