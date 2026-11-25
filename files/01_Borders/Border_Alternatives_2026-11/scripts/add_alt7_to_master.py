# Adds alternative 7 (Sharon line, de facto 1980s-early 1990s) to MASTER group 1.2. Re-runnable. usage: python3 add_alt7_to_master.py <ROOT>
import zipfile, os, sys, copy, shutil, datetime, uuid
from lxml import etree
ROOT=sys.argv[1]; M=os.path.join(ROOT,'Israel_Jordan_Arava_MASTER.qgz')
shutil.copy2(M,os.path.join(ROOT,'99_Archive','qgz_backups',f'Israel_Jordan_Arava_MASTER_BEFORE_alt7_{datetime.datetime.now():%Y-%m-%d_%H%M}.qgz'))
G='./01_Borders/Border_Alternatives_2026-11/Border_alternative_7_Sharon_line.gpkg|layername='
CR=' PhD research of Shimon Frish, Technion (supervisors Prof. Maxim Shoshany, Prof. Aviad Shapira). All rights reserved.'
SRC='Sources: Survey of Israel / SPNI hiking and trail-marking maps 1:50,000, sheet 14 (Oct 1993) and sheet 17 (Nov 1991), purple border band; local maps "the border near Yahel / Yotvata before and after the peace treaty" (blue dashed line; Yahel map shifted -350 m E, +50 m N to fit its own 1994 line); gaps filled with the armistice line from the historical 1:100k maps.'
L=[('alt7_sharon_line','חלופה 7: קו שרון – הקו בפועל בשנות ה-80 ותחילת ה-90','line','123,44,191,255','0.8','solid',
    'Alternative 7: "Sharon line" = the de facto line held by Israel in the 1980s and early 1990s, before the 1994 treaty. 63% of its length from period maps, the rest = armistice line. '+SRC),
   ('alt7_vs_armistice_areas','חלופה 7: שטחים בין קו שרון לקו שביתת הנשק','fill','253,230,138,255','0','solid',
    'Areas between alternative 7 and the armistice line. 12.8 km2 lie east of the armistice line (held by Israel de facto), 0.25 km2 west of it. '+SRC)]
z=zipfile.ZipFile(M); qn=[n for n in z.namelist() if n.endswith('.qgs')][0]
r=etree.fromstring(z.read(qn)); extra={n:z.read(n) for n in z.namelist() if n!=qn}; z.close()
top=r.find('layer-tree-group'); pl=r.find('projectlayers')
old={l.get('id') for l in r.iter('layer-tree-layer') if 'Border_alternative_7_Sharon_line' in l.get('source','')}
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
    src=G+lay; lid='ALT7_'+uuid.uuid4().hex[:12]
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
