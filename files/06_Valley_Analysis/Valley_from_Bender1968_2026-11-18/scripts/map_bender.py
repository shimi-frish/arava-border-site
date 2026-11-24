import pickle, numpy as np, geopandas as gpd, rasterio, matplotlib, textwrap
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import patheffects as pe
from rasterio.windows import from_bounds
plt.rcParams['font.family']=['Noto Sans Hebrew','DejaVu Sans']
OUT='/mnt/project-files/valley-from-bender1968/'; FV='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
P,VC=pickle.load(open('/tmp/claude-0/Pb_final.pkl','rb'))
S=gpd.read_file(FV,layer='straight_line').to_crs(2039).geometry.iloc[0]
X0,X1,Y0,Y1=182000,260000,378000,561000
fig=plt.figure(figsize=(8.27,11.69))
H=0.90; Wd=H*11.69*(X1-X0)/(Y1-Y0)/8.27
ax=fig.add_axes([0.975-Wd,0.05,Wd,H])
for f,ya,yb in [('Aqaba-Maan',Y0,546400),('Amman',546400,Y1)]:
    r=rasterio.open(f'/mnt/project-files/jordan-geology/Bender1968_250k_{f}_ITM.tif')
    img=r.read(window=from_bounds(X0,ya,X1,yb,r.transform),out_shape=(3,int((yb-ya)/50),int((X1-X0)/50)),boundless=True,fill_value=255).transpose(1,2,0)/255.; img=1-(1-img)*0.55
    ax.imshow(img,extent=(X0,X1,ya,yb),interpolation='bilinear',zorder=1)
gpd.GeoSeries([P.difference(VC)]).plot(ax=ax,fc='none',ec='#b45f06',hatch='////',lw=0,zorder=3)
gpd.GeoSeries([VC.difference(P)]).plot(ax=ax,fc='none',ec='#1f4e9c',hatch='\\\\\\\\',lw=0,zorder=3)
for G_,c,lw,ls in [(P,'#b45f06',1.9,'-'),(VC,'#1f4e9c',1.3,(0,(5,2)))]:
    for g in getattr(G_,'geoms',[G_]):
        for ring in [g.exterior]+list(g.interiors):
            x,y=ring.xy; ax.plot(x,y,color='white',lw=lw+1.6,zorder=5); ax.plot(x,y,color=c,lw=lw,ls=ls,zorder=6)
x,y=S.xy; ax.plot(x,y,color='#d7191c',lw=1.1,zorder=7)
def u(lo,la): q=gpd.GeoSeries(gpd.points_from_xy([lo],[la]),crs=4326).to_crs(2039).iloc[0]; return q.x,q.y
def T_(x,y,s,**k):
    kw=dict(fontsize=8,ha='center',va='center',zorder=31,path_effects=[pe.withStroke(linewidth=2.6,foreground='white')]); kw.update(k); ax.text(x,y,s,**kw)
PL=[('אילת',34.951,29.557,'w'),('עקבה',35.006,29.532,'e'),('יטבתה',35.062,29.887,'w'),('פארן',35.151,30.356,'w'),
 ('ספיר',35.187,30.617,'w'),('חצבה',35.255,30.783,'w'),('נאות הכיכר',35.373,30.932,'w'),('פינאן',35.493,30.627,'e')]
for n,lo,la,s in PL:
    x,y=u(lo,la); ax.plot(x,y,'o',ms=3.4,mfc='white',mec='#111',mew=1,zorder=32)
    T_(x+(-1200 if s=='w' else 1200),y,n,ha='right' if s=='w' else 'left',fontsize=8.4,weight='bold')
for n,x,y in [('ישראל',190000,480000),('ירדן',252000,445000)]: T_(x,y,n,fontsize=15,weight='bold',color='#666')
ZONES=[(205792,452570,190500,455000),(195098,388025,186500,394000),(232972,551688,220000,553000),(245317,540517,255000,532000),(209150,472878,196000,476000),
       (216269,510243,201000,506000),(242230,554633,255000,557000),(211929,466450,198000,463000),(226717,465633,239000,462000),(235564,502264,250000,494000)]
