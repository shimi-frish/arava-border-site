# Adds Kitchener/Armstrong 1886 Wady el Arabah map to MASTER (3.4, British early maps group, renamed 1883-1916)
import zipfile, os, sys, copy, shutil, datetime, uuid
from lxml import etree
ROOT=sys.argv[1]; M=os.path.join(ROOT,'Israel_Jordan_Arava_MASTER.qgz')
stamp=datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
shutil.copy2(M,os.path.join(ROOT,'99_Archive','qgz_backups',f'Israel_Jordan_Arava_MASTER_BEFORE_kitchener_{stamp}.qgz'))
OLD='מפות בריטיות מוקדמות 1914–1916 (סיני וואדי ערבה)'; NEW='מפות בריטיות מוקדמות 1883–1916 (סיני וואדי ערבה)'
SRC='./05_Historical_Maps/Kitchener_Arabah_1883/Kitchener_Arabah_1883_ITM.tif'
NAME='ואדי ערבה 1:380,160 – מדידת קיצ\'נר 1883 (ארמסטרונג 1886)'
AB=('Map of the Wady el Arabah from the surveys of Major Kitchener, R.E., reduced from the 3/8 inch map by Geo. Armstrong; geological details by Prof. Hull. '
    'Stanford, London, 1886 (Hull, Memoir on the Geology and Geography of Arabia Petraea, SWP). Scale 6 miles to an inch. '
    'Scan: National Library of Israel (Eran Laor collection, FL33249947) via Wikimedia Commons, public domain (3840 px version). '
    'Georeferenced 2026-11-19 on 19 frame graticule ticks (10\'), WGS84 assumed, 2nd-order polynomial, RMS ~100 m vs frame. '
    'Map content errors vs reality: Masada 0.8 km, Jebel Harun 2.1 km E, Aqaba 3.8 km, Ein Ghadian/Yotvata 4.7 km S.')
EXT=[163120.0,360560.0,264360.0,583280.0]; WGS=[34.61245933114421,29.331010024879976,35.676291478332224,31.341297965470076]
z=zipfile.ZipFile(M); qn=[n for n in z.namelist() if n.endswith('.qgs')][0]
r=etree.fromstring(z.read(qn)); extra={n:z.read(n) for n in z.namelist() if n!=qn}; z.close()
top=r.find('layer-tree-group'); pl=r.find('projectlayers')
grp=[g for g in top.iter('layer-tree-group') if g.get('name') in (OLD,NEW)][0]; grp.set('name',NEW)
# remove previous run
old={l.get('id') for l in grp.findall('layer-tree-layer') if 'Kitchener_Arabah_1883' in l.get('source','')}
for l in list(grp):
    if l.get('id') in old: grp.remove(l)
for m in list(pl):
    if m.find('id').text in old: pl.remove(m)
for e in list(r.iter('item'))+list(r.iter('layer')):
    if (e.text in old) or (e.get('id') in old): e.getparent().remove(e)
tl_tpl=[l for l in grp.findall('layer-tree-layer') if 'Sinai_Wadi_el_Jeib_1915' in l.get('source','')][0]
ml_tpl=[m for m in pl if m.find('id').text==tl_tpl.get('id')][0]
lid='KIT_'+uuid.uuid4().hex[:12]
m=copy.deepcopy(ml_tpl); m.find('id').text=lid; m.find('datasource').text=SRC; m.find('layername').text=NAME
for tag,v in (('extent',EXT),('wgs84extent',WGS)):
    e=m.find(tag)
    if e is not None:
        for k,x in zip(('xmin','ymin','xmax','ymax'),v): e.find(k).text=repr(float(x))
rm=m.find('resourceMetadata')
if rm is not None:
    if rm.find('title') is not None: rm.find('title').text=NAME
    if rm.find('abstract') is not None: rm.find('abstract').text=AB
pl.append(m)
tl=copy.deepcopy(tl_tpl); tl.set('id',lid); tl.set('source',SRC); tl.set('name',NAME); tl.set('checked','Qt::Unchecked')
grp.insert(list(grp).index(tl_tpl),tl)
co=top.find('custom-order')
if co is not None: etree.SubElement(co,'item').text=lid
for lo in r.iter('layerorder'): etree.SubElement(lo,'layer',id=lid)
with zipfile.ZipFile(M,'w',zipfile.ZIP_DEFLATED) as zo:
    zo.writestr(qn,etree.tostring(r,encoding='utf-8',xml_declaration=True))
    for k,v in extra.items(): zo.writestr(k,v)
print('ok',NEW,[c.get('name') for c in grp if c.tag=='layer-tree-layer'])
