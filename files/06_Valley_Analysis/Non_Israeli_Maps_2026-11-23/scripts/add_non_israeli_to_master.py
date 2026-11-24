# Adds the non-Israeli maps of the Arava (2026-11-23/24) to Israel_Jordan_Arava_MASTER.qgz
#  - 2.3 "השוואה לתיחומי העמק במקורות לא-ישראליים": 6 vector delineations (all off)
#  - 3.4 > "מפות לא-ישראליות של הערבה (עבר הירדן, ירדן, ארה"ב)": 6 georeferenced rasters (all off)
# usage: python3 add_non_israeli_to_master.py <ROOT> <master_extents.json>   (re-runnable)
import zipfile, os, sys, copy, shutil, datetime, uuid, json
from lxml import etree
ROOT = sys.argv[1]; M = os.path.join(ROOT, 'Israel_Jordan_Arava_MASTER.qgz')
EXT = json.load(open(sys.argv[2]))
stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
shutil.copy2(M, os.path.join(ROOT, '99_Archive', 'qgz_backups', f'Israel_Jordan_Arava_MASTER_BEFORE_non_israeli_maps_{stamp}.qgz'))
P = './06_Valley_Analysis/Non_Israeli_Maps_2026-11-23/'
G_V = '2.3 השוואה לתיחומי העמק במקורות לא-ישראליים'
G_R = 'מפות לא-ישראליות של הערבה (עבר הירדן, ירדן, ארה"ב)'
TAG = 'NIM_'

RASTERS = [
 ('Jordan_Tourist_1962_UTM36.tif', 'מפת התיירות של ירדן 1:750,000 – מחלקת הקרקעות והמדידות (1962, הדפסה 1979)',
  'Hashemite Kingdom of Jordan Tourist Map 1:750,000, compiled and drawn by Dept. of Lands and Surveys for the Tourism Authority, 1962; Ministry of Tourism & Antiquities print May 1979. IRCICA Library H-791. Georeferenced on 9 graticule nodes, RMS 90 m (towns 1-2 km).'),
 ('AMS_K502_Aqaba_1961_UTM36.tif', 'AMS K502 1:250,000 – גיליון עקבה NH 36-12 (1961)',
  'U.S. Army Map Service Series K502, sheet NH 36-12 Aqaba, Edition 3-AMS 1961. Public domain, PCL UT Austin. Georeferenced on printed UTM grid nodes (ED50), RMS 17-35 m.'),
 ('AMS_K502_Maan_1961_UTM36.tif', 'AMS K502 1:250,000 – גיליון מען NH 36-8 (1961)',
  'U.S. Army Map Service Series K502, sheet NH 36-8 Ma\'an, Edition 3-AMS 1961. Public domain, PCL UT Austin. Georeferenced on printed UTM grid nodes (ED50), RMS 17-35 m.'),
 ('AMS_K502_Jerusalem_1961_UTM36.tif', 'AMS K502 1:250,000 – גיליון ירושלים NH 36-4 (1961)',
  'U.S. Army Map Service Series K502, sheet NH 36-4 Jerusalem, Edition 3-AMS 1961. Public domain, PCL UT Austin. Georeferenced on printed UTM grid nodes (ED50), RMS 17-35 m.'),
 ('K737_3049III_Aqaba_1960_UTM36.tif', 'מפת ירדן 1:50,000 – K737 גיליון 3049 III עקבה (1960)',
  'U.S. Army Map Service Series K737, Jordan 1:50,000, sheet 3049 III \'Aqaba, Edition 1-AMS 1960. Public domain, UC Berkeley digicoll 222014. 700 UTM 1 km nodes, RMS 12 m.'),
 ('TransJordan_250k_Kerak_1941_UTM36.tif', 'מפת עבר הירדן 1:250,000 – גיליון כרך (1941)',
  'Trans-Jordan 1:250,000, sheet Kerak, Department of Lands & Surveys Trans-Jordan, edition June 1941. National Library of Australia nla.obj-233522746 (out of copyright). 144 Palestine-grid nodes, RMS 23 m.'),
]
# (gpkg, layer, name, abstract, kind, colour, style)
VECTORS = [
 ('JVA_law_zone_vs_valley.gpkg', 'jva_law_zone_500m', '"העמק" בחוק פיתוח עמק הירדן הירדני – אזור 2 (עד קו 500 מ\')',
  'Jordan Valley Development Law 1988 (Law 30/2001) art 2(c) area 2: from N Dead Sea to S boundary of Qatar village, W = frontier, E = 500 m a.s.l. contour (Copernicus GLO-30).', 'poly', '230,130,20', 'outline'),
 ('Atlas_of_Jordan_2013_depression_unit.gpkg', 'depression_unit_digitised', 'יחידת השקע – Atlas of Jordan 2013 (אל-בילביסי, איור I.2)',
  'Al-Bilbisi 2013, Atlas of Jordan (Ifpo) fig I.2 depression unit, red boundary lines digitised. Georef on 13 towns, RMS ~1 km. Figure (c) Ifpo - research use only.', 'poly', '200,30,30', 'outline'),
 ('Non_Israeli_maps_valley_delineations.gpkg', 'K737_3049III_valley_floor_mapped', 'משטח העמק לפי מפת ירדן 1:50,000 עקבה (K737, 1960)',
  'Valley floor incl. "wadi spread" fans up to the mountain foot, extracted from brown-ink fraction (<30% in 310 m window, 250 m opening) on K737 sheet 3049 III.', 'poly', '30,100,220', 'fill'),
 ('Non_Israeli_maps_valley_delineations.gpkg', 'AMS_K502_east_mountain_front', 'חזית ההר המזרחית לפי AMS K502 1:250,000 (1961)',
  'First 1.5 km of continuous dense contours east of border+800 m, 3 km running median.', 'line', '20,90,200', 'dash'),
 ('Non_Israeli_maps_valley_delineations.gpkg', 'Tourist1962_first_contour_south', 'קו הגובה הראשון במפת התיירות של ירדן 1962 (עקבה–ע\'רנדל)',
  'First (orange) contour east of border+800 m on DLS tourist map 1962, rows every 250 m, 3 km running median, Aqaba-Gharandal only (north unreliable).', 'line', '230,120,0', 'dash'),
 ('Non_Israeli_maps_valley_delineations.gpkg', 'Powell2015_fig2a_mountain_foot', 'רגל ההר לפי מחשופי סלע היסוד – Powell ועמיתיו 2015 (לפי NRA)',
  'West edge of basement outcrops, Powell, Abed & Jarrar 2015 GeoArabia 20(1) fig 2a (after McCourt & Ibrahim 1990, NRA).', 'line', '150,60,20', 'solid'),
]

