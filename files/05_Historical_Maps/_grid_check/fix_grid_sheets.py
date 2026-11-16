# -*- coding: utf-8 -*-
# Run in QGIS Python console:  exec(open(r'<path>/fix_grid_sheets.py', encoding='utf-8').read())
# Builds north-up, compressed GeoTIFFs (EPSG:2039, with pyramids) from the grid-fitted affine of each sheet,
# then repoints the project layers from *_grid_ITM.vrt to the new *_grid_ITM.tif. Original rasters are untouched.
import os
from osgeo import gdal
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QApplication
gdal.UseExceptions()
SHEETS = {
 "0001_FL44748971_modified.tif": {
  "gt": [
   206903.010796212,
   2.206192218,
   -1.9907e-05,
   506050.100252537,
   -0.002289662,
   -2.078457629
  ],
  "W": 11449,
  "H": 16942,
  "vrt": "0001_FL44748971_modified_grid_ITM.vrt"
 },
 "0001_FL44749077_modified.tif": {
  "gt": [
   207051.327737528,
   2.123092619,
   -0.007131606,
   486331.092117456,
   -0.009081973,
   -2.116285967
  ],
  "W": 11731,
  "H": 16413,
  "vrt": "0001_FL44749077_modified_grid_ITM.vrt"
 },
 "0001_FL44749060_modified.tif": {
  "gt": [
   206912.118795011,
   2.11157227,
   -0.002196798,
   466196.407723609,
   -0.003032292,
   -2.122935746
  ],
  "W": 11963,
  "H": 16621,
  "vrt": "0001_FL44749060_modified_grid_ITM.vrt"
 },
 "0001_FL266344297_modified_modified.tif": {
  "gt": [
   224154.829550399,
   4.240081887,
   0.000315274,
   572780.499960648,
   0.011424017,
   -4.238793262
  ],
  "W": 11799,
  "H": 16491,
  "vrt": "0001_FL266344297_modified_modified_grid_ITM.vrt"
 },
 "גליון נחל הערבה - 1958 -100,000.tif": {
  "gt": [
   211688.929593133,
   4.249676962,
   -0.01094049,
   543728.708274954,
   -0.020113961,
   -4.238899683
  ],
  "W": 14466,
  "H": 11512,
  "vrt": "גליון נחל הערבה - 1958 -100,000_grid_ITM.vrt"
 },
 "גליון אילת - 1955 - 100,000.tif": {
  "gt": [
   160014.58852244,
   4.240689321,
   0.01136356,
   423824.114227824,
   0.003519262,
   -4.236400106
  ],
  "W": 17663,
  "H": 14901,
  "vrt": "גליון אילת - 1955 - 100,000_grid_ITM.vrt"
 },
 "גליון עין עדין - 1949 - 100,000.tif": {
  "gt": [
   184680.357504697,
   4.237869343,
   -0.013856343,
   465241.44106814,
   -0.002551561,
   -4.248642033
  ],
  "W": 15984,
  "H": 11642,
  "vrt": "גליון עין עדין - 1949 - 100,000_grid_ITM.vrt"
 },
 "גליון עין יהב - 1948 - 100,000.tif": {
  "gt": [
   185118.456326099,
   4.249407858,
   -0.008279151,
   525487.06445164,
   0.000446553,
   -4.247857342
  ],
  "W": 11195,
  "H": 13047,
  "vrt": "גליון עין יהב - 1948 - 100,000_grid_ITM.vrt"
 },
 "גליון אל עומר - 1948 -100,000.tif": {
  "gt": [
   183034.393125976,
   4.238709364,
   -0.005972371,
   504033.66582188,
   0.009767587,
   -4.247244821
  ],
  "W": 16302,
  "H": 11595,
  "vrt": "גליון אל עומר - 1948 -100,000_grid_ITM.vrt"
 }
}
home = QgsProject.instance().homePath()
d = os.path.join(home, '05_Historical_Maps', 'Historical_Maps1')
done = {}
for tif, p in SHEETS.items():
    src = os.path.join(d, tif); out = os.path.join(d, p['vrt'][:-4] + '.tif')
    if not os.path.exists(out):
        g = p['gt']; W, H = p['W'], p['H']
        gcps = [gdal.GCP(g[0] + g[1]*c + g[2]*r, g[3] + g[4]*c + g[5]*r, 0, c, r) for c, r in [(0, 0), (W, 0), (0, H), (W, H)]]
        tmp = '/vsimem/grid_tmp.vrt'
        gdal.Translate(tmp, src, format='VRT', GCPs=gcps, outputSRS='EPSG:2039')
        print('warping', tif); QApplication.processEvents()
        gdal.Warp(out, tmp, dstSRS='EPSG:2039', polynomialOrder=1, resampleAlg='bilinear', xRes=abs(g[1]), yRes=abs(g[5]),
                  multithread=True, warpMemoryLimit=512,
                  creationOptions=['COMPRESS=JPEG', 'JPEG_QUALITY=90', 'PHOTOMETRIC=YCBCR', 'TILED=YES', 'BIGTIFF=IF_SAFER'])
        gdal.Unlink(tmp)
        ds = gdal.Open(out, gdal.GA_Update)
        gdal.SetConfigOption('COMPRESS_OVERVIEW', 'JPEG'); gdal.SetConfigOption('PHOTOMETRIC_OVERVIEW', 'YCBCR')
        ds.BuildOverviews('AVERAGE', [2, 4, 8, 16, 32]); ds = None
    done[p['vrt']] = out
    print('ok', out); QApplication.processEvents()
n = 0
for lyr in QgsProject.instance().mapLayers().values():
    s = lyr.source().replace('\\', '/')
    for vrt, out in done.items():
        if s.endswith(vrt):
            lyr.setDataSource(out, lyr.name(), 'gdal'); lyr.triggerRepaint(); n += 1
print('repointed', n, 'layers. Save the project (Ctrl+S).')
