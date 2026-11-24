import sys; sys.path.insert(0,'scripts'); from georef_tools import *
P=[(302,83,34.7913,31.2518,'Beersheba'),(383,212,35.0636,31.0247,'Kurnub (Mamshit)'),(445,315,35.2410,30.7770,'Ein Husub (Mezad Hatzeva)'),(508,185,35.3920,31.0650,'Sdom'),(118,277,34.4270,30.8830,'Auja el-Hafir (Nitzana)'),(202,707,34.6760,29.9820,'Kuntilla'),(323,902,34.9540,29.5464,'Umm Rashrash (Eilat)'),(342,933,35.0025,29.5197,'Aqaba')]
G=[(c,r,*LL.transform(lo,la)) for c,r,lo,la,_ in P]
res=from_gcps('/mnt/user-data/uploads/Israel-Jordan-Arava/05_Historical_Maps/B_Topographic_Thematic_Maps/Israeli/התקדמות חטיבת גולני בערבה במבצע חורב.jpg',G,'Operation_Uvda_Golani_1949_ITM.tif',order=2)
print('RMS',np.sqrt((res**2).mean()).round(),dict(zip([p[4] for p in P],res.round())))
json.dump({'gcps_px_lonlat':P,'rms_m':float(np.sqrt((res**2).mean()))},open('Uvda1949_gcps.json','w'),ensure_ascii=False)
