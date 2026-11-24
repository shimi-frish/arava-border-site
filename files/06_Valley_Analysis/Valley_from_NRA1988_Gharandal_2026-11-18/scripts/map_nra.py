import pickle, numpy as np, geopandas as gpd, rasterio, matplotlib, textwrap
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import patheffects as pe
from rasterio.windows import from_bounds
plt.rcParams['font.family']=['Noto Sans Hebrew','DejaVu Sans']
OUT='/mnt/project-files/valley-from-nra1988/'; FV='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
P=pickle.load(open('/tmp/claude-0/Pnra.pkl','rb')); VE=pickle.load(open('/tmp/claude-0/VE.pkl','rb'))
V=gpd.read_file(FV,layer='valley_polygon_auto_rule').to_crs(2039).geometry.iloc[0]
S=gpd.read_file(FV,layer='straight_line').to_crs(2039).geometry.iloc[0]
r=rasterio.open('/mnt/project-files/jordan-geology/NRA50k_3050III_Wadi_Gharandal_1988_ITM.tif')
X0,X1,Y0,Y1=205000,223829,434451,462186
w=from_bounds(X0,Y0,X1,Y1,r.transform); img=r.read(window=w,out_shape=(3,2800,1900)).transpose(1,2,0)/255.; img=1-(1-img)*0.6
fig=plt.figure(figsize=(8.27,11.69))
Wd=0.6; H=Wd*8.27*(Y1-Y0)/(X1-X0)/11.69
ax=fig.add_axes([0.975-Wd,0.975-H,Wd,H])
ax.imshow(img,extent=(X0,X1,Y0,Y1),interpolation='bilinear',zorder=1)
gpd.GeoSeries([P.difference(VE)]).plot(ax=ax,fc='none',ec='#b45f06',hatch='////',lw=0,zorder=3)
gpd.GeoSeries([VE.difference(P)]).plot(ax=ax,fc='none',ec='#1f4e9c',hatch='\\\\\\\\',lw=0,zorder=3)
for G_,c,lw,ls in [(P,'#b45f06',2,'-'),(V,'#1f4e9c',1.4,(0,(5,2)))]:
    for g in getattr(G_,'geoms',[G_]):
        for ring in [g.exterior]+list(g.interiors):
            x,y=ring.xy; ax.plot(x,y,color='white',lw=lw+1.8,zorder=5); ax.plot(x,y,color=c,lw=lw,ls=ls,zorder=6)
x,y=S.xy; ax.plot(x,y,color='#d7191c',lw=1.2,zorder=7)
def T_(x,y,s,**k):
    kw=dict(fontsize=8.5,ha='center',va='center',zorder=31,path_effects=[pe.withStroke(linewidth=2.8,foreground='white')]); kw.update(k); ax.text(x,y,s,**kw)
for n,x,y,s in [('יהל',207749,443784,'w'),('עין ע\'רנדל',216800,444600,'e')]:
    ax.plot(x,y,'o',ms=4,mfc='white',mec='#111',mew=1,zorder=32); T_(x+(-500 if s=='w' else 500),y+(0 if s=='w' else 700),n,ha='right' if s=='w' else 'left',weight='bold')
T_(207500,452000,'ישראל\n(לא ממופה בגיליון)',fontsize=10,color='#555',weight='bold')
T_(222600,437200,'ירדן',fontsize=14,color='#555',weight='bold')
ax.set_xlim(X0,X1); ax.set_ylim(Y0,Y1); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel('')
sx,sy=X0+1200,Y0+1200
for k in range(2): ax.add_patch(plt.Rectangle((sx+k*2000,sy),2000,180,fc='k' if k%2==0 else 'w',ec='k',lw=.6,zorder=40))
for k in (0,1,2): ax.text(sx+k*2000,sy+420,str(k*2),ha='center',fontsize=7,zorder=40,path_effects=[pe.withStroke(linewidth=2,foreground='white')])
ax.text(sx+4300,sy+90,'ק"מ',ha='left',va='center',fontsize=7.5,zorder=40,path_effects=[pe.withStroke(linewidth=2,foreground='white')])
ax.annotate('',xy=(X0+900,Y1-700),xytext=(X0+900,Y1-2600),arrowprops=dict(arrowstyle='-|>',lw=2,color='k'),zorder=40)
ax.text(X0+900,Y1-600,'N',ha='center',va='bottom',fontsize=10,weight='bold',zorder=40)
EMED=288
iou=P.intersection(VE).area/P.union(VE).area
fp=fig.add_axes([0.015,0.03,0.975-Wd-0.03,0.945]); fp.axis('off'); fp.set_xlim(0,1); fp.set_ylim(0,1)
fp.text(1,0.99,'עמק הערבה לפי',ha='right',va='top',fontsize=16,weight='bold')
fp.text(1,0.958,'המפה הגאולוגית',ha='right',va='top',fontsize=16,weight='bold')
fp.text(1,0.926,'הירדנית 1:50,000',ha='right',va='top',fontsize=16,weight='bold')
fp.text(1,0.888,'גיליון 3050 III ואדי ע\'רנדל',ha='right',va='top',fontsize=9.5,color='#444')
fp.text(1,0.866,'(NRA, מיפוי 1988, הדפסה 1990)',ha='right',va='top',fontsize=9.5,color='#444')
y=0.825; fp.text(1,y,'מקרא',ha='right',va='top',fontsize=11,weight='bold'); y-=0.032
def leg(kind,txt,wrap=30):
    global y
    if kind=='nra': fp.plot([0.80,0.98],[y-0.007]*2,color='#b45f06',lw=2.2)
    elif kind=='fin': fp.plot([0.80,0.98],[y-0.007]*2,color='#1f4e9c',lw=1.5,ls=(0,(5,2)))
    elif kind=='str': fp.plot([0.80,0.98],[y-0.007]*2,color='#d7191c',lw=1.2)
    elif kind=='hg': fp.add_patch(plt.Rectangle((0.80,y-0.016),0.18,0.016,fc='none',ec='#b45f06',hatch='////',lw=0))
    elif kind=='hf': fp.add_patch(plt.Rectangle((0.80,y-0.016),0.18,0.016,fc='none',ec='#1f4e9c',hatch='\\\\\\\\',lw=0))
    L=textwrap.wrap(txt,wrap)
    for k,l in enumerate(L): fp.text(0.76,y-k*0.018,l,ha='right',va='top',fontsize=8.2)
    y-=0.018*len(L)+0.011
