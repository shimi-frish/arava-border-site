# Adds the maps of the review "Israel-Jordan border in the Arava" (edited article after Amiram Oren 2023) to MASTER group 3.4,
# and tags the review maps that were already in MASTER with their figure number. Re-runnable.
# usage: python3 add_review_maps_to_master.py <ROOT>
import zipfile, os, sys, copy, shutil, datetime, uuid
from lxml import etree
ROOT=sys.argv[1]; M=os.path.join(ROOT,'Israel_Jordan_Arava_MASTER.qgz')
shutil.copy2(M,os.path.join(ROOT,'99_Archive','qgz_backups',f'Israel_Jordan_Arava_MASTER_BEFORE_review_oren_{datetime.datetime.now():%Y-%m-%d_%H%M}.qgz'))
D='./05_Historical_Maps/Review_Oren_2023/georef/'
CR=' PhD research of Shimon Frish, Technion (supervisors Prof. Maxim Shoshany, Prof. Aviad Shapira). All rights reserved.'
REV='Review "Israel-Jordan border in the Arava: from Mandate formation to a marked peace border" (edited article after Amiram Oren, "Amiram in Israel\'s paths", 12 Feb 2023)'
TAG='[REVIEW]'
# (file, layer name, group prefix, abstract)
NEW=[
 ('Benvenisti_Luria_1971_Negev_Arava_ITM.tif','מפת עזר ללימוד תנ"ך – בנבנשתי ולוריא 1971 (הערבה ללא גבול מסומן)','ישראליות (',
  'Bible study map of Eretz Israel for students, ed. David Benvenisti and Ben-Zion Luria (1971), Negev-Arava sheet. '+REV+', fig. 2, ch. 1: the Arava as a space with no marked border. Source: Amiram Oren map collection. Georeferenced on 8 graticule intersections (30-31N, 34.5-35.5E), affine, RMS 250 m.'),
 ('Bigger_military_zones_after_WWI_ITM.tif','שרטוט תחומי השליטה הצבאיים לאחר מלחמת העולם הראשונה (ביגר)','בריטיות ועות',
  'Sketch of the military administration zones after WWI (OETA South), courtesy Prof. Gideon Biger. '+REV+', fig. 4, ch. 2. Image taken from the review PDF (low resolution). Georeferenced on 6 places, affine, RMS 3.4 km (hand sketch).'),
 ('Mandate_borders_southern_Palestine_2M_ITM.tif','גבולות עם עבר הירדן בערבה בתקופת המנדט (Map Illustrating Jewish Property, 1:2,000,000)','בריטיות ועות',
  '"Map illustrating Jewish property - Southern Palestine", 1:2,000,000, Mandate period; red line = Mandated territory boundary with Trans-Jordan along Wadi Araba. '+REV+', fig. 5, ch. 2. Georeferenced on 7 points, affine, RMS 2.9 km (1.5 mm at map scale).'),
 ('TransJordan_250k_Maan_1939_Arava_ITM.tif','עבר הירדן 1:250,000 – גיליון מעאן 1939, קטע הערבה (פארן–יהל)','בריטיות (',
  'Trans-Jordan 1:250,000 (Ma\'an sheet), printed 1939 by the Survey of Palestine, Arava section between about Ein Yahav and Yahel, with the boundary line (orange band). Courtesy Avi Nabon. '+REV+', fig. 6, ch. 3 (caption there: north Arava valley). Georeferenced on 7 Palestine-grid intersections, affine, RMS 115 m.'),
 ('Boundary_marking_Gulf_of_Aqaba_1946_ITM.tif','סימון קו הגבול עם עבר הירדן בראש מפרץ עקבה – 1946 (1:50,000, חתום)','בריטיות ועות',
  'Map showing boundary between Palestine and Trans-Jordan at the Gulf of Aqaba, 1:50,000, 1946, signed; pillars 1-5 from the shore northward, Umm Rashrash police post, Aqaba. '+REV+', fig. 7, ch. 3. Georeferenced by similarity on pillar 1 (1994 border at the shore), Aqaba fort and Umm Rashrash (ink-flag site): residuals 70-160 m.'),
 ('UN_Partition_Plan_1947_ITM.tif','תוכנית החלוקה של האו"ם – 29 בנובמבר 1947','בינלאומיות',
  'UN Palestine Plan of Partition with Economic Union (UN map no. 103.1, 1956 printing). The southern Negev and the head of the Gulf of Aqaba are in the Jewish State. '+REV+', fig. 8, ch. 4. Low resolution; georeferenced by similarity on Jerusalem, Gulf head and Rafah coast, errors 2-4 km.'),
 ('Operation_Uvda_Golani_1949_ITM.tif','התקדמות חטיבת גולני בערבה – מבצע עובדה, מרץ 1949','ישראליות (',
  'Advance of the Golani brigade along the Arava in Operation Uvda (March 1949): Kurnub - Ein Husub - Ein Weiba - Ghamr - Ein Radian - Umm Rashrash. From the book "Ilan and Shelah - the battle path of the Golani brigade". '+REV+', fig. 9, ch. 4. Note: the source file name says Operation Horev; the review identifies it as Operation Uvda. Georeferenced on 8 places, 2nd-order polynomial, RMS 1.7 km (sketch).'),
 ('Border_map_1973_ITM.tif','קו הגבול על פי מפה משנת 1973','ישראליות –',
  'The Israel-Jordan line in the Arava on a 1973 map (about 1:750,000). Source: Amiram Oren map collection. '+REV+', fig. 12, ch. 6. Georeferenced on 6 points, affine, RMS 1.0 km.'),
 ('Zofar_enclave_1994-2020_ITM.tif','מובלעת צופר – שטח ירדני בשימוש ישראלי (1994–2020)','ישראליות –',
  'Zofar enclave: Jordanian territory with Israeli agricultural use under the 1994 treaty, until 2020 (black dashed outline east of the border). '+REV+', fig. 13, ch. 7. Georeferenced from the existing world file (EPSG:3857); fits the 1994 border within about 50 m.'),
 ('Border_Zofar_Paran_after_1994_ITM.tif','הגבול הבין-לאומי באזור צופר ופארן לאחר הסכם השלום','ישראליות –',
  'International border in the Zofar - Paran area after the 1994 peace treaty, Survey of Israel base map. '+REV+', fig. 16, ch. 8. Georeferenced from the existing world file (EPSG:3857); fits the 1994 border within about 100 m.'),
]
# existing MASTER layers that appear in the review: source key -> (fig note, optional new name)
OLD={
 'וויאלת חג_אז בשנת 1884':('fig. 3, ch. 1 (Ottoman provincial borders 1884, courtesy Prof. Yuval Ben-Bassat).',None),
 'קווי שביתת הנשק 1950,_georef':('fig. 10, ch. 4-5 (Armistice lines 1950, Amiram Oren map collection).',None),
 'קווי הפסקת האש 1967_georef_ITM':('fig. 11, ch. 6 (Ceasefire lines June 1967, Amiram Oren map collection).',None),
 'הגבול באיזור עידן עין יהב_modified':('cover figure (the Arava border segment of the planned tour, Neot HaKikar to Rekhes Menuha) and fig. 15, ch. 8 (international border at Idan and Ein Yahav after the 1994 treaty).',None),
 'מאמר ביגר ושטנר':('fig. 14, ch. 8 (border near Idan before and after the peace treaty, from D. Steiner and G. Biger, "Lahav ha-mahresha kava et ha-gvul").',None),
 'חורף 2023_georef':('fig. 17, summary (settlement map along the border, Kikar Sdom and middle Arava, winter 2023, with founding years).',None),
}
z=zipfile.ZipFile(M); qn=[n for n in z.namelist() if n.endswith('.qgs')][0]
r=etree.fromstring(z.read(qn)); extra={n:z.read(n) for n in z.namelist() if n!=qn}; z.close()
top=r.find('layer-tree-group'); pl=r.find('projectlayers')
old={l.get('id') for l in r.iter('layer-tree-layer') if 'Review_Oren_2023' in l.get('source','')}
for l in list(r.iter('layer-tree-layer')):
    if l.get('id') in old: l.getparent().remove(l)
