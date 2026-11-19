import numpy as np, json
P=[(2080,1760,773.5,5664),(2090,1760,1167.4,5662),(2100,1760,1560.1,5664),(2110,1760,1954.4,5663),(2120,1760,2347.2,5663),(2130,1760,2739.1,5659),
(2120,1880,2325.5,261),(2130,1880,2733.2,257),
(2140,1770,3137,5205.3),(2140,1780,3137,4754.8),(2140,1790,3136,4300.5),(2140,1800,3138,3855.1),(2140,1810,3136,3398.2),(2140,1820,3135,2949.4),(2140,1825,3133,2725),(2140,1830,3134,2500.1),(2140,1840,3134,2049.0),(2140,1850,3129,1596.2),(2140,1870,3125,694.2)]
P=np.array(P,float); lon=P[:,0]/60; lat=P[:,1]/60; x=P[:,2]; y=P[:,3]
def A(lo,la,o):
    c=[np.ones_like(lo),lo,la]
    if o>=2: c+= [lo*lo,lo*la,la*la]
    return np.column_stack(c)
for o in (1,2):
    M=A(lon,lat,o); cx=np.linalg.lstsq(M,x,rcond=None)[0]; cy=np.linalg.lstsq(M,y,rcond=None)[0]
    r=np.hypot(M@cx-x,M@cy-y); print(o,'rms px',round(np.sqrt((r**2).mean()),1),'max',round(r.max(),1), np.round(r,1))
# check yl of top line at corner: px per deg
M=A(lon,lat,2); cx=np.linalg.lstsq(M,x,rcond=None)[0]; cy=np.linalg.lstsq(M,y,rcond=None)[0]
json.dump({'cx':cx.tolist(),'cy':cy.tolist(),'gcps':P.tolist()},open('poly.json','w'))
from PIL import Image, ImageDraw
im=Image.open('k.jpg')
pts={'Masada':(35.3536,31.3157),'Qasr al-Bint':(35.4410,30.3290),'Jebel Harun':(35.4068,30.3166),'Aqaba fort':(35.0036,29.5200),'Jezirat Faraun':(34.8577,29.4646),'Ein Gharandal(J)':(35.3290,30.1180)}
tiles=[]
for n,(lo,la) in pts.items():
    m=A(np.array([lo]),np.array([la]),2); px,py=float((m@cx)[0]),float((m@cy)[0]); print(n,round(px),round(py))
    t=im.crop((int(px)-60,int(py)-60,int(px)+60,int(py)+60)).resize((360,360)); d=ImageDraw.Draw(t); d.ellipse((174,174,186,186),outline=(255,0,0),width=2); d.text((3,3),n,fill=(255,0,0)); tiles.append(t)
o=Image.new('RGB',(360*len(tiles),360),'white')
for i,t in enumerate(tiles): o.paste(t,(360*i,0))
o.save('chk.png')
