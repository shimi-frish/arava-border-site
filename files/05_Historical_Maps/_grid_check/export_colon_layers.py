# -*- coding: utf-8 -*-
# Run in QGIS Python console. Exports every vector layer whose file name contains ':' (stored in a hidden
# NTFS stream) to a normal GeoPackage in 01_Borders, and repoints the layer to it. Originals are not deleted.
import os
from qgis.core import QgsProject, QgsMapLayer, QgsVectorFileWriter, QgsCoordinateTransformContext
home = QgsProject.instance().homePath()
NAMES = {'שביתת': 'Armistice_line_hist_maps.gpkg', 'המנדט': 'Mandate_border_1942_digitized.gpkg'}
n = 0
for lyr in list(QgsProject.instance().mapLayers().values()):
    if lyr.type() != QgsMapLayer.VectorLayer: continue
    path = lyr.source().split('|')[0]
    base = os.path.basename(path)
    if ':' not in base: continue
    outname = next((v for k, v in NAMES.items() if k in base), base.replace(':', '-').rsplit('.', 1)[0] + '.gpkg')
    out = os.path.join(home, '01_Borders', outname)
    opt = QgsVectorFileWriter.SaveVectorOptions(); opt.driverName = 'GPKG'; opt.fileEncoding = 'UTF-8'
    err = QgsVectorFileWriter.writeAsVectorFormatV3(lyr, out, QgsCoordinateTransformContext(), opt)
    if err[0] != QgsVectorFileWriter.NoError:
        print('FAILED', lyr.name(), err); continue
    print('exported', lyr.name(), lyr.featureCount(), 'features ->', out)
    lyr.setDataSource(out, lyr.name(), 'ogr'); n += 1
print(n, 'layers exported and repointed. Save the project (Ctrl+S).')