leg('nra',f'העמק לפי מפת NRA ‏({P.area/1e6:.0f} קמ"ר, הצד הירדני בלבד)')
leg('fin','העמק לפי רגל ההר – התיחום הסופי')
leg('hg','רק לפי מפת NRA'); leg('hf','רק לפי רגל ההר')
leg('str','קו ישר ים המלח – אילת')
y-=0.008; fp.text(1,y,'איך נקלט',ha='right',va='top',fontsize=11,weight='bold'); y-=0.03
TX=['סיווג צבעים של הרסטר המגואורפרנס לפי צבעי המקרא. נכללו יחידות הסחף: Al (סחף וערוצי נחלים, הולוקן), Alf/Alm/Als (מניפות, שטחי בוץ, חול), Plg/Pls (חצץ וחול נחלי, פלייסטוקן) ו-LM (חוואר הלשון).',
 'קווים וכיתוב בתוך שטחי הסחף צורפו לשטח; ערוצים צרים מ-1 ק"מ שחודרים להרים הוסרו ("פתיחה" ברדיוס 500 מ\'); נשמר הגוש הרציף, ואיי סלע קטנים מ-2 קמ"ר מולאו.',
 'הגיליון ממפה רק את הצד הירדני, ולכן הגבול המערבי של הפוליגון הוא שולי השטח הממופה (קו שביתת הנשק המודפס במפה).']
for t in TX:
    for l in textwrap.wrap(t,40): fp.text(1,y,l,ha='right',va='top',fontsize=7.8,color='#222'); y-=0.0165
    y-=0.005
fq=fig.add_axes([0.975-Wd,0.03,Wd,0.975-H-0.06]); fq.axis('off'); fq.set_xlim(0,1); fq.set_ylim(0,1)
fq.text(1,0.97,'השוואה לתיחום הסופי',ha='right',va='top',fontsize=11,weight='bold'); yq=0.86
FX=['ההשוואה נעשתה באותה רצועה בלבד, ממזרח לשולי המיפוי.',f'מידת החפיפה (שטח החיתוך חלקי שטח האיחוד): {iou:.2f}.',f'שטח שנמצא רק בתיחום הגאולוגי: {P.difference(VE).area/1e6:.0f} קמ"ר. שטח שנמצא רק בתיחום לפי רגל ההר: {VE.difference(P).area/1e6:.0f} קמ"ר.',
 f'השוליים המזרחיים: הפרש חציוני כ-{EMED:.0f} מ\' בין שני התיחומים.',
 'ההבדל העיקרי (כ-8 קמ"ר) בפתח ואדי ע\'רנדל: התיחום לפי רגל ההר נכנס לעומק הפתח, והמפה מסמנת שם יחידות סלע וקונגלומרט.']
for t in FX:
    for l in textwrap.wrap(t,70): fq.text(1,yq,l,ha='right',va='top',fontsize=8.3,color='#222'); yq-=0.075
    yq-=0.02
y=0.10
for s_ in ['מקור: Ibrahim & Rashdan 1988, Geological Map of Jordan 1:50,000, sheet 3050 III Wadi Gharandal, NRA. © NRA/MEMR – לשימוש מחקרי, לא לפרסום באתר.']:
    for l in textwrap.wrap(s_,55): fp.text(1,y,l,ha='right',va='top',fontsize=6.5,color='#444'); y-=0.013
fp.text(1,0.045,'שמעון פריש, הטכניון – עבודת דוקטורט',ha='right',va='top',fontsize=7,color='#444')
fp.text(1,0.03,'בהנחיית פרופ׳ מקסים שושני ופרופ׳ אביעד שפירא',ha='right',va='top',fontsize=7,color='#444')
fp.text(1,0.015,'© כל הזכויות שמורות',ha='right',va='top',fontsize=7,color='#444')
gpd.GeoDataFrame([dict(name='valley_NRA1988_Gharandal',area_km2=round(P.area/1e6,2),source='NRA 1:50k 3050 III Wadi Gharandal 1988; colour classification Al,Alf,Alm,Als,Plg,Pls,LM; opening 500 m',geometry=P)],crs=2039).to_file(OUT+'Arava_valley_from_NRA1988_Gharandal.gpkg',layer='valley_polygon_nra1988',driver='GPKG')
gpd.GeoDataFrame([dict(side='nra_only',geometry=P.difference(VE)),dict(side='mountain_foot_only',geometry=VE.difference(P))],crs=2039).to_file(OUT+'Arava_valley_from_NRA1988_Gharandal.gpkg',layer='difference_vs_final',driver='GPKG')
fig.savefig(OUT+'arava_valley_nra1988_gharandal.png',dpi=300); fig.savefig(OUT+'arava_valley_nra1988_gharandal.pdf')
print('H',H, 'iou',iou)
