# Adds alternative 7 (settlement-extent version, Landsat 1987-1994) to MASTER group 1.2; renames the trail-map version to 7a. Re-runnable.
# usage: python3 add_alt7_settlement_to_master.py <ROOT>
import zipfile, os, sys, copy, shutil, datetime, uuid
from lxml import etree
ROOT=sys.argv[1]; M=os.path.join(ROOT,'Israel_Jordan_Arava_MASTER.qgz')
shutil.copy2(M,os.path.join(ROOT,'99_Archive','qgz_backups',f'Israel_Jordan_Arava_MASTER_BEFORE_alt7_settlement_{datetime.datetime.now():%Y-%m-%d_%H%M}.qgz'))
G='./01_Borders/Border_Alternatives_2026-11/alt7_settlement/Border_alternative_7_Sharon_line_settlement.gpkg|layername='
CR=' PhD research of Shimon Frish, Technion (supervisors Prof. Maxim Shoshany, Prof. Aviad Shapira). All rights reserved.'
SRC='Method: Landsat 5 TM surface reflectance (USGS Collection 2, path 174 row 39), NDVI of 4 winter scenes 1987-04-08, 1990-02-27, 1993-03-23, 1994-02-06; cultivated = NDVI > 0.17 in at least 2 of 4 scenes (30 m pixels, opening/closing). Israeli fields = cultivated patches east of the 1949 armistice line that lie inside Israel after 1994; Zofar enclave fields kept separately; Jordanian fields (east of the 1994 border) excluded. The line = armistice/trail-map line (old alternative 7) pushed east to the outer edge of the Israeli fields, including the strip between each field and the line.'
L=[('alt7_settlement_line','חלופה 7: קו שרון – תחום ההתיישבות והחקלאות בפועל (Landsat 1987–1994)','line','123,44,191,255','1.0','solid',
    'Alternative 7 (revised 2026-11-25): de facto extent of Israeli settlement and agriculture before the 1994 treaty. Median 53 m east of the armistice line, up to 2.0 km; 27.1 km2 east of the armistice line (the trail-map version: 12.8 km2). '+SRC),
   ('israeli_zone_east_of_armistice','חלופה 7: תחום ישראלי בפועל ממזרח לקו שביתת הנשק','fill','253,230,138,255','0','solid',
    'Zone east of the 1949 armistice line held in practice by Israeli agriculture before 1994: the Israeli fields plus the strip between them and the line (16.1 km2). '+SRC),
   ('israeli_fields_east_of_armistice','חלופה 7: שדות ישראליים ממזרח לקו שביתת הנשק ומובלעת צופר (1987–1994)','fill','245,158,11,255','0','solid',
    'Cultivated fields east of the 1949 armistice line: Israeli fields (kind=israeli, 723 ha) and the Zofar enclave fields (kind=zofar_enclave, 79 ha, about 3 km east of the line, cultivated from 1987). '+SRC)]
z=zipfile.ZipFile(M); qn=[n for n in z.namelist() if n.endswith('.qgs')][0]
r=etree.fromstring(z.read(qn)); extra={n:z.read(n) for n in z.namelist() if n!=qn}; z.close()
top=r.find('layer-tree-group'); pl=r.find('projectlayers')
old={l.get('id') for l in r.iter('layer-tree-layer') if 'Border_alternative_7_Sharon_line_settlement' in l.get('source','')}
for l in list(r.iter('layer-tree-layer')):
    if l.get('id') in old: l.getparent().remove(l)
for m in list(pl):
    if m.find('id').text in old: pl.remove(m)
for e in list(r.iter('item'))+list(r.iter('layer')):
    if (e.text in old) or (e.get('id') in old): e.getparent().remove(e)
# rename trail-map version to 7a
REN={'חלופה 7: קו שרון – הקו בפועל בשנות ה-80 ותחילת ה-90':'חלופה 7א (גרסה קודמת): קו שרון לפי מפות סימון שבילים 1991–1993',
     'חלופה 7: שטחים בין קו שרון לקו שביתת הנשק':'חלופה 7א (גרסה קודמת): שטחים בין קו שרון לקו שביתת הנשק'}
for l in r.iter('layer-tree-layer'):
    if l.get('name') in REN:
        nn=REN[l.get('name')]; lid=l.get('id'); l.set('name',nn)
        for m in pl:
            if m.find('id').text==lid:
                m.find('layername').text=nn
                t=m.find('resourceMetadata/title')
                if t is not None: t.text=nn
grp=[g for g in top.iter('layer-tree-group') if g.get('name','').startswith('1.2')][0]
def tpl(key):
    t=[l for l in top.iter('layer-tree-layer') if key(l)][0]; return t,[m for m in pl if m.find('id').text==t.get('id')][0]
LT=tpl(lambda l:l.get('name','').startswith('חלופה: קו מרכז העמק'))
PT=tpl(lambda l:'Atlas_of_Jordan_2013_depression_unit' in l.get('source',''))
EXT=(160000,370000,280000,580000); WGS=(34.6,29.3,35.9,31.6)
for lay,name,kind,col,w,st,ab in L:
    tl_t,ml_t=LT if kind=='line' else PT
    src=G+lay; lid='ALT7S_'+uuid.uuid4().hex[:12]
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
            if n=='line_color': o.set('value',col)
            elif n=='line_width': o.set('value',w)
            elif n=='line_style': o.set('value',st)
    else:
        sym.set('alpha','0.6')
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
