import numpy as np,pickle,geopandas as g
from shapely.geometry import LineString
from shapely.ops import unary_union
T,sh=pickle.load(open('ams_T.pkl','rb')); f=np.load('ams_frac41.npy'); al=np.load('ams_al.npy')
V=unary_union(g.read_file('/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg',layer='valley_polygon_auto_rule').to_crs(32636).geometry)
B=unary_union(g.read_file('/mnt/project-files/border-map/border1994.geojson').to_crs(32636).geometry)
res=T.a; need=int(1500/res); thr=0.10
rows=[]
for y in np.arange(V.bounds[1]+500,V.bounds[3]-500,250):
    L=LineString([(V.bounds[0]-20000,y),(V.bounds[2]+20000,y)])
    bi=B.intersection(L); vi=V.intersection(L)
    if bi.is_empty or vi.is_empty: continue
    xb=max(p.x for p in (bi.geoms if hasattr(bi,'geoms') else [bi]) if p.geom_type=='Point') if bi.geom_type!='LineString' else bi.bounds[2]
    r=int((T.f-y)/(-T.e)); c0=int((xb+800-T.c)/res)
    if r<0 or r>=sh[1]: continue
    prof=f[r,c0:]; ok=al[r,c0:]
    hi=(prof>thr)&ok
    run=np.convolve(hi.astype(int),np.ones(need,int),'valid')
    j=np.where(run==need)[0]
    if not len(j): continue
    xe=T.c+(c0+j[0])*res
    rows.append((y,xb,xe,vi.bounds[2]))
r=np.array(rows); np.save('ams_edge.npy',r)
d=r[:,2]-r[:,3]
print(len(r),'median',np.median(d).round(),'p10',np.percentile(d,10).round(),'p90',np.percentile(d,90).round(),'abs<1km',(abs(d)<1000).mean().round(2),'abs<2km',(abs(d)<2000).mean().round(2))
for lo in range(3270000,3440000,20000):
    m=(r[:,0]>=lo)&(r[:,0]<lo+20000)
    if m.sum(): print(lo,m.sum(),np.median(d[m]).round())
