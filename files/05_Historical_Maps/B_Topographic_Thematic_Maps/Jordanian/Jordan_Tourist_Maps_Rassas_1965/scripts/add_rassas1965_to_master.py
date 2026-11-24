# Adds Rassas 1965 Jordan tourist map (1:2.5M inset, georeferenced) to MASTER 3.4.2 > Jordanian maps,
# and its Wadi Araba border line to 1.3 historical border lines. Re-runnable.  usage: python3 add_rassas1965_to_master.py <ROOT>
import zipfile, os, sys, copy, shutil, datetime, uuid
from lxml import etree
ROOT = sys.argv[1]; M = os.path.join(ROOT, 'Israel_Jordan_Arava_MASTER.qgz')
stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
shutil.copy2(M, os.path.join(ROOT, '99_Archive', 'qgz_backups', f'Israel_Jordan_Arava_MASTER_BEFORE_rassas1965_{stamp}.qgz'))
D = './05_Historical_Maps/B_Topographic_Thematic_Maps/Jordanian/Jordan_Tourist_Maps_Rassas_1965/'
RSRC = D + 'georef/Rassas1965_Jordan_inset_ITM.tif'
VSRC = D + 'Rassas1965_Arava_border.gpkg|layername=Rassas1965_Arava_border'
RNAME = 'מפת התיירות של ירדן – רסאס 1965 (מפת ירדן 1:2,500,000)'
VNAME = 'גבול ירדן בערבה לפי מפת התיירות הירדנית 1965 (רסאס, 1:2,500,000)'
CREDIT = ' PhD research of Shimon Frish, Technion (supervisors Prof. Maxim Shoshany, Prof. Aviad Shapira). All rights reserved.'
RAB = ('The Hashemite Kingdom of Jordan Tourist Maps, revised, prepared and drawn by Abdul Rahman Rassas, licensed surveyor, Amman, '
       'Sept. 1965; recommended and approved by the Tourism Authority, June 1965. Inset map of Jordan, scale approx. 1:2,500,000. '
       'Georeferenced 2026-11-24 on 26 town positions, 2nd-order polynomial, RMS about 6 km (4 km for the southern towns); schematic map.' + CREDIT)
VAB = ('Jordan border along Wadi Araba as drawn (dashed) on the 1:2,500,000 inset of the Rassas 1965 Jordan tourist map; the label "Wadi Araba" '
       'is written along this line. Digitised 2026-11-24 with a local affine fit on 13 southern towns (RMS 4.3 km). '
       'Versus the 1994 border: median 1.0 km, max 3.7 km.' + CREDIT)
z = zipfile.ZipFile(M); qn = [n for n in z.namelist() if n.endswith('.qgs')][0]
r = etree.fromstring(z.read(qn)); extra = {n: z.read(n) for n in z.namelist() if n != qn}; z.close()
top = r.find('layer-tree-group'); pl = r.find('projectlayers')
old = {l.get('id') for l in r.iter('layer-tree-layer') if 'Rassas_1965' in l.get('source', '')}
for l in list(r.iter('layer-tree-layer')):
    if l.get('id') in old: l.getparent().remove(l)
for m in list(pl):
    if m.find('id').text in old: pl.remove(m)
for e in list(r.iter('item')) + list(r.iter('layer')):
    if (e.text in old) or (e.get('id') in old): e.getparent().remove(e)
def grp(prefix): return [g for g in top.iter('layer-tree-group') if g.get('name', '').startswith(prefix)][0]
def add(tpl_src_key, src, name, ab, kw, group, ext, wgs):
    tl_tpl = [l for l in top.iter('layer-tree-layer') if tpl_src_key in l.get('source', '')][0]
    ml_tpl = [m for m in pl if m.find('id').text == tl_tpl.get('id')][0]
    lid = 'RAS65_' + uuid.uuid4().hex[:12]
    m = copy.deepcopy(ml_tpl); m.find('id').text = lid; m.find('datasource').text = src; m.find('layername').text = name
    for tag, v in (('extent', ext), ('wgs84extent', wgs)):
        e = m.find(tag)
        if e is not None:
            for k, x in zip(('xmin', 'ymin', 'xmax', 'ymax'), v): e.find(k).text = repr(float(x))
    rm = m.find('resourceMetadata')
    if rm is not None:
        for t, v in (('title', name), ('abstract', ab)):
            el = rm.find(t)
            if el is None: el = etree.SubElement(rm, t)
            el.text = v
        for k in rm.findall('keywords'): rm.remove(k)
        kwe = etree.SubElement(rm, 'keywords', vocabulary='gmd:topicCategory')
        for k in kw: etree.SubElement(kwe, 'keyword').text = k
    rr = m.find('.//rasterrenderer')
    if rr is not None and src.endswith('.tif'):
        rr.set('type', 'multibandcolor'); rr.set('redBand', '1'); rr.set('greenBand', '2'); rr.set('blueBand', '3'); rr.set('alphaBand', '4')
    pl.append(m)
    tl = copy.deepcopy(tl_tpl)
    for c in list(tl): tl.remove(c)
    tl.set('id', lid); tl.set('source', src); tl.set('name', name); tl.set('checked', 'Qt::Unchecked')
    group.insert(0, tl)
    co = top.find('custom-order')
    if co is not None: etree.SubElement(co, 'item').text = lid
    for lo in r.iter('layerorder'): etree.SubElement(lo, 'layer', id=lid)
KW = ['1965', 'Jordan', 'tourist map', 'Rassas', 'Wadi Araba', 'border']
add('Armistice_Map_1949_Palestine_250k_ITM.tif', RSRC, RNAME, RAB, KW, grp('ירדניות'),
    (100000, 330000, 560000, 860000), (34.11, 28.96, 39.05, 33.74))
add('Ottoman_provincial_boundary_1916.gpkg', VSRC, VNAME, VAB, KW, grp('1.3'),
    (194000, 383000, 253000, 552000), (34.95, 29.52, 35.57, 31.05))
with zipfile.ZipFile(M, 'w', zipfile.ZIP_DEFLATED) as zo:
    zo.writestr(qn, etree.tostring(r, encoding='utf-8', xml_declaration=True))
    for k, v in extra.items(): zo.writestr(k, v)
print('ok')
