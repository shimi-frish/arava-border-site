# Adds trail-marking sheets 19 (1998) and 20 (Aug 1996), grid-georeferenced to ITM, to MASTER group 3.4.2 / Israeli,
# and renames alt 8 (now completed from these sheets). usage: python3 add_sheets19_20_to_master.py <ROOT> [qgz name]
import zipfile, os, sys, copy, shutil, datetime, uuid
from lxml import etree
ROOT=sys.argv[1]; QN=sys.argv[2] if len(sys.argv)>2 else 'Israel_Jordan_Arava_MASTER.qgz'; M=os.path.join(ROOT,QN)
shutil.copy2(M,os.path.join(ROOT,'99_Archive','qgz_backups',QN.replace('.qgz','')+f'_BEFORE_sheets19_20_{datetime.datetime.now():%Y-%m-%d_%H%M}.qgz'))
D='./05_Historical_Maps/B_Topographic_Thematic_Maps/Israeli/Topographic_sheets/'
CR=' PhD research of Shimon Frish, Technion (supervisors Prof. Maxim Shoshany, Prof. Aviad Shapira). All rights reserved.'
NEW=[('גליון 19 - מישורי פארן וגב הערבה - 1998_grid_ITM.tif','מפת סימון שבילים 1:50,000 – גיליון 19 "מישורי פארן וגב הערבה" (1998)',
  [161400.0,429700.0,219000.0,469600.0],[34.60083,29.95464,35.19971,30.31593],
  'Trail-marking map (Hiking and trail-marking map) 1:50,000, sheet 19 "Paran plains and Arava ridge", Survey of Israel and the Society for the Protection of Nature in Israel, 1998 (after the 1994 peace treaty: shows the 1994 border as a chain of black crosses). Scan purchased by the researcher. Georeferenced to ITM on the printed old Israeli grid (2nd-order polynomial, RMS about 10 m). The border traced from it (median 37 m from the 1994 border) completes alternative 8 between sheet 17 and Yahel and between Yahel and Yotvata.'),
 ('גליון 20 - הרי אילת - אוגוסט 1996_grid_ITM.tif','מפת סימון שבילים 1:50,000 – גיליון 20 "הרי אילת" (אוגוסט 1996)',
  [173600.0,376500.0,213597.5,434400.0],[34.72920,29.47524,35.14403,29.99839],
  'Trail-marking map 1:50,000, sheet 20 "Eilat Mountains", Survey of Israel and the Society for the Protection of Nature in Israel, August 1996 (after the 1994 peace treaty: shows the 1994 border as a chain of black crosses). Scan purchased by the researcher. Georeferenced to ITM on the printed old Israeli grid (2nd-order polynomial, RMS about 25 m). The border traced from it (median 56 m from the 1994 border) completes alternative 8 from Yotvata south to Eilat.')]
A8_OLD='חלופה 8: קו רשמי ישראלי טרם ההסכם (מפות סימון שבילים 1991–1993)'
A8_NEW='חלופה 8: קו רשמי ישראלי טרם ההסכם (מפות סימון שבילים 1991–1993, השלמה מ-1996/1998)'
A8_NOTE=' Update 2026-11-26: the stretches previously filled from the armistice line were replaced (at the researcher\'s request) by the border traced from trail-marking sheets 19 (1998) and 20 (Aug 1996), printed AFTER the treaty and therefore showing the 1994 border. Composition: 61% pre-treaty maps, 34% sheets 19/20, 2% armistice line; 181 km; median 139 m from the 1994 border.'
z=zipfile.ZipFile(M); qn=[n for n in z.namelist() if n.endswith('.qgs')][0]
r=etree.fromstring(z.read(qn)); extra={n:z.read(n) for n in z.namelist() if n!=qn}; z.close()
top=r.find('layer-tree-group'); pl=r.find('projectlayers')
old={l.get('id') for l in r.iter('layer-tree-layer') if any(f for f,*_ in NEW if f in l.get('source',''))}
for l in list(r.iter('layer-tree-layer')):
    if l.get('id') in old: l.getparent().remove(l)
for m in list(pl):
    if m.find('id').text in old: pl.remove(m)
for e in list(r.iter('item'))+list(r.iter('layer')):
    if (e.text in old) or (e.get('id') in old): e.getparent().remove(e)
g342=[g for g in top.iter('layer-tree-group') if g.get('name','').startswith('3.4.2')][0]
gis=[g for g in g342 if g.tag=='layer-tree-group' and g.get('name','').startswith('ישראליות')][0]
tpl=[l for l in top.iter('layer-tree-layer') if l.get('source','').endswith('_grid_ITM.tif') and 'Topographic_sheets' in l.get('source','')]
tl_tpl=tpl[0]; ml_tpl=[m for m in pl if m.find('id').text==tl_tpl.get('id')][0]
def setmeta(m,name,ab):
    rm=m.find('resourceMetadata')
    if rm is None: return
    for t,v in (('title',name),('abstract',ab)):
        el=rm.find(t)
        if el is None: el=etree.SubElement(rm,t)
        el.text=v
for f,name,ext,wgs,ab in NEW:
    src=D+f; lid='TRAIL1920_'+uuid.uuid4().hex[:12]
    m=copy.deepcopy(ml_tpl); m.find('id').text=lid; m.find('datasource').text=src; m.find('layername').text=name
    for tag,v in (('extent',ext),('wgs84extent',wgs)):
        e=m.find(tag)
        if e is not None:
            for k,x in zip(('xmin','ymin','xmax','ymax'),v): e.find(k).text=repr(float(x))
    setmeta(m,name,ab+CR)
    rr=m.find('.//rasterrenderer')
    if rr is not None:
        rr.set('type','multibandcolor'); rr.set('redBand','1'); rr.set('greenBand','2'); rr.set('blueBand','3'); rr.set('alphaBand','-1')
    pl.append(m)
    tl=copy.deepcopy(tl_tpl)
    for c in list(tl): tl.remove(c)
    tl.set('id',lid); tl.set('source',src); tl.set('name',name); tl.set('checked','Qt::Unchecked')
    gis.append(tl)
    co=top.find('custom-order')
    if co is not None: etree.SubElement(co,'item').text=lid
    for lo in r.iter('layerorder'): etree.SubElement(lo,'layer',id=lid)
n8=0
for tl in top.iter('layer-tree-layer'):
    if tl.get('name') in (A8_OLD,A8_NEW):
        tl.set('name',A8_NEW); m=[m for m in pl if m.find('id').text==tl.get('id')][0]; m.find('layername').text=A8_NEW
        rm=m.find('resourceMetadata')
        if rm is not None:
            t=rm.find('title'); t=t if t is not None else etree.SubElement(rm,'title'); t.text=A8_NEW
            ab=rm.find('abstract'); ab=ab if ab is not None else etree.SubElement(rm,'abstract')
            if 'Update 2026-11-26' not in (ab.text or ''): ab.text=(ab.text or '')+A8_NOTE
        n8+=1
with zipfile.ZipFile(M,'w',zipfile.ZIP_DEFLATED) as zo:
    zo.writestr(qn,etree.tostring(r,encoding='utf-8',xml_declaration=True))
    for k,v in extra.items(): zo.writestr(k,v)
print('ok template',tl_tpl.get('name'),'| alt8 renamed',n8,'| layers',len(list(pl)))
