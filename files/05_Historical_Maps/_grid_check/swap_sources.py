# Repoint the 9 historical sheet layers in MASTER.qgz to the grid-corrected VRTs (ITM). Backup first.
import zipfile, shutil, os, copy, datetime
from lxml import etree
R=os.path.expanduser('~/mnt/Israel-Jordan-Arava/'); Q=R+'Israel_Jordan_Arava_MASTER.qgz'
H='./05_Historical_Maps/Historical_Maps1/'
MAP={'0001_FL266344297_modified.tif':'0001_FL266344297_modified_modified_grid_ITM.vrt'}
for b in ['0001_FL44748971_modified','0001_FL44749060_modified','0001_FL44749077_modified','גליון אילת - 1955 - 100,000','גליון אל עומר - 1948 -100,000','גליון עין יהב - 1948 - 100,000','גליון עין עדין - 1949 - 100,000','גליון נחל הערבה - 1958 -100,000']:
    MAP[b+'.tif']=b+'_grid_ITM.vrt'
MAP={H+k:H+v for k,v in MAP.items()}
for v in MAP.values(): assert os.path.exists(R+v[2:]), v
bk=R+'99_Archive/qgz_backups/Israel_Jordan_Arava_MASTER_BEFORE_grid_vrt_'+datetime.datetime.now().strftime('%Y-%m-%d_%H%M')+'.qgz'
shutil.copy2(Q,bk); print('backup',bk)
z=zipfile.ZipFile(Q); names=z.namelist(); data={n:z.read(n) for n in names}; z.close()
qgs=[n for n in names if n.endswith('.qgs')][0]
root=etree.fromstring(data[qgs])
ref=[ml for ml in root.iter('maplayer') if ml.findtext('datasource','').endswith('50,000.tif')][0].find('srs')
n=0
for ml in root.iter('maplayer'):
    ds=ml.find('datasource')
    if ds is not None and ds.text in MAP:
        ds.text=MAP[ds.text]; old=ml.find('srs'); ml.replace(old,copy.deepcopy(ref)); n+=1
        print('layer',ml.findtext('layername'),'->',ds.text)
for lt in root.iter('layer-tree-layer'):
    if lt.get('source') in MAP: lt.set('source',MAP[lt.get('source')])
assert n==9, n
data[qgs]=etree.tostring(root,xml_declaration=False,encoding='utf-8')
if not data[qgs].startswith(b'<!DOCTYPE'): data[qgs]=b'<!DOCTYPE qgis PUBLIC "http://mrcc.com/qgis.dtd" "SYSTEM">\n'+data[qgs]
import io
buf=io.BytesIO()
with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as zo:
    for k in names: zo.writestr(k,data[k])
open(Q,'wb').write(buf.getvalue()); print('done',n)
