# Adds the 4 GMBA layers (GMBA_Arava_layers.gpkg) to MASTER group 2.3. Re-runnable. usage: python3 add_gmba_to_master.py <ROOT>
import zipfile, os, sys, copy, shutil, datetime, uuid, re
from lxml import etree
ROOT = sys.argv[1]; M = os.path.join(ROOT, 'Israel_Jordan_Arava_MASTER.qgz')
stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
shutil.copy2(M, os.path.join(ROOT, '99_Archive', 'qgz_backups', f'Israel_Jordan_Arava_MASTER_BEFORE_gmba_{stamp}.qgz'))
G = './06_Valley_Analysis/Non_Israeli_Maps_2026-11-23/GMBA_2022/GMBA_Arava_layers.gpkg|layername='
CREDIT = ' PhD research of Shimon Frish, Technion (supervisors Prof. Maxim Shoshany, Prof. Aviad Shapira). All rights reserved.'
V2 = ('GMBA Mountain Definition v2.0 algorithm (Snethlage et al. 2022, Scientific Data 9:149) re-implemented on the Arava: ruggedness '
      '(max-min elevation) in 8 circular windows r = 240 m to 4.8 km with thresholds 3-404 m, all must pass; majority filter; flats <100 km2 '
      'inside mountains = mountain. DEM Copernicus GLO-30 aggregated to 240 m. Not the official GMBA layer (earthenv.org blocks automated access).')
OF = ('Official GMBA mountain mask, release 4 (2021): GMBA_2021_MntnMask_EarthEnv_30s_V2.tif, University of Bern, DOI 10.7892/boris.83486; '
      'rule of Koerner et al. 2011 (elevation range >= 200 m in 3x3 cells of ~1 km, EarthEnv/GMTED2010). Cropped to the Arava and polygonised 2026-11-24.')
VAL = ' "Valley" = non-mountain area touching the straight line Dead Sea-Eilat, within 20 km of it.'
L = [('gmba_v2_mountains', 'הרים לפי הגדרת GMBA v2.0 (2022, הפעלה של האלגוריתם על הערבה)', V2, ('160,110,60,255', '160,110,60,0', 'solid', 'no', 0.45)),
     ('gmba_v2_valley', 'העמק לפי GMBA v2.0 (4,702 קמ"ר, IoU 0.53)', V2 + VAL, ('230,170,0,255', '230,170,0,255', 'no', 'solid', 1.0)),
     ('gmba_official_2021_mountains', 'מסכת ההרים הרשמית של GMBA 2021 (1 ק"מ)', OF, ('93,58,26,255', '93,58,26,255', 'no', 'dash', 1.0)),
     ('gmba_official_2021_valley', 'העמק לפי מסכת ההרים הרשמית של GMBA 2021 (5,788 קמ"ר)', OF + VAL, ('200,120,0,255', '200,120,0,255', 'no', 'dot', 1.0))]
z = zipfile.ZipFile(M); qn = [n for n in z.namelist() if n.endswith('.qgs')][0]
r = etree.fromstring(z.read(qn)); extra = {n: z.read(n) for n in z.namelist() if n != qn}; z.close()
top = r.find('layer-tree-group'); pl = r.find('projectlayers')
old = {l.get('id') for l in r.iter('layer-tree-layer') if 'GMBA_Arava_layers.gpkg' in l.get('source', '')}
for l in list(r.iter('layer-tree-layer')):
    if l.get('id') in old: l.getparent().remove(l)
for m in list(pl):
    if m.find('id').text in old: pl.remove(m)
for e in list(r.iter('item')) + list(r.iter('layer')):
    if (e.text in old) or (e.get('id') in old): e.getparent().remove(e)
grp = [g for g in top.iter('layer-tree-group') if g.get('name', '').startswith('2.3')][0]
tl_tpl = [l for l in top.iter('layer-tree-layer') if 'Atlas_of_Jordan_2013_depression_unit' in l.get('source', '')][0]
ml_tpl = [m for m in pl if m.find('id').text == tl_tpl.get('id')][0]
EXT = (170000, 360000, 285000, 580000); WGS = (34.70, 29.30, 35.80, 31.70)
for lay, name, ab, (fc, oc, fs, os_, alpha) in L:
    src = G + lay; lid = 'GMBA_' + uuid.uuid4().hex[:12]
    m = copy.deepcopy(ml_tpl); m.find('id').text = lid; m.find('datasource').text = src; m.find('layername').text = name
    for tag, v in (('extent', EXT), ('wgs84extent', WGS)):
        e = m.find(tag)
        if e is not None:
            for k, x in zip(('xmin', 'ymin', 'xmax', 'ymax'), v): e.find(k).text = repr(float(x))
    rm = m.find('resourceMetadata')
    if rm is not None:
        for t, v in (('title', name), ('abstract', ab + CREDIT)):
            el = rm.find(t)
            if el is None: el = etree.SubElement(rm, t)
            el.text = v
        for k in rm.findall('keywords'): rm.remove(k)
        kwe = etree.SubElement(rm, 'keywords', vocabulary='gmd:topicCategory')
        for k in ('GMBA', 'mountains', 'ruggedness', 'Arava valley'): etree.SubElement(kwe, 'keyword').text = k
    sym = m.find('.//renderer-v2//symbol'); sym.set('alpha', str(alpha))
    for o in sym.iter('Option'):
        n = o.get('name')
        if n == 'color': o.set('value', fc)
        elif n == 'outline_color': o.set('value', oc)
        elif n == 'style': o.set('value', 'solid' if fs == 'solid' else 'no')
        elif n == 'outline_style': o.set('value', 'no' if os_ == 'no' else os_)
    pl.append(m)
    tl = copy.deepcopy(tl_tpl)
    for c in list(tl): tl.remove(c)
    tl.set('id', lid); tl.set('source', src); tl.set('name', name); tl.set('checked', 'Qt::Unchecked')
    grp.append(tl)
    co = top.find('custom-order')
    if co is not None: etree.SubElement(co, 'item').text = lid
    for lo in r.iter('layerorder'): etree.SubElement(lo, 'layer', id=lid)
with zipfile.ZipFile(M, 'w', zipfile.ZIP_DEFLATED) as zo:
    zo.writestr(qn, etree.tostring(r, encoding='utf-8', xml_declaration=True))
    for k, v in extra.items(): zo.writestr(k, v)
print('ok', len(list(pl)))