for k,(x,y,xt,yt) in enumerate(ZONES,1):
    ax.annotate(str(k),xy=(x,y),xytext=(xt,yt),fontsize=8.5,weight='bold',ha='center',va='center',
        bbox=dict(boxstyle='circle,pad=0.25',fc='white',ec='#333',lw=.8),arrowprops=dict(arrowstyle='-',lw=.7,color='#333'),zorder=34)
ax.set_xlim(X0,X1); ax.set_ylim(Y0,Y1); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel('')
sx,sy=X1-24000,Y0+4000
for k in range(2): ax.add_patch(plt.Rectangle((sx+k*10000,sy),10000,800,fc='k' if k%2==0 else 'w',ec='k',lw=.6,zorder=40))
for k in (0,1,2): ax.text(sx+k*10000,sy+1700,str(k*10),ha='center',fontsize=7,zorder=40,path_effects=[pe.withStroke(linewidth=2,foreground='white')])
ax.text(sx-1000,sy+400,'ק"מ',ha='right',va='center',fontsize=7.5,zorder=40,path_effects=[pe.withStroke(linewidth=2,foreground='white')])
ax.annotate('',xy=(X0+4000,Y1-3500),xytext=(X0+4000,Y1-12000),arrowprops=dict(arrowstyle='-|>',lw=2,color='k'),zorder=40)
ax.text(X0+4000,Y1-3000,'N',ha='center',va='bottom',fontsize=10,weight='bold',zorder=40)
iou=P.intersection(VC).area/P.union(VC).area; gi=P.difference(VC).area/1e6; fi=VC.difference(P).area/1e6
fp=fig.add_axes([0.015,0.03,0.975-Wd-0.03,0.945]); fp.axis('off'); fp.set_xlim(0,1); fp.set_ylim(0,1)
fp.text(1,0.99,'עמק הערבה לפי',ha='right',va='top',fontsize=17,weight='bold')
fp.text(1,0.957,'מפת Bender 1968',ha='right',va='top',fontsize=17,weight='bold')
fp.text(1,0.922,'המפה הגאולוגית של ירדן 1:250,000, גיליונות עקבה–מען ועמאן',ha='right',va='top',fontsize=9.1,color='#444')
y=0.885; fp.text(1,y,'מקרא',ha='right',va='top',fontsize=11,weight='bold'); y-=0.034
def leg(kind,txt,wrap=40):
    global y
    if kind=='geo': fp.plot([0.84,0.98],[y-0.007]*2,color='#b45f06',lw=2)
    elif kind=='fin': fp.plot([0.84,0.98],[y-0.007]*2,color='#1f4e9c',lw=1.5,ls=(0,(5,2)))
    elif kind=='str': fp.plot([0.84,0.98],[y-0.007]*2,color='#d7191c',lw=1.2)
    elif kind=='hg': fp.add_patch(plt.Rectangle((0.84,y-0.016),0.14,0.016,fc='none',ec='#b45f06',hatch='////',lw=0))
    elif kind=='hf': fp.add_patch(plt.Rectangle((0.84,y-0.016),0.14,0.016,fc='none',ec='#1f4e9c',hatch='\\\\\\\\',lw=0))
    L=textwrap.wrap(txt,wrap)
    for k,l in enumerate(L): fp.text(0.81,y-k*0.017,l,ha='right',va='top',fontsize=7.8)
    y-=0.017*len(L)+0.01
leg('geo',f'העמק לפי מפת Bender ‏({P.area/1e6:,.0f} קמ"ר)')
leg('fin',f'העמק לפי רגל ההר – התיחום הסופי ({VC.area/1e6:,.0f} קמ"ר)')
leg('hg','רק לפי מפת Bender'); leg('hf','רק לפי רגל ההר'); leg('str','קו ישר ים המלח – אילת')
y-=0.006; fp.text(1,y,'איך נקלט',ha='right',va='top',fontsize=11,weight='bold'); y-=0.03
METHOD=['יחידות העמק לפי המקרא: q5 (סחף נחלים ווואדיות, חול אאולי), q4 (משקעי בוץ בשטחי הצפה), q3 (מניפות ומדרוני טאלוס), q2 עם עיגולים (חצץ נחלי פלייסטוקני) ו-q2 (חוואר הלשון). כולן מסומנות בגווני קרם ובז\'.',
 'בכל תא של 300 מ\' חושב החלק של פיקסלים בצבעי קרם/בז\' לעומת פיקסלים בצבעי סלע (צבע רווי). קווים, כיתוב ועיגולים קטנים לא נספרו.',
 'שטח עמק = לפחות 60% קרם/בז\' ופחות מ-30% סלע. נסגרו פערים של עד 200 מ\', הוסרו ערוצים צרים מ-2 ק"מ ("פתיחה" ברדיוס 1 ק"מ), ונשמר הגוש הרציף שהקו הישר עובר בו. שני הגיליונות אוחדו; גבול צפוני כמו בתיחום הסופי.']