def rend_line(col, style):
    ls = {'dash': 'dash', 'solid': 'solid'}[style]
    return etree.fromstring(f'<renderer-v2 type="singleSymbol" symbollevels="0" forceraster="0" enableorderby="0" referencescale="-1"><symbols><symbol name="0" type="line" alpha="1" clip_to_extent="1" force_rhr="0"><layer class="SimpleLine" enabled="1" pass="0" locked="0"><Option type="Map"><Option name="line_color" value="{col},255" type="QString"/><Option name="line_width" value="0.9" type="QString"/><Option name="line_width_unit" value="MM" type="QString"/><Option name="line_style" value="{ls}" type="QString"/><Option name="capstyle" value="round" type="QString"/><Option name="joinstyle" value="round" type="QString"/></Option></layer></symbol></symbols><rotation/><sizescale/></renderer-v2>')

def rend_poly(col, style):
    fill = 'solid' if style == 'fill' else 'no'
    return etree.fromstring(f'<renderer-v2 type="singleSymbol" symbollevels="0" forceraster="0" enableorderby="0" referencescale="-1"><symbols><symbol name="0" type="fill" alpha="0.45" clip_to_extent="1" force_rhr="0"><layer class="SimpleFill" enabled="1" pass="0" locked="0"><Option type="Map"><Option name="color" value="{col},255" type="QString"/><Option name="outline_color" value="{col},255" type="QString"/><Option name="outline_width" value="0.6" type="QString"/><Option name="style" value="{fill}" type="QString"/><Option name="outline_style" value="solid" type="QString"/></Option></layer></symbol></symbols><rotation/><sizescale/></renderer-v2>')

z = zipfile.ZipFile(M); qn = [n for n in z.namelist() if n.endswith('.qgs')][0]
r = etree.fromstring(z.read(qn)); extra = {n: z.read(n) for n in z.namelist() if n != qn}; z.close()
top = r.find('layer-tree-group'); pl = r.find('projectlayers')
g2 = [g for g in top.findall('layer-tree-group') if (g.get('name') or '').startswith('2.')][0]
hist = [g for g in top.iter('layer-tree-group') if (g.get('name') or '').startswith('3.4')][0]

