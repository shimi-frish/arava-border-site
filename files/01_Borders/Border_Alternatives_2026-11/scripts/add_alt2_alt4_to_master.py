# Adds alternatives 2 and 4 (historical) + historical valley polygon to MASTER group 1.2. Re-runnable. usage: python3 add_alt2_alt4_to_master.py <ROOT>
import zipfile, os, sys, copy, shutil, datetime, uuid
from lxml import etree
ROOT=sys.argv[1]; M=os.path.join(ROOT,'Israel_Jordan_Arava_MASTER.qgz')
shutil.copy2(M,os.path.join(ROOT,'99_Archive','qgz_backups',f'Israel_Jordan_Arava_MASTER_BEFORE_alt2_alt4_{datetime.datetime.now():%Y-%m-%d_%H%M}.qgz'))
G='./01_Borders/Border_Alternatives_2026-11/Border_alternatives_2_4_historical.gpkg|layername='
CR=' PhD research of Shimon Frish, Technion (supervisors Prof. Maxim Shoshany, Prof. Aviad Shapira). All rights reserved.'
SRC='Sources: Bender 1968 geological map 1:250k; USGS PP560-I / Bender 1974 (Kempf 2023 vector); Atlas of Jordan 2013 fig I.2; AMS K737 1:50k Aqaba 1960; AMS K502 1:250k 1961; Jordan tourist map 1962; Powell et al. 2015.'
L=[('alt2_historical_centre_line','חלופה 2: קו מרכז העמק לפי עדויות היסטוריות ומפות לא-ישראליות','line','27,122,58,255','0.8','solid',
    'Alternative 2: valley centre line from the valley edges drawn on historical and non-Israeli maps (per 250 m cross-section: median of available edges on each side, 2 km running median; centre = midpoint, smoothed). '+SRC),
   ('alt4_historical_thalweg_line','חלופה 4: קו התלווג לפי עדויות היסטוריות (AMS K502 1961 ומפות 1915)','line','217,95,2,255','0.8','solid',
    'Alternative 4: thalweg per historical maps = least-cost route along drainage drawn on AMS K502 1:250k (1961) and large wadi beds of British 1:125k sheets (1914-15), inside the historical valley. Between Eilat and Gav HaArava the maps draw no continuous channel, so the line there is interpolated.'),
   ('historical_valley_polygon','עמק הערבה לפי מפות היסטוריות ולא-ישראליות (חציון, 2,662 קמ"ר)','fill','233,220,181,255','0','solid','Valley polygon per historical / non-Israeli maps (median edges). '+SRC)]
z=zipfile.ZipFile(M); qn=[n for n in z.namelist() if n.endswith('.qgs')][0]
r=etree.fromstring(z.read(qn)); extra={n:z.read(n) for n in z.namelist() if n!=qn}; z.close()
top=r.find('layer-tree-group'); pl=r.find('projectlayers')
old={l.get('id') for l in r.iter('layer-tree-layer') if 'Border_alternatives_2_4_historical' in l.get('source','')}
for l in list(r.iter('layer-tree-layer')):
    if l.get('id') in old: l.getparent().remove(l)
for m in list(pl):
    if m.find('id').text in old: pl.remove(m)
for e in list(r.iter('item'))+list(r.iter('layer')):
    if (e.text in old) or (e.get('id') in old): e.getparent().remove(e)
grp=[g for g in top.iter('layer-tree-group') if g.get('name','').startswith('1.2')][0]
def tpl(key):
    t=[l for l in top.iter('layer-tree-layer') if key(l)][0]; return t,[m for m in pl if m.find('id').text==t.get('id')][0]
LT=tpl(lambda l:l.get('name','').startswith('חלופה: קו מרכז העמק'))
PT=tpl(lambda l:'Atlas_of_Jordan_2013_depression_unit' in l.get('source',''))
EXT=(160000,370000,280000,580000); WGS=(34.6,29.3,35.9,31.6)
pos=0
for lay,name,kind,col,w,st,ab in L:
    tl_t,ml_t=LT if kind=='line' else PT
    src=G+lay; lid='ALT24_'+uuid.uuid4().hex[:12]
    m=copy.deepcopy(ml_t); m.find('id').text=lid; m.find('datasource').text=src; m.find('layername').text=name
    if m.find('provider') is not None: m.find('provider').text='ogr'
    for tag,v in (('extent',EXT),('wgs84extent',WGS)):
        e=m.find(tag)
        if e is not None:
            for k,x in zip(('xmin','ymin','xmax','ymax'),v): e.find(k).text=repr(float(x))
    rm=m.find('resourceMetadata')
    if rm is not None:
        for t,v in (('title',name),('abstract',ab+CR)):
            el=rm.find(t)
            if el is None: el=etree.SubElement(rm,t)
            el.text=v
    sym=m.find('.//renderer-v2//symbol')
    if kind=='line':
        for o in sym.iter('Option'):
            n=o.get('name')
            if n in('line_color',): o.set('value',col)
            elif n=='line_width': o.set('value',w)
            elif n=='line_style': o.set('value',st)
    else:
        sym.set('alpha','0.5')
        for o in sym.iter('Option'):
            n=o.get('name')
            if n=='color': o.set('value',col)
            elif n=='style': o.set('value','solid')
            elif n=='outline_style': o.set('value','no')
    pl.append(m)
    tl=copy.deepcopy(tl_t)
    for c in list(tl): tl.remove(c)
    tl.set('id',lid); tl.set('source',src); tl.set('name',name); tl.set('checked','Qt::Unchecked')
    grp.append(tl)
    co=top.find('custom-order')
    if co is not None: etree.SubElement(co,'item').text=lid
    for lo in r.iter('layerorder'): etree.SubElement(lo,'layer',id=lid)
with zipfile.ZipFile(M,'w',zipfile.ZIP_DEFLATED) as zo:
    zo.writestr(qn,etree.tostring(r,encoding='utf-8',xml_declaration=True))
    for k,v in extra.items(): zo.writestr(k,v)
print('ok',len(list(pl)))
