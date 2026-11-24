import sys; sys.path.insert(0,'scripts'); from georef_tools import *
T=TO_ITM(28193)
P=[(121,78,130000,990000),(672,80,170000,990000),(118,905,130000,930000),(258,768,140000,940000),(532,492,160000,960000),(392,631,150000,950000),(260,219,140000,980000)]
G=[(c,r,*T.transform(x,y)) for c,r,x,y in P]
f='/mnt/user-data/uploads/Israel-Jordan-Arava/05_Historical_Maps/B_Topographic_Thematic_Maps/British/מפת מעאן המיפוי של פלשתינה-אי), 1939.jpg'
res=from_gcps(f,G,'TransJordan_250k_1939_north_Arava_ITM.tif',order=1)
print('RMS m',np.sqrt((res**2).mean()).round(0),res.round(0))
json.dump({'gcps_px_PalGrid28193':P,'rms_m':float(np.sqrt((res**2).mean()))},open('TransJordan_1939_gcps.json','w'))
