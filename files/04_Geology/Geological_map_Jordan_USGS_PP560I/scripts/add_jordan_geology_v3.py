# Jordan geology group in MASTER (4.3): NRA 1:50k Gharandal + Bender 1968 1:250k (Aqaba-Ma'an, Amman) + Kempf 2023 vector (CC-BY)
import zipfile, os, sys, copy, shutil, datetime, uuid, sqlite3, colorsys
from lxml import etree
ROOT=sys.argv[1]; M=os.path.join(ROOT,'Israel_Jordan_Arava_MASTER.qgz')
stamp=datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
shutil.copy2(M,os.path.join(ROOT,'99_Archive','qgz_backups',f'Israel_Jordan_Arava_MASTER_BEFORE_jordan_geology_v3_{stamp}.qgz'))
GN='מפות גאולוגיות ירדניות (NRA, Bender, USGS, Kempf)'
NRA='./04_Geology/Geological_maps_Jordan_NRA/'; BEN='./04_Geology/Geological_maps_Jordan_Bender1968/'; KEM='./04_Geology/Geological_map_Jordan_Kempf2023_CCBY/'; USG='./04_Geology/Geological_map_Jordan_USGS_PP560I/'
R=[dict(file=NRA+'NRA50k_3050III_Wadi_Gharandal_1988_ITM.tif',name='ירדן 1:50,000 – ואדי גרנדל 3050 III (NRA 1988)',on=True,
   ext=(199704.136,434450.964,223829.136,462185.964),wgs=(34.99921,29.99871,35.24987,30.24906),
   abstract='Wadi Gharandal 3050 III, Geological Map 1:50,000, NRA Jordan, 1988 (printed 1990). K.M. Ibrahim & M. Rashdan. Source: https://www.researchgate.net/publication/270050943. Georef ED50 neatline corners, <50 m. Copyright NRA/MEMR – not for public web.'),
 dict(file=BEN+'Bender1968_250k_Aqaba-Maan_ITM.tif',name="ירדן 1:250,000 – Bender 1968, גיליון עקבה–מעאן",on=True,
   ext=(174262.3,341816.0,333662.3,547291.0),wgs=(34.73116,29.15802,36.40035,31.0167),
   abstract="Geologische Karte von Jordanien / Geological Map of Jordan 1:250,000, sheet Aqaba-Ma'an. Bundesanstalt fuer Bodenforschung, Hannover (German Geological Mission in Jordan, F. Bender et al.), 1968. Scan: National Library of Australia nla.obj-2518025444. Georef from Palestine Grid ticks (EPSG:28193), est. 100-300 m. In copyright until 2038 – not for public web."),
 dict(file=BEN+'Bender1968_250k_Amman_ITM.tif',name='ירדן 1:250,000 – Bender 1968, גיליון עמאן',on=True,
   ext=(174885.3,545653.0,333260.3,749778.0),wgs=(34.72836,30.99643,36.41992,32.84277),
   abstract='Geologische Karte von Jordanien / Geological Map of Jordan 1:250,000, sheet Amman. Bundesanstalt fuer Bodenforschung, Hannover, 1968. Scan: National Library of Australia nla.obj-2518025384. Georef from Palestine Grid ticks, est. 100-300 m. In copyright until 2038 – not for public web.'),
 dict(file=USG+'USGS_PP560I_Plate1_Bender_Geologic_Map_of_Jordan_500k_ITM.tif',name='ירדן 1:500,000 – Bender, USGS PP 560-I לוח 1 (כל ירדן)',on=False,
   ext=(175200.0,342050.0,613200.0,829900.0),wgs=(34.75,29.16667,39.25,33.5),
   abstract='Geologic Map of Jordan 1:500,000, by Friedrich Bender. U.S. Geological Survey Professional Paper 560-I, Plate 1 (1975), with Government of Jordan and Geological Survey of the Fed. Rep. of Germany. Scan: USGS pubs (PP_560-I_plate_1, supplied by Shimi 2026-11-17). Georef: 243 graticule intersections (15 min), Lambert conformal (17/33) + affine + cubic correction, ED50 -> ITM, RMS ~85 m; vs 1994 border ~0.5-1 km (cartographic generalisation). US Government work - public domain.')]
V=dict(file=KEM+'Jordan_geology_Kempf2023_ITM.gpkg',layer='geology_units_jordan',name='ירדן – מפה גאולוגית דיגיטלית (Kempf 2023, וקטור, CC-BY)',on=False,
   ext=(186068.8,374061.9,425078.7,740439.1),wgs=(34.84815,29.43722,37.39803,32.75856),
   abstract='Digital Geological Map of Jordan. M. Kempf (University of Basel), Zenodo 2023, doi:10.5281/zenodo.10061800, licence CC-BY 4.0. Digitised from F. Bender, Geologic Map of Jordan, USGS Professional Paper 560-I Plate 1 (1975); legend: geological_map_print.pdf. Reprojected EPSG:3857 -> ITM. Accuracy ~0.5-1 km.')
codes=[c for (c,) in sqlite3.connect(os.path.join(ROOT,V['file'][2:])).execute('select distinct unit_code from geology_units_jordan order by unit_code')]
HUE={'Q':(0.15,0.55),'T':(0.09,0.6),'K':(0.30,0.5),'J':(0.58,0.5),'TR':(0.80,0.4),'S':(0.45,0.4),'O':(0.40,0.45),'C':(0.05,0.55),'p':(0.98,0.6)}
def col(c):
    k='TR' if c.upper().startswith('TR') else ('p' if c.startswith('p') else c[:1].upper())
    h,s=HUE.get(k,(0,0)); n=sum(ord(x) for x in c)%5
    rr,gg,bb=colorsys.hls_to_rgb(h,0.55+0.07*(n-2),s); return f'{int(rr*255)},{int(gg*255)},{int(bb*255)},255'
