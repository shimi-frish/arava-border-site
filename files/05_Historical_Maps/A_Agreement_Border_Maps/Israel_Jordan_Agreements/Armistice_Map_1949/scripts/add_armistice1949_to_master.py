# Adds the signed 1949 Israel-Jordan armistice map (Palestine 1:250k N+S sheets, 1946 print) to MASTER,
# group 3.4 > "מפות הסכמים וקווי גבול (רסטר)", with metadata (title/abstract/keywords). Re-runnable.
# usage: python3 add_armistice1949_to_master.py <ROOT> <extent.json>
import zipfile, os, sys, copy, shutil, datetime, uuid, json
from lxml import etree
ROOT = sys.argv[1]; M = os.path.join(ROOT, 'Israel_Jordan_Arava_MASTER.qgz'); EXT = json.load(open(sys.argv[2]))
stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
shutil.copy2(M, os.path.join(ROOT, '99_Archive', 'qgz_backups', f'Israel_Jordan_Arava_MASTER_BEFORE_armistice1949_{stamp}.qgz'))
SRC = './05_Historical_Maps/Armistice_Map_1949/georef/Armistice_Map_1949_Palestine_250k_ITM.tif'
NAME = 'מפת הסכם שביתת הנשק ישראל–ירדן 1949 (פלשתינה 1:250,000, מהדורת 1946, חתומה)'
AB = ('Map annexed to the Israel-Hashemite Jordan Kingdom General Armistice Agreement, Rhodes, 3 April 1949, signed '
      '(top left of North sheet) by Col. A. Sudki El-Jundi (Jordan) and Moshe Dayan (Israel). Base map: Palestine 1:250,000 '
      'North and South sheets (layered), compiled, drawn & printed by Survey of Palestine Aug. 1944, road revision Jan. 1946; '
      'reproduced by No. 1 Base Survey Drawing and Photo Process Office Apr. 1946, reprinted by 512 Fd Survey Coy R.E. Dec 1946; '
      'M.D.R. 1509/12460. Map note: "This map must NOT be considered an authority on the delimitation of international boundaries". '
      'Scan: M00348_GreenLineEnglish_0.jpg (2891x8000 px, holding institution to be completed), uploaded by the researcher 2026-11-24. '
      'Georeferenced 2026-11-24 on 557 auto-detected Palestine-grid (EPSG:28191) 10 km intersections, poly-3 RMS 1.75 px (~100 m), '
      'thin-plate spline to ITM (EPSG:2039), 40 m. Check: 1994 border and Gulf of Aqaba shore coincide within a few hundred metres. '
      'PhD research of Shimon Frish, Technion (supervisors Prof. Maxim Shoshany, Prof. Aviad Shapira). All rights reserved.')
KW = ['1949', 'armistice', 'Green Line', 'Rhodes', 'Survey of Palestine', '1:250,000', 'Israel-Jordan', 'Arava']
z = zipfile.ZipFile(M); qn = [n for n in z.namelist() if n.endswith('.qgs')][0]
r = etree.fromstring(z.read(qn)); extra = {n: z.read(n) for n in z.namelist() if n != qn}; z.close()
top = r.find('layer-tree-group'); pl = r.find('projectlayers')
grp = [g for g in top.iter('layer-tree-group') if g.get('name') == 'מפות הסכמים וקווי גבול (רסטר)'][0]
old = {l.get('id') for l in r.iter('layer-tree-layer') if 'Armistice_Map_1949' in l.get('source', '')}
for l in list(r.iter('layer-tree-layer')):
    if l.get('id') in old: l.getparent().remove(l)
for m in list(pl):
    if m.find('id').text in old: pl.remove(m)
for e in list(r.iter('item')) + list(r.iter('layer')):
    if (e.text in old) or (e.get('id') in old): e.getparent().remove(e)
tl_tpl = [l for l in grp.findall('layer-tree-layer') if 'South_sheet_1942' in l.get('source', '')][0]
ml_tpl = [m for m in pl if m.find('id').text == tl_tpl.get('id')][0]
srs_tpl = [m for m in pl if (m.findtext('.//srs/spatialrefsys/authid') == 'EPSG:2039' and m.get('type') == 'raster')][0].find('srs')
lid = 'ARM49_' + uuid.uuid4().hex[:12]
m = copy.deepcopy(ml_tpl); m.find('id').text = lid; m.find('datasource').text = SRC; m.find('layername').text = NAME
m.replace(m.find('srs'), copy.deepcopy(srs_tpl))
for tag, v in (('extent', EXT['ext']), ('wgs84extent', EXT['wgs'])):
    e = m.find(tag)
    if e is not None:
        for k, x in zip(('xmin', 'ymin', 'xmax', 'ymax'), v): e.find(k).text = repr(float(x))
rm = m.find('resourceMetadata')
if rm is not None:
    for t, v in (('title', NAME), ('abstract', AB), ('type', 'dataset')):
        el = rm.find(t)
        if el is None: el = etree.SubElement(rm, t)
        el.text = v
    for k in rm.findall('keywords'): rm.remove(k)
    kw = etree.SubElement(rm, 'keywords', vocabulary='gmd:topicCategory')
    for k in KW: etree.SubElement(kw, 'keyword').text = k
kl = m.find('keywordList')
if kl is not None:
    for c in list(kl): kl.remove(c)
    for k in KW: etree.SubElement(kl, 'value').text = k
# raster renderer: RGB bands 1-3, no alpha band (internal mask)
rr = m.find('.//rasterrenderer')
if rr is not None:
    rr.set('type', 'multibandcolor'); rr.set('redBand', '1'); rr.set('greenBand', '2'); rr.set('blueBand', '3'); rr.set('alphaBand', '-1')
pl.append(m)
tl = copy.deepcopy(tl_tpl)
for c in list(tl): tl.remove(c)
tl.set('id', lid); tl.set('source', SRC); tl.set('name', NAME); tl.set('checked', 'Qt::Unchecked')
grp.insert(0, tl)
co = top.find('custom-order')
if co is not None: etree.SubElement(co, 'item').text = lid
for lo in r.iter('layerorder'): etree.SubElement(lo, 'layer', id=lid)
with zipfile.ZipFile(M, 'w', zipfile.ZIP_DEFLATED) as zo:
    zo.writestr(qn, etree.tostring(r, encoding='utf-8', xml_declaration=True))
    for k, v in extra.items(): zo.writestr(k, v)
print('ok', NAME, '->', grp.get('name'), [c.get('name')[:30] for c in grp if c.tag == 'layer-tree-layer'][:4])