for m in list(pl):
    if m.find('id').text in old: pl.remove(m)
for e in list(r.iter('item'))+list(r.iter('layer')):
    if (e.text in old) or (e.get('id') in old): e.getparent().remove(e)
g341=[g for g in top.iter('layer-tree-group') if g.get('name','').startswith('3.4.1')][0]
def grp(prefix):
    if prefix=='בינלאומיות':
        c=[g for g in g341 if g.tag=='layer-tree-group' and g.get('name','').startswith('בינלאומיות')]
        if c: return c[0]
        ng=copy.deepcopy([g for g in g341 if g.tag=='layer-tree-group'][0])
        for ch in list(ng):
            if ch.tag in('layer-tree-layer','layer-tree-group'): ng.remove(ch)
        ng.set('name','בינלאומיות – החלטת החלוקה של האו"ם (1947)'); ng.set('checked','Qt::Unchecked'); ng.set('expanded','0')
        g341.append(ng); return ng
    return [g for g in top.iter('layer-tree-group') if g.get('name','').startswith(prefix)][0]
tl_tpl=[l for l in top.iter('layer-tree-layer') if 'Armistice_Map_1949_Palestine_250k_ITM.tif' in l.get('source','')][0]
ml_tpl=[m for m in pl if m.find('id').text==tl_tpl.get('id')][0]
BOUNDS={"Benvenisti_Luria_1971_Negev_Arava_ITM.tif": [[109618.9, 379880.8, 272157.7, 588543.7], [34.07173, 29.50175, 35.75851, 31.38757]], "Bigger_military_zones_after_WWI_ITM.tif": [[37818.9, 355412.3, 339500.1, 826151.5], [33.33559, 29.27276, 36.49662, 33.52464]], "Border_Zofar_Paran_after_1994_ITM.tif": [[200736.6, 460286.2, 230113.8, 485661.8], [35.00997, 30.23177, 35.31541, 30.46077]], "Border_map_1973_ITM.tif": [[151464.4, 374500.6, 293537.6, 622302.6], [34.50357, 29.45619, 35.9858, 31.69084]], "Boundary_marking_Gulf_of_Aqaba_1946_ITM.tif": [[193304.9, 379579.1, 202239.2, 388110.9], [34.93474, 29.50358, 35.02674, 29.5807]], "Mandate_borders_southern_Palestine_2M_ITM.tif": [[106496.3, 344310.7, 322800.1, 641676.0], [34.04318, 29.18063, 36.29644, 31.86326]], "Operation_Uvda_Golani_1949_ITM.tif": [[111614.4, 374491.9, 268718.9, 597444.7], [34.09284, 29.45332, 35.72279, 31.468]], "TransJordan_250k_Maan_1939_Arava_ITM.tif": [[171101.9, 421371.8, 225560.6, 495825.3], [34.7039, 29.87993, 35.26806, 30.55248]], "UN_Partition_Plan_1947_ITM.tif": [[109863.1, 367748.4, 332197.6, 820492.4], [34.07546, 29.39234, 36.41732, 33.47443]], "Zofar_enclave_1994-2020_ITM.tif": [[216077.4, 492954.7, 224817.0, 498043.1], [35.16923, 30.5266, 35.26032, 30.57249]]}  # ITM and WGS84 extents, computed in the container
def setmeta(m,name,ab):
    rm=m.find('resourceMetadata')
    if rm is None: return
    for t,v in (('title',name),('abstract',ab)):
        el=rm.find(t)
        if el is None: el=etree.SubElement(rm,t)
        el.text=v