def renderer():
    cats=''.join(f'<category render="true" value="{c}" symbol="{i}" label="{c}" type="string"/>' for i,c in enumerate(codes))
    syms=''.join(f'<symbol name="{i}" type="fill" alpha="0.85" clip_to_extent="1" force_rhr="0"><layer class="SimpleFill" enabled="1" pass="0" locked="0"><Option type="Map"><Option name="color" value="{col(c)}" type="QString"/><Option name="outline_color" value="90,90,90,255" type="QString"/><Option name="outline_width" value="0.1" type="QString"/><Option name="outline_style" value="solid" type="QString"/><Option name="style" value="solid" type="QString"/></Option></layer></symbol>' for i,c in enumerate(codes))
    return etree.fromstring(f'<renderer-v2 type="categorizedSymbol" attr="unit_code" symbollevels="0" forceraster="0" enableorderby="0" referencescale="-1"><categories>{cats}</categories><symbols>{syms}</symbols><rotation/><sizescale/></renderer-v2>')
z=zipfile.ZipFile(M); qn=[n for n in z.namelist() if n.endswith('.qgs')][0]
r=etree.fromstring(z.read(qn)); extra={n:z.read(n) for n in z.namelist() if n!=qn}; z.close()
top=r.find('layer-tree-group'); pl=r.find('projectlayers')
geo=[g for g in top.iter('layer-tree-group') if (g.get('name') or '').startswith('3.3')][0]
gsi=[g for g in geo if g.tag=='layer-tree-group' and g.get('name')=='מפות גאולוגיות (מצפון לדרום)'][0]
gvec=[g for g in geo if g.tag=='layer-tree-group' and g.get('name')=='שכבות וקטור – המכון הגאולוגי'][0]
# remove previous Jordan groups/layers
old=[g for g in geo if g.tag=='layer-tree-group' and ('ירדני' in (g.get('name') or ''))]
oldids={l.get('id') for g in old for l in g.iter('layer-tree-layer')}
for g in old: geo.remove(g)
for m in list(pl):
    if m.find('id').text in oldids: pl.remove(m)
for e in list(r.iter('item'))+list(r.iter('layer')):
    if (e.text in oldids) or (e.get('id') in oldids): e.getparent().remove(e)
grp=copy.deepcopy(gsi); grp.set('name',GN)
for c in list(grp):
    if c.tag in ('layer-tree-layer','layer-tree-group'): grp.remove(c)
geo.insert(list(geo).index(gsi)+1,grp)
def add(tl_tpl,ml_tpl,s,src,provider=None,vector=False):
    lid='JOR_'+uuid.uuid4().hex[:12]
    m=copy.deepcopy(ml_tpl); m.find('id').text=lid; m.find('datasource').text=src; m.find('layername').text=s['name']
    for tag,v in (('extent',s['ext']),('wgs84extent',s['wgs'])):
        e=m.find(tag)
        if e is None:
            e=etree.Element(tag); m.insert(0,e)
            for k in ('xmin','ymin','xmax','ymax'): etree.SubElement(e,k)
        for k,x in zip(('xmin','ymin','xmax','ymax'),v): e.find(k).text=repr(float(x))
    rm=m.find('resourceMetadata')
    if rm is not None: rm.find('title').text=s['name']; rm.find('abstract').text=s['abstract']
    if vector:
        m.replace(m.find('renderer-v2'),renderer())
        for lab in m.findall('labeling'): m.remove(lab)
        if m.find('provider') is not None: m.find('provider').text='ogr'
        m.replace(m.find('srs'),copy.deepcopy(rml.find('srs')))
        if m.get('wkbType'): m.set('wkbType','MultiPolygon')
    else:
        pipe=m.find('pipe'); pipe.replace(pipe.find('rasterrenderer'),etree.fromstring('<rasterrenderer type="multibandcolor" redBand="1" greenBand="2" blueBand="3" alphaBand="-1" opacity="1" nodataColor=""><rasterTransparency/><minMaxOrigin><limits>None</limits><extent>WholeRaster</extent><statAccuracy>Estimated</statAccuracy><cumulativeCutLower>0.02</cumulativeCutLower><cumulativeCutUpper>0.98</cumulativeCutUpper><stdDevFactor>2</stdDevFactor></minMaxOrigin></rasterrenderer>'))
    pl.append(m)
    tl=copy.deepcopy(tl_tpl)
    for c in list(tl): tl.remove(c)
    tl.set('id',lid); tl.set('source',src); tl.set('name',s['name']); tl.set('checked','Qt::Checked' if s['on'] else 'Qt::Unchecked')
    grp.append(tl)
    co=top.find('custom-order')
    if co is not None: etree.SubElement(co,'item').text=lid
    for lo in r.iter('layerorder'): etree.SubElement(lo,'layer',id=lid)
rtl=list(gsi.iter('layer-tree-layer'))[0]; rml=[m for m in r.iter('maplayer') if m.find('id').text==rtl.get('id')][0]
for s in R: add(rtl,rml,s,s['file'])
vtl=[l for l in gvec.iter('layer-tree-layer') if 'formations' in l.get('source')][0]; vml=[m for m in r.iter('maplayer') if m.find('id').text==vtl.get('id')][0]
add(vtl,vml,V,V['file']+'|layername='+V['layer'],vector=True)
with zipfile.ZipFile(M,'w',zipfile.ZIP_DEFLATED) as zo:
    zo.writestr(qn,etree.tostring(r,encoding='utf-8',xml_declaration=True))
    for k,v in extra.items(): zo.writestr(k,v)
print('group',GN,'layers',len(grp),'codes',len(codes))