for t in METHOD:
    for l in textwrap.wrap(t,52): fp.text(1,y,l,ha='right',va='top',fontsize=7.4,color='#222'); y-=0.0158
    y-=0.004
y-=0.004; fp.text(1,y,'השוואה לתיחום הסופי',ha='right',va='top',fontsize=11,weight='bold'); y-=0.03
FIND=[f'מידת החפיפה (שטח החיתוך חלקי שטח האיחוד): {iou:.2f}.',
 f'שטח שנמצא רק לפי Bender: {gi:.0f} קמ"ר. שטח שנמצא רק לפי רגל ההר: {fi:.0f} קמ"ר.',
 'רק לפי Bender: (1) מישור פארן, (2) המניפות שממערב לאילת, (3) מישור סדום ממערב לנאות הכיכר (חוואר הלשון), (4) מניפות בצד הירדני מדרום לגור א-צאפי, (5) שוליים מערביים ליד פארן.',
 'רק לפי רגל ההר: (6) מערבית לחצבה ועין יהב, שם Bender ממפה את תצורת חצבה (tl) ויחידות קרטיקון עד רגלי ההר, (7) בריכות ים המלח, שב-1968 היו עדיין חלק מהאגן הדרומי של הים, (8) מדרום לפארן, (9) רגלי ההרים מזרחית לע\'רנדל, (10) פתח ואדי פידאן.']
for t in FIND:
    for l in textwrap.wrap(t,52): fp.text(1,y,l,ha='right',va='top',fontsize=7.4,color='#222'); y-=0.0158
    y-=0.004
y=0.09
for s_ in ['מקור: F. Bender et al. 1968, Geologische Karte von Jordanien 1:250,000, Blätter Aqaba–Ma\'an, Amman, BfB Hannover. סריקה: הספרייה הלאומית של אוסטרליה. מוגן בזכויות יוצרים – לשימוש מחקרי.']:
    for l in textwrap.wrap(s_,64): fp.text(1,y,l,ha='right',va='top',fontsize=6.2,color='#444'); y-=0.012
fp.text(1,0.040,'שמעון פריש, הטכניון – עבודת דוקטורט',ha='right',va='top',fontsize=7,color='#444')
fp.text(1,0.027,'בהנחיית פרופ׳ מקסים שושני ופרופ׳ אביעד שפירא',ha='right',va='top',fontsize=7,color='#444')
fp.text(1,0.014,'© כל הזכויות שמורות',ha='right',va='top',fontsize=7,color='#444')
gpd.GeoDataFrame([dict(name='valley_Bender1968',area_km2=round(P.area/1e6,1),source='Bender 1968 1:250k Aqaba-Maan + Amman; q2-q5 colour share>=60%, rock<30% (300 m cells), closing 200 m, opening 1000 m',geometry=P)],crs=2039).to_file(OUT+'Arava_valley_from_Bender1968.gpkg',layer='valley_polygon_bender1968',driver='GPKG')
gpd.GeoDataFrame([dict(side='bender_only',geometry=P.difference(VC)),dict(side='mountain_foot_only',geometry=VC.difference(P))],crs=2039).to_file(OUT+'Arava_valley_from_Bender1968.gpkg',layer='difference_vs_final',driver='GPKG')
fig.savefig(OUT+'arava_valley_bender1968.png',dpi=300); fig.savefig(OUT+'arava_valley_bender1968.pdf')
