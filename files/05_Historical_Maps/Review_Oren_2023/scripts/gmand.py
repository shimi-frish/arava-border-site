import sys; sys.path.insert(0,'scripts'); from georef_tools import *
P=[(212,231,35.0,31.0,'graticule 35E 31N'),(171,161,34.7913,31.2518,'Beersheba'),(359,175,35.7046,31.1806,'Kerak'),(326,405,35.4794,30.3216,'Wadi Musa'),(308,417,35.4444,30.3285,'Petra'),(373,443,35.7341,30.1962,"Ma'an")]
G=[(c,r,*LL.transform(lo,la)) for c,r,lo,la,_ in P]+[(195,627,197515,383900)]
names=[p[4] for p in P]+['gulf head boundary point']
res=from_gcps('/mnt/user-data/uploads/Israel-Jordan-Arava/05_Historical_Maps/A_Agreement_Border_Maps/British_Ottoman/גבולות עם עבר הירדן בערבה בתקופת המנדט.png',G,'Mandate_borders_southern_Palestine_2M_ITM.tif',order=1)
print('RMS',np.sqrt((res**2).mean()).round(),dict(zip(names,res.round())))
json.dump({'gcps':[list(g) for g in G],'names':names,'rms_m':float(np.sqrt((res**2).mean()))},open('Mandate2M_gcps.json','w'),ensure_ascii=False)
