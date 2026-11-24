# Adds the four early British maps (1914-1916) + derived vectors to MASTER.
# 3.4 > new group "מפות בריטיות מוקדמות 1914–1916"; 1.3 > Ottoman provincial boundary 1916.
import zipfile, os, sys, copy, shutil, datetime, uuid, json
from lxml import etree
ROOT=sys.argv[1]; M=os.path.join(ROOT,'Israel_Jordan_Arava_MASTER.qgz')
EXT=json.load(open(sys.argv[2]))
stamp=datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
shutil.copy2(M,os.path.join(ROOT,'99_Archive','qgz_backups',f'Israel_Jordan_Arava_MASTER_BEFORE_british_early_{stamp}.qgz'))
P='./05_Historical_Maps/British_Early_1914-1916/'
GN='מפות בריטיות מוקדמות 1914–1916 (סיני וואדי ערבה)'
SRC='Scan: National Library of Israel (Eran Laor collection) via Wikimedia Commons. Georeferenced 2026-11-18 by thin-plate spline on printed graticule intersections, source datum Egypt 1907 (EPSG:4229) -> ITM. '
R=[dict(f='Sinai_Wadi_el_Jeib_1915_125k_ITM.tif',name='סיני 1:125,000 – ואדי אל-ג\'ייב (1914–1915)',
   ab=SRC+'Sinai Peninsula 1:125,000, sheet Wadi el Jeib, North H-36 L-I & part of II. GSGS 2230, Ordnance Survey Southampton 1914, printed War Office 1915. Survey under Capt. S.F. Newcombe; hills east of ~35°28\' from Kitchener 1883 (unreliable). 35 graticule GCPs, fit RMS 13 px (~70 m); absolute error vs modern 200-500 m west of 35°28\'.'),
 dict(f='Sinai_Gebel_Harun_1915_125k_ITM.tif',name='סיני 1:125,000 – ג\'בל הארון (1914–1915)',
   ab=SRC+'Sinai Peninsula 1:125,000, sheet Gebel Harun, North H-36 L-III & part of IV. GSGS 2230, OS Southampton 1914, War Office 1915. 30 GCPs, RMS 12 px (~60 m); Gebel Harun trig point 250 m from modern position.'),
 dict(f='Sinai_Akaba_Sheet4_1915_250k_ITM.tif',name='סיני 1:250,000 – גיליון 4 עקבה (1915)',
   ab=SRC+'Sinai Peninsula 1:250,000, sheet 4 Akaba. GSGS 2761, War Office March 1915. Shows 1906 Turco-Egyptian boundary (Rafah-Taba) with boundary pillars. 45 GCPs, RMS 4 px (~45 m); Aqaba fort ~600 m off.'),
 dict(f='Asia_1M_Cairo_H36_1916_ITM.tif',name='אסיה 1:1,000,000 – קהיר North H-36 (1916)',
   ab=SRC+'Asia 1:1,000,000, sheet Cairo North H-36, provisional edition. GSGS 2544, compiled RGS, War Office 1916. Shows international (1906) and Ottoman provincial boundaries (El Kuds / Suriya). Map note: region east of Gulf of Akaba and Wadi Araba unsurveyed. 15 GCPs (1° graticule), RMS 15 px (~0.6 km).')]
def tree_and_layer(r,pred):
    tl=[l for l in r.iter('layer-tree-layer') if pred(l)][0]
    ml=[m for m in r.iter('maplayer') if m.find('id').text==tl.get('id')][0]
    return tl,ml
z=zipfile.ZipFile(M); qn=[n for n in z.namelist() if n.endswith('.qgs')][0]
r=etree.fromstring(z.read(qn)); extra={n:z.read(n) for n in z.namelist() if n!=qn}; z.close()
top=r.find('layer-tree-group'); pl=r.find('projectlayers')
hist=[g for g in top.iter('layer-tree-group') if (g.get('name') or '').startswith('3.4')][0]
b13=[g for g in top.iter('layer-tree-group') if (g.get('name') or '').startswith('1.3')][0]
# remove previous run
oldids=set()
for g in list(hist):
    if g.tag=='layer-tree-group' and g.get('name')==GN:
        oldids|={l.get('id') for l in g.iter('layer-tree-layer')}; hist.remove(g)
for l in list(b13):
    if l.tag=='layer-tree-layer' and 'Ottoman_provincial_boundary_1916' in l.get('source',''): oldids.add(l.get('id')); b13.remove(l)
for m in list(pl):
    if m.find('id').text in oldids: pl.remove(m)
for e in list(r.iter('item'))+list(r.iter('layer')):
    if (e.text in oldids) or (e.get('id') in oldids): e.getparent().remove(e)
agr=[g for g in hist if g.tag=='layer-tree-group' and g.get('name')=='מפות הסכמים וקווי גבול (רסטר)'][0]
grp=copy.deepcopy(agr); grp.set('name',GN); grp.set('checked','Qt::Checked'); grp.set('expanded','1')
for c in list(grp):
    if c.tag in ('layer-tree-layer','layer-tree-group'): grp.remove(c)
