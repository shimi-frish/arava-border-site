import pickle, numpy as np, geopandas as gpd, matplotlib, textwrap
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import patheffects as pe
from shapely.geometry import box
plt.rcParams['font.family']=['Noto Sans Hebrew','DejaVu Sans']
OUT='/mnt/project-files/valley-from-jordan-geology/'; FV='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
exec(open(OUT+'scripts/extract_core.py').read())   # defines P, V, g, YN
VA=V.geometry.iloc[0]
ZONES=[(205700,452557,193000,452557),(194509,389163,186000,395000),(199637,414367,189000,414367),(232838,551073,219000,553000),
       (216646,520249,203000,520249),(223107,456725,236000,456725),(208165,408246,220000,404000),(241972,554650,255000,541000)]
gi=P.difference(VA).area/1e6; fi=VA.difference(P).area/1e6; iou=P.intersection(VA).area/P.union(VA).area
METHOD=['אוחדו כל פוליגוני המשקעים הרביעוניים במפה (Qs1–Qs5).',
 'סינון ערוצי נחלים צרים שחודרים להרים: "פתיחה" מורפולוגית ברדיוס 500 מ\' (מוסרים רצועות צרות מ-1 ק"מ).',
 'נשמר הגוש הרציף שהגבול עובר בו; איי סלע קטנים מ-2 קמ"ר מולאו. צפון: כמו בתיחום הסופי; דרום: חוף המפרץ.']
FINDINGS=[f'חפיפה (IoU, שטח החיתוך חלקי שטח האיחוד): {iou:.2f}. שטח רק לפי הגאולוגיה {gi:.0f} קמ"ר, רק לפי רגל ההר {fi:.0f} קמ"ר.',
 'רק לפי הגאולוגיה: (1) מישור פארן, (2) המניפות שממערב לאילת, (3) אגן תמנע וסביבתו, (4) מדרום לים המלח באזור נאות הכיכר. 1 ו-3 הם אזורים שהוצאו מהעמק בתיחום הסופי.',
 'רק לפי רגל ההר: (5) מערבית לחצבה, שם המפה הגאולוגית מסמנת סלע (Ks3, קרטיקון עליון) עד קו הגבול, (6) רגלי ההרים מזרחית לע\'רנדל, (7) רגלי הגרניט בדרום הצד הירדני, (8) בריכות ים המלח שאינן ממופות כיבשה.',
 'המפה הארצית בקנה מידה 1:500,000 כללית מאוד בצד הישראלי, ולכן בצד המערבי ההשוואה פחות אמינה.']

X0,X1,Y0,Y1=180000,262000,378000,562000
g['geometry']=g.buffer(0); gg=g[g.intersects(box(X0,Y0,X1,Y1))]
COL={'Qs5':'#fff2b3','Qs4':'#f9dcc0','Qs3':'#f6c08a','Qs2':'#f1d77a','Qs1':'#e7c3a0'}
fig=plt.figure(figsize=(8.27,11.69))
H=0.88; Wd=H*11.69*(X1-X0)/(Y1-Y0)/8.27
ax=fig.add_axes([0.975-Wd,0.05,Wd,H])
gg.plot(ax=ax,color=[COL.get(u,'#e4e4e4') for u in gg.unit_code],ec='#c8c8c8',lw=.15,zorder=1)
VA=V.geometry.iloc[0]
gpd.GeoSeries([P.difference(VA)],crs=2039).plot(ax=ax,fc='none',ec='#b45f06',hatch='////',lw=0,zorder=3)
gpd.GeoSeries([VA.difference(P)],crs=2039).plot(ax=ax,fc='none',ec='#1f4e9c',hatch='\\\\\\\\',lw=0,zorder=3)
for G_,c,lw,ls in [(P,'#b45f06',1.8,'-'),(VA,'#1f4e9c',1.3,(0,(5,2)))]:
    for r in getattr(G_,'geoms',[G_]):
        for ring in [r.exterior]+list(r.interiors):
            x,y=ring.xy; ax.plot(x,y,color='white',lw=lw+1.6,zorder=5); ax.plot(x,y,color=c,lw=lw,ls=ls,zorder=6)