# remove a previous run
old = set()
for parent, name in ((g2, G_V), (hist, G_R)):
    for g in list(parent):
        if g.tag == 'layer-tree-group' and g.get('name') == name:
            old |= {l.get('id') for l in g.iter('layer-tree-layer')}; parent.remove(g)
for m in list(pl):
    if m.find('id').text in old: pl.remove(m)
for e in list(r.iter('item')) + list(r.iter('layer')):
    if (e.text in old) or (e.get('id') in old): e.getparent().remove(e)

def tl_ml(pred):
    tl = [l for l in r.iter('layer-tree-layer') if pred(l.get('source', ''))][0]
    ml = [m for m in pl if m.find('id').text == tl.get('id')][0]
    return tl, ml
rtl, rml = tl_ml(lambda s: 'Sinai_Wadi_el_Jeib_1915' in s)
ptl, pml = tl_ml(lambda s: 'valley_polygon_auto_rule' in s)
ltl, lml = tl_ml(lambda s: 'layername=thalweg_line' in s)
srs32636 = pml.find('srs')

def new_group(parent, tpl_group, name, pos):
    g = copy.deepcopy(tpl_group); g.set('name', name); g.set('checked', 'Qt::Checked'); g.set('expanded', '1')
    for c in list(g):
        if c.tag in ('layer-tree-layer', 'layer-tree-group'): g.remove(c)
    parent.insert(pos, g); return g

sub21 = [g for g in g2.findall('layer-tree-group')]
gv = new_group(g2, sub21[0], G_V, list(g2).index(sub21[-1]) + 1)
hsub = [g for g in hist.findall('layer-tree-group')]
gr = new_group(hist, hsub[0], G_R, list(hist).index(hsub[-1]) + 1)

def add(group, tl_tpl, ml_tpl, name, src, key, ab, kind=None, col=None, style=None):
    lid = TAG + uuid.uuid4().hex[:12]
    m = copy.deepcopy(ml_tpl); m.find('id').text = lid; m.find('datasource').text = src; m.find('layername').text = name
    m.replace(m.find('srs'), copy.deepcopy(srs32636))
    for tag, v in (('extent', EXT[key]['ext']), ('wgs84extent', EXT[key]['wgs'])):
        e = m.find(tag)
        if e is not None:
            for k, x in zip(('xmin', 'ymin', 'xmax', 'ymax'), v): e.find(k).text = repr(float(x))
    rm = m.find('resourceMetadata')
    if rm is not None:
        if rm.find('title') is not None: rm.find('title').text = name
        if rm.find('abstract') is not None: rm.find('abstract').text = ab
    if kind:
        new = rend_line(col, style) if kind == 'line' else rend_poly(col, style)
        old_r = m.find('renderer-v2')
        if old_r is not None: m.replace(old_r, new)
        else: m.append(new)
        for lab in m.findall('labeling'): m.remove(lab)
        m.set('labelsEnabled', '0')
        if kind == 'poly': m.set('geometry', 'Polygon'); m.set('wkbType', 'MultiPolygon' if 'K737' in src or 'Atlas' in src else 'Polygon')
        else: m.set('geometry', 'Line'); m.set('wkbType', 'MultiLineString' if 'Tourist' in src else 'LineString')
    pl.append(m)
    tl = copy.deepcopy(tl_tpl)
    for c in list(tl): tl.remove(c)
    tl.set('id', lid); tl.set('source', src); tl.set('name', name); tl.set('checked', 'Qt::Unchecked')
    group.append(tl)
    co = top.find('custom-order')
    if co is not None: etree.SubElement(co, 'item').text = lid
    for lo in r.iter('layerorder'): etree.SubElement(lo, 'layer', id=lid)

for f, l, name, ab, kind, col, style in VECTORS:
    tl, ml = (ptl, pml) if kind == 'poly' else (ltl, lml)
    add(gv, tl, ml, name, P + f + '|layername=' + l, f + '|' + l, ab, kind, col, style)
for f, name, ab in RASTERS:
    add(gr, rtl, rml, name, P + 'georef/' + f, f, ab)

with zipfile.ZipFile(M, 'w', zipfile.ZIP_DEFLATED) as zo:
    zo.writestr(qn, etree.tostring(r, encoding='utf-8', xml_declaration=True))
    for k, v in extra.items(): zo.writestr(k, v)
print('ok', G_V, len(gv.findall('layer-tree-layer')), '|', G_R, len(gr.findall('layer-tree-layer')))
