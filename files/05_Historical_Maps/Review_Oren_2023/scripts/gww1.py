import sys; sys.path.insert(0,'scripts'); from georef_tools import *
P=[(318,148,34.9896,32.8191,'Haifa'),(257,326,34.7522,32.0543,'Jaffa'),(341,386,35.2310,31.7767,'Jerusalem'),(133,463,34.2170,31.3220,'Rafah coast'),(242,898,34.9800,29.5380,'Gulf of Aqaba head'),(402,388,35.5530,31.7620,'Dead Sea north tip')]
G=[(c,r,*LL.transform(lo,la)) for c,r,lo,la,_ in P]
res=from_gcps('pdfimg/p06.jpg',G,'Bigger_military_zones_after_WWI_ITM.tif',order=1)
print('RMS',np.sqrt((res**2).mean()).round(),dict(zip([p[4] for p in P],res.round())))
json.dump({'gcps_px_lonlat':P,'rms_m':float(np.sqrt((res**2).mean()))},open('BiggerWW1_gcps.json','w'))