S=gpd.read_file(FV,layer='straight_line').to_crs(2039); x,y=S.geometry.iloc[0].xy; ax.plot(x,y,color='#d7191c',lw=1.1,zorder=7)
def u(lo,la): q=gpd.GeoSeries(gpd.points_from_xy([lo],[la]),crs=4326).to_crs(2039).iloc[0]; return q.x,q.y
def T_(x,y,s,**k):
    kw=dict(fontsize=8,ha='center',va='center',zorder=31,path_effects=[pe.withStroke(linewidth=2.6,foreground='white')]); kw.update(k); ax.text(x,y,s,**kw)
PL=[('אילת',34.951,29.557,'w',1),('עקבה',35.006,29.532,'e',1),('יטבתה',35.062,29.887,'w',1),('פארן',35.151,30.356,'w',1),
 ('ספיר',35.187,30.617,'w',1),('חצבה',35.255,30.783,'w',1),('נאות הכיכר',35.373,30.932,'w',1),('גור א-צאפי',35.470,31.030,'e',1),('פינאן',35.493,30.627,'e',1)]
for n,lo,la,s,mj in PL:
    x,y=u(lo,la); ax.plot(x,y,'o',ms=3.4,mfc='white',mec='#111',mew=1,zorder=32)
    T_(x+(-1200 if s=='w' else 1200),y,n,ha='right' if s=='w' else 'left',fontsize=8.4,weight='bold')
for n,x,y in [('ישראל',190000,500000),('ירדן',255000,450000)]: T_(x,y,n,fontsize=15,weight='bold',color='#777')
# numbered difference zones
for k,(x,y,xt,yt) in enumerate(ZONES,1):
    ax.annotate(str(k),xy=(x,y),xytext=(xt,yt),fontsize=8.5,weight='bold',ha='center',va='center',
        bbox=dict(boxstyle='circle,pad=0.25',fc='white',ec='#333',lw=.8),arrowprops=dict(arrowstyle='-',lw=.7,color='#333'),zorder=34)
ax.set_xlim(X0,X1); ax.set_ylim(Y0,Y1); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel('')
sx,sy=X1-24000,Y0+4000
for k in range(2): ax.add_patch(plt.Rectangle((sx+k*10000,sy),10000,800,fc='k' if k%2==0 else 'w',ec='k',lw=.6,zorder=40))
for k in (0,1,2): ax.text(sx+k*10000,sy+1700,str(k*10),ha='center',fontsize=7,zorder=40,path_effects=[pe.withStroke(linewidth=2,foreground='white')])
ax.text(sx-1000,sy+400,'ק"מ',ha='right',va='center',fontsize=7.5,zorder=40,path_effects=[pe.withStroke(linewidth=2,foreground='white')])
ax.annotate('',xy=(X0+5000,Y1-3500),xytext=(X0+5000,Y1-12000),arrowprops=dict(arrowstyle='-|>',lw=2,color='k'),zorder=40)
ax.text(X0+5000,Y1-3000,'N',ha='center',va='bottom',fontsize=10,weight='bold',zorder=40)
fp=fig.add_axes([0.015,0.03,0.975-Wd-0.03,0.945]); fp.axis('off'); fp.set_xlim(0,1); fp.set_ylim(0,1)
fp.text(1,0.99,'עמק הערבה לפי',ha='right',va='top',fontsize=17,weight='bold')
fp.text(1,0.957,'המפה הגאולוגית של ירדן',ha='right',va='top',fontsize=17,weight='bold')
fp.text(1,0.922,'משקעים רביעוניים (Qs1–Qs5), מאילת עד בריכות ים המלח',ha='right',va='top',fontsize=9.3,color='#444')
y=0.88; fp.text(1,y,'מקרא',ha='right',va='top',fontsize=11,weight='bold'); y-=0.034
def leg(kind,txt,wrap=40):
    global y
    if kind=='geo': fp.plot([0.84,0.98],[y-0.007]*2,color='#b45f06',lw=2)
    elif kind=='fin': fp.plot([0.84,0.98],[y-0.007]*2,color='#1f4e9c',lw=1.5,ls=(0,(5,2)))
    elif kind=='str': fp.plot([0.84,0.98],[y-0.007]*2,color='#d7191c',lw=1.2)
    elif kind=='hg': fp.add_patch(plt.Rectangle((0.84,y-0.016),0.14,0.016,fc='none',ec='#b45f06',hatch='////',lw=0))
    elif kind=='hf': fp.add_patch(plt.Rectangle((0.84,y-0.016),0.14,0.016,fc='none',ec='#1f4e9c',hatch='\\\\\\\\',lw=0))
    else: fp.add_patch(plt.Rectangle((0.84,y-0.016),0.14,0.016,fc=kind,ec='#999',lw=.4))
    L=textwrap.wrap(txt,wrap)
    for k,l in enumerate(L): fp.text(0.81,y-k*0.017,l,ha='right',va='top',fontsize=7.6)
    y-=0.017*len(L)+0.009
