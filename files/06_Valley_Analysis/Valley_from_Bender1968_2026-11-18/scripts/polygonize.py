import sys
RO=float(sys.argv[1]) if len(sys.argv)>1 else 1000
SHEET=sys.argv[2] if len(sys.argv)>2 else 'Aqaba-Maan'
import numpy as np, pickle, geopandas as gpd, rasterio, rasterio.features as rf
from rasterio.windows import from_bounds
from scipy import ndimage as ndi
from shapely.geometry import shape
from shapely.ops import unary_union
r=rasterio.open(f'/mnt/project-files/jordan-geology/Bender1968_250k_{SHEET}_ITM.tif')
B=(186000,378000,262000,547290) if SHEET=='Aqaba-Maan' else (186000,545660,262000,565000); w=from_bounds(*B,r.transform); T=r.window_transform(w)
img=r.read(window=w,boundless=True,fill_value=255).astype(float); px=abs(T.a)
R0,G0,B0=img
VP=(R0>200)&(G0>192)&(B0>145)&((R0-B0)<78)&((G0-R0)<5)&((R0-G0)<22)&~((B0>228)&(R0>244))
sat=img.max(0)-img.min(0)
ROCK=ndi.binary_opening((~VP)&(sat>45),structure=np.ones((3,3)))
PA=(B0>226)&(R0>243)&(G0>243)
win=int(300/px)|1
fv=ndi.uniform_filter(VP.astype(float),win); fr=ndi.uniform_filter(ROCK.astype(float),win)
unm=ndi.uniform_filter(PA.astype(float),int(1000/px)|1)>0.75
m=(fv/np.maximum(fv+fr,1e-6)>0.6)&(fr<0.3)&(fv>0.03)&~unm
def dil(a,r): return ndi.distance_transform_edt(~a)<=r
def ero(a,r): return ndi.distance_transform_edt(a)>r
Rc=int(200/px); m=ero(dil(m,Rc),Rc)
Rr=int(RO/px); m=dil(ero(m,Rr),Rr)
FV='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
S=gpd.read_file(FV,layer='straight_line').to_crs(2039).geometry.iloc[0]
m&=rf.rasterize([(S.buffer(20000),1)],out_shape=m.shape,transform=T).astype(bool)
L,n=ndi.label(m); sz=ndi.sum(np.ones_like(L),L,range(1,n+1))
Lm=rf.rasterize([(S,1)],out_shape=m.shape,transform=T,all_touched=True).astype(bool)
keep=[i for i in set(np.unique(L[Lm&(L>0)])) if sz[i-1]*px*px>2e6]; m=np.isin(L,keep)
holes=ndi.binary_fill_holes(m)&~m; HL,hn=ndi.label(holes); hs=ndi.sum(np.ones_like(HL),HL,range(1,hn+1))*px*px
m|=np.isin(HL,np.where(hs<2e6)[0]+1)
P=unary_union([shape(g) for g,v in rf.shapes(m.astype('uint8'),mask=m,transform=T)]).simplify(15)
U=unary_union([shape(g) for g,v in rf.shapes(unm.astype('uint8'),mask=unm,transform=T)])
pickle.dump((P,U),open(f'/tmp/claude-0/Pbender_{SHEET}_{int(RO)}.pkl','wb')); print(round(P.area/1e6,1),len(getattr(P,'geoms',[P])))