hist.insert(list(hist).index(agr)+1,grp)
rtl,rml=tree_and_layer(r,lambda l:'South_sheet_1942' in l.get('source',''))
vtl,vml=tree_and_layer(r,lambda l:'Mandate_border_1942_digitized' in l.get('source',''))
def renderer_line():
    return etree.fromstring('<renderer-v2 type="singleSymbol" symbollevels="0" forceraster="0" enableorderby="0" referencescale="-1"><symbols><symbol name="0" type="line" alpha="1" clip_to_extent="1" force_rhr="0"><layer class="SimpleLine" enabled="1" pass="0" locked="0"><Option type="Map"><Option name="line_color" value="120,60,20,255" type="QString"/><Option name="line_width" value="0.8" type="QString"/><Option name="line_width_unit" value="MM" type="QString"/><Option name="line_style" value="dash dot" type="QString"/><Option name="capstyle" value="round" type="QString"/><Option name="joinstyle" value="round" type="QString"/></Option></layer></symbol></symbols><rotation/><sizescale/></renderer-v2>')
def renderer_poly():
    return etree.fromstring('<renderer-v2 type="singleSymbol" symbollevels="0" forceraster="0" enableorderby="0" referencescale="-1"><symbols><symbol name="0" type="fill" alpha="0.6" clip_to_extent="1" force_rhr="0"><layer class="SimpleFill" enabled="1" pass="0" locked="0"><Option type="Map"><Option name="color" value="230,120,170,255" type="QString"/><Option name="outline_color" value="170,40,110,255" type="QString"/><Option name="outline_width" value="0.3" type="QString"/><Option name="style" value="solid" type="QString"/><Option name="outline_style" value="solid" type="QString"/></Option></layer></symbol></symbols><rotation/><sizescale/></renderer-v2>')
def add(group,tl_tpl,ml_tpl,name,src,key,ab,on,vector=None,pos=None):
    lid='BRE_'+uuid.uuid4().hex[:12]
    m=copy.deepcopy(ml_tpl); m.find('id').text=lid; m.find('datasource').text=src; m.find('layername').text=name
    for tag,v in (('extent',EXT[key]['ext']),('wgs84extent',EXT[key]['wgs'])):
        e=m.find(tag)
        if e is not None:
            for k,x in zip(('xmin','ymin','xmax','ymax'),v): e.find(k).text=repr(float(x))
    rm=m.find('resourceMetadata')
    if rm is not None:
        if rm.find('title') is not None: rm.find('title').text=name
        if rm.find('abstract') is not None: rm.find('abstract').text=ab
    if vector:
        old=m.find('renderer-v2'); new=renderer_line() if vector=='line' else renderer_poly()
        if old is not None: m.replace(old,new)
        else: m.append(new)
        for lab in m.findall('labeling'): m.remove(lab)
        m.set('labelsEnabled','0')
        if vector=='poly': m.set('geometry','Polygon'); m.set('wkbType','MultiPolygon')
        else: m.set('geometry','Line'); m.set('wkbType','LineString')
    pl.append(m)
    tl=copy.deepcopy(tl_tpl)
    for c in list(tl): tl.remove(c)
    tl.set('id',lid); tl.set('source',src); tl.set('name',name); tl.set('checked','Qt::Checked' if on else 'Qt::Unchecked')
    if pos is None: group.append(tl)
    else: group.insert(pos,tl)
    co=top.find('custom-order')
    if co is not None: etree.SubElement(co,'item').text=lid
    for lo in r.iter('layerorder'): etree.SubElement(lo,'layer',id=lid)
add(grp,vtl,vml,'ערוצי נחל רחבים לפי מפות 1:125,000 (1915, חילוץ אוטומטי)',P+'Large_wadi_beds_1915_125k.gpkg|layername=Large_wadi_beds_1915_125k','Large_wadi_beds_1915_125k.gpkg',
    'Large wadi beds (pink stipple on the 1914-15 1:125k sheets), auto-extracted by colour, polygons >0.2 km2 inside sheet frames.',False,vector='poly')
for s in R: add(grp,rtl,rml,s['name'],P+s['f'],s['f'],s['ab'],False)
pos=list(b13).index(vtl)+1
add(b13,vtl,vml,'גבול מחוזי עות\'מאני ירושלים / סוריה (מפת 1:1,000,000, 1916)','./01_Borders/Ottoman_provincial_boundary_1916.gpkg|layername=Ottoman_provincial_boundary_1916','Ottoman_provincial_boundary_1916.gpkg',
    'Ottoman provincial boundary between the Mutasarriflik of El Kuds (Jerusalem) and the Vilayet of Suriya (Syria), digitised by hand from GSGS 2544 Asia 1:1M Cairo H-36 (1916). Accuracy +-1-2 km.',False,vector='line',pos=pos)
with zipfile.ZipFile(M,'w',zipfile.ZIP_DEFLATED) as zo:
    zo.writestr(qn,etree.tostring(r,encoding='utf-8',xml_declaration=True))
    for k,v in extra.items(): zo.writestr(k,v)
print('added group',GN,'layers',len([c for c in grp if c.tag=='layer-tree-layer']),'+ 1.3 Ottoman line')