leg('geo',f'העמק לפי המפה הגאולוגית ({P.area/1e6:,.0f} קמ"ר)')
leg('fin',f'העמק לפי רגל ההר – התיחום הסופי ({VA.area/1e6:,.0f} קמ"ר)')
leg('hg','רק לפי המפה הגאולוגית'); leg('hf','רק לפי רגל ההר')
leg('str','קו ישר ים המלח – אילת')
for c,t in [('#fff2b3','Qs5 – משקעי סחף ואגם לא מלוכדים'),('#f9dcc0','Qs4 – משקעים פליטיים (שטחי בוץ)'),('#f6c08a','Qs3 – תצורת הלשון'),('#f1d77a','Qs2 – חצץ נחלי, גיר ומרל אגמי'),('#e4e4e4','סלע (יחידות קדם-רביעוניות)')]: leg(c,t)
y-=0.006; fp.text(1,y,'איך נקלט',ha='right',va='top',fontsize=11,weight='bold'); y-=0.03
for t in METHOD:
    for l in textwrap.wrap(t,54): fp.text(1,y,l,ha='right',va='top',fontsize=7.4,color='#222'); y-=0.0158
    y-=0.004
y-=0.004; fp.text(1,y,'השוואה לתיחום הסופי',ha='right',va='top',fontsize=11,weight='bold'); y-=0.03
for t in FINDINGS:
    for l in textwrap.wrap(t,54): fp.text(1,y,l,ha='right',va='top',fontsize=7.4,color='#222'); y-=0.0158
    y-=0.004
y=0.085
for s_ in ['מקור: Kempf 2023, Digital Geological Map of Jordan, doi:10.5281/zenodo.10061800 (CC-BY 4.0), דיגיטציה של Bender 1975, USGS PP 560-I לוח 1, 1:500,000. דיוק המקור כ-0.5–1 ק"מ.']:
    for l in textwrap.wrap(s_,70): fp.text(1,y,l,ha='right',va='top',fontsize=6.2,color='#444'); y-=0.012
fp.text(1,0.040,'שמעון פריש, הטכניון – עבודת דוקטורט',ha='right',va='top',fontsize=7,color='#444')
fp.text(1,0.027,'בהנחיית פרופ׳ מקסים שושני ופרופ׳ אביעד שפירא',ha='right',va='top',fontsize=7,color='#444')
fp.text(1,0.014,'© כל הזכויות שמורות',ha='right',va='top',fontsize=7,color='#444')
gpd.GeoDataFrame([dict(name='valley_jordan_geology',area_km2=round(P.area/1e6,1),source='Kempf 2023 (USGS PP560-I), Qs1-Qs5, opening 500 m',geometry=P)],crs=2039).to_file(OUT+'Arava_valley_from_Jordan_geology.gpkg',layer='valley_polygon_geology',driver='GPKG')
gpd.GeoDataFrame([dict(side='geology_only',geometry=P.difference(VA)),dict(side='mountain_foot_only',geometry=VA.difference(P))],crs=2039).to_file(OUT+'Arava_valley_from_Jordan_geology.gpkg',layer='difference_vs_final',driver='GPKG')
fig.savefig(OUT+'arava_valley_jordan_geology.png',dpi=300); fig.savefig(OUT+'arava_valley_jordan_geology.pdf')
