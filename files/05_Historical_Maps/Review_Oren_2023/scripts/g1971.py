import sys; sys.path.insert(0,'scripts'); from georef_tools import *
P=[(323,328,34.5,31.0),(690,328,35.0,31.0),(1060,330,35.5,31.0),(323,757,34.5,30.5),(690,755,35.0,30.5),(1062,753,35.5,30.5),(323,1183,34.5,30.0),(690,1182,35.0,30.0)]
G=[(c,r,*LL.transform(lo,la)) for c,r,lo,la in P]
res=from_gcps('/mnt/user-data/uploads/Israel-Jordan-Arava/05_Historical_Maps/B_Topographic_Thematic_Maps/Israeli/מפת עזר ללימוד תנך דוד בנבנשתי ובן ציון לוריא, 1971.jpg',G,'Benvenisti_Luria_1971_Negev_Arava_ITM.tif',order=1)
print('RMS',np.sqrt((res**2).mean()).round(),res.round())
f,_=fit(G,1)
for n,c,r,lo,la in [('Kerak',1208,170,35.7046,31.1806),('Beersheba',568,125,34.7913,31.2518),('Mamshit',745,307,35.0636,31.0247)]:
    e,nn=f(c,r); E,N=LL.transform(lo,la); print(n,'check err m',round(float(np.hypot(e-E,nn-N))))
json.dump({'graticule_gcps_px_lonlat':P,'rms_m':float(np.sqrt((res**2).mean()))},open('Benvenisti1971_gcps.json','w'))