for f,name,gp,ab in NEW:
    src=D+f; ext,wgs=BOUNDS[f]
    lid='REVOREN_'+uuid.uuid4().hex[:12]
    m=copy.deepcopy(ml_tpl); m.find('id').text=lid; m.find('datasource').text=src; m.find('layername').text=name
    for tag,v in (('extent',ext),('wgs84extent',wgs)):
        e=m.find(tag)
        if e is not None:
            for k,x in zip(('xmin','ymin','xmax','ymax'),v): e.find(k).text=repr(float(x))
    setmeta(m,name,TAG+' '+ab+CR)
    rr=m.find('.//rasterrenderer')
    if rr is not None:
        rr.set('type','multibandcolor'); rr.set('redBand','1'); rr.set('greenBand','2'); rr.set('blueBand','3'); rr.set('alphaBand','4')
    pl.append(m)
    tl=copy.deepcopy(tl_tpl)
    for c in list(tl): tl.remove(c)
    tl.set('id',lid); tl.set('source',src); tl.set('name',name); tl.set('checked','Qt::Unchecked')
    grp(gp).append(tl)
    co=top.find('custom-order')
    if co is not None: etree.SubElement(co,'item').text=lid
    for lo in r.iter('layerorder'): etree.SubElement(lo,'layer',id=lid)
n_old=0
for key,(note,newname) in OLD.items():
    tls=[l for l in top.iter('layer-tree-layer') if key in l.get('source','')]
    assert tls, key
    for tl in tls:
        m=[m for m in pl if m.find('id').text==tl.get('id')][0]
        rm=m.find('resourceMetadata'); ab=rm.find('abstract') if rm is not None else None
        if ab is None and rm is not None: ab=etree.SubElement(rm,'abstract'); ab.text=''
        t=ab.text or ''
        if 'In the review' in t: t=t[:t.index(' In the review')] if ' In the review' in t else ''
        ab.text=(t+' In the review: '+note+' '+REV+'.').strip(); n_old+=1
with zipfile.ZipFile(M,'w',zipfile.ZIP_DEFLATED) as zo:
    zo.writestr(qn,etree.tostring(r,encoding='utf-8',xml_declaration=True))
    for k,v in extra.items(): zo.writestr(k,v)
print('ok new',len(NEW),'tagged',n_old,'layers',len(list(pl)))
