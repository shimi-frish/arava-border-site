import numpy as np, pickle, geopandas as gpd, rasterio.features as rf
from scipy import ndimage as ndi
from shapely.geometry import shape, Polygon
from shapely.ops import unary_union
lab=np.load('/tmp/claude-0/lab.npy'); names,T,sh=pickle.load(open('/tmp/claude-0/lab.pkl','rb'))
VAL=['Al','Alf','Als','Plg','Pls','LM']
LINE=['black','grey','red']  # linework/text: neutral, assign by closing
m=np.isin(lab,[names.index(k) for k in VAL])
lw=np.isin(lab,[names.index(k) for k in LINE])
px=abs(T.a)
def dil(a,r): return ndi.distance_transform_edt(~a)<=r
def ero(a,r): return ndi.distance_transform_edt(a)>r
m2=m|(lw&dil(m,3))                  # line work surrounded by valley colours
m2=ero(dil(m2,3),3)                 # closing 30 m
R=int(500/px); m3=dil(ero(m2,R),R)  # opening 500 m
L,n=ndi.label(m3); sz=ndi.sum(np.ones_like(L),L,range(1,n+1)); k=np.argmax(sz)+1; m4=L==k
holes=ndi.binary_fill_holes(m4)&~m4; HL,hn=ndi.label(holes); hs=ndi.sum(np.ones_like(HL),HL,range(1,hn+1))*px*px
small=np.isin(HL,np.where(hs<2e6)[0]+1); m5=m4|small
geoms=[shape(g) for g,v in rf.shapes(m5.astype('uint8'),mask=m5,transform=T)]
P=unary_union(geoms).simplify(10)
pickle.dump(P,open('/tmp/claude-0/Pnra.pkl','wb')); print(round(P.area/1e6,1), P.bounds)
