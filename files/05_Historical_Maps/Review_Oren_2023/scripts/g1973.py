import sys; sys.path.insert(0,'scripts'); from georef_tools import *
P=[(195,783,35.0,30.0,'graticule 35E 30N'),(106,205,34.7913,31.2518,'Beersheba'),(502,685,35.7341,30.1962,"Ma'an"),(191,990,34.9519,29.5577,'Eilat'),(232,65,35.0998,31.5326,'Hebron'),(404,778,35.4936,29.9911,'Ras en Naqb')]
G=[(c,r,*LL.transform(lo,la)) for c,r,lo,la,_ in P]
res=from_gcps('/mnt/user-data/uploads/Israel-Jordan-Arava/05_Historical_Maps/A_Agreement_Border_Maps/Israeli/קו הגבול על פי מפה משנת 1973.jpg',G,'Border_map_1973_ITM.tif',order=1)
print('RMS',np.sqrt((res**2).mean()).round(),dict(zip([p[4] for p in P],res.round())))
json.dump({'control_points_px_lonlat':P,'rms_m':float(np.sqrt((res**2).mean()))},open('Map1973_gcps.json','w'),ensure_ascii=False)
