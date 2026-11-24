import numpy as np, geopandas as gpd, rasterio, matplotlib, textwrap, pandas as pd
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import patheffects as pe
from rasterio.windows import from_bounds
from shapely.geometry import LineString
from shapely.ops import unary_union
plt.rcParams['font.family']=['Noto Sans Hebrew','DejaVu Sans']
D='/mnt/user-data/uploads/Israel-Jordan-Arava/01_Borders/'; OUT='/mnt/project-files/armistice-vs-mandate/'
a=gpd.read_file(D+'Armistice_line_hist_maps_grid_ITM.gpkg').to_crs(2039)
m=gpd.read_file(D+'Mandate_border_1942_digitized.gpkg').to_crs(2039)
A=unary_union(list(a.geometry)); M=unary_union(list(m.geometry))
def xat(G,y):
    i=G.intersection(LineString([(150000,y),(300000,y)]))
    if i.is_empty: return np.nan
    return np.mean([p.x for p in getattr(i,'geoms',[i])])
Y=np.arange(384800,540050,100.)
XA=np.array([xat(A,y) for y in Y]); XM=np.array([xat(M,y) for y in Y]); DX=XM-XA  # >0 : armistice west of mandate
ok=~np.isnan(DX)
pd.DataFrame(dict(itm_y=Y,x_armistice=XA,x_mandate=XM,dx_m=DX)).to_csv(OUT+'gap_by_northing_100m.csv',index=False)
W=DX[ok&(DX>0)].sum()*100/1e6; E_=-DX[ok&(DX<0)].sum()*100/1e6
ad=np.abs(DX[ok]); print('cov km',ok.sum()/10,'mean',ad.mean(),'med',np.median(ad),'p90',np.percentile(ad,90),'max',ad.max(),Y[ok][ad.argmax()],'W',W,'E',E_)
print('share <500',(ad<500).mean(),'<1000',(ad<1000).mean())
X0,X1,Y0,Y1=186000,248000,378000,546000
r=rasterio.open('/mnt/project-files/british-map/Palestine_1-250000_South_sheet_1942_georef_ITM.tif')
w=from_bounds(X0,Y0,X1,Y1,r.transform); img=r.read(window=w,out_shape=(3,int((Y1-Y0)/25),int((X1-X0)/25))).transpose(1,2,0)/255.
img=1-(1-img)*0.55  # fade
fig=plt.figure(figsize=(8.27,11.69))
H=0.86; Wd=H*11.69*(X1-X0)/(Y1-Y0)/8.27
ax=fig.add_axes([0.335,0.055,Wd,H])
ax.imshow(img,extent=(X0,X1,Y0,Y1),interpolation='bilinear',zorder=1)
ax.fill_betweenx(Y,XA,XM,where=ok&(DX>0),color='#f28e2b',alpha=.75,lw=0,zorder=5)
ax.fill_betweenx(Y,XA,XM,where=ok&(DX<0),color='#59a14f',alpha=.75,lw=0,zorder=5)
for g in m.geometry.explode():
    x,y=g.xy; ax.plot(x,y,color='white',lw=3,zorder=8); ax.plot(x,y,color='#1f4e9c',lw=1.5,ls=(0,(5,2)),zorder=9)
for g in a.geometry.explode():
    x,y=g.xy; ax.plot(x,y,color='white',lw=3,zorder=10); ax.plot(x,y,color='#d7191c',lw=1.5,zorder=11)
def u(lo,la): q=gpd.GeoSeries(gpd.points_from_xy([lo],[la]),crs=4326).to_crs(2039).iloc[0]; return q.x,q.y
def T_(x,y,s,**k):
    kw=dict(fontsize=8,ha='center',va='center',zorder=31,path_effects=[pe.withStroke(linewidth=2.6,foreground='white')]); kw.update(k); ax.text(x,y,s,**kw)
PL=[('עקבה',35.006,29.532,'e',1),('באר אורה',34.995,29.708,'w',0),('יטבתה',35.062,29.887,'w',1),
 ('קטורה',35.063,29.970,'w',0),('יהל',35.083,30.083,'w',0),('פארן',35.151,30.356,'w',1),('צופר',35.180,30.552,'w',0),
 ('ספיר',35.187,30.617,'w',1),('עין יהב',35.240,30.660,'w',0),('חצבה',35.255,30.783,'w',1),('עין ע\'רנדל',35.208,29.933,'e',0)]
for n,lo,la,s,mj in PL:
    x,y=u(lo,la)
    if not (X0<x<X1 and Y0<y<Y1): continue
    ax.plot(x,y,'o',ms=3.4 if mj else 2.8,mfc='white',mec='#111',mew=1,zorder=32)
    T_(x+(-1000 if s=='w' else 1000),y,n,ha='right' if s=='w' else 'left',fontsize=8.4 if mj else 7.4,weight='bold' if mj else 'normal')
x,y=u(34.951,29.557); ax.plot(x,y,'o',ms=3.4,mfc='white',mec='#111',mew=1,zorder=32); T_(x-1000,y+2600,'אילת',ha='right',fontsize=8.4,weight='bold')
x,y=195700,384750; ax.plot(x,y,'s',ms=3.5,mfc='#1f4e9c',mec='k',zorder=32)
ax.annotate('אום רשרש',xy=(x,y),xytext=(x-1500,y-3700),ha='center',va='center',fontsize=7.4,color='#1f4e9c',arrowprops=dict(arrowstyle='-',lw=.6,color='#1f4e9c'),zorder=33,path_effects=[pe.withStroke(linewidth=2.6,foreground='white')])
for n,x,y in [('מפרץ אילת/עקבה',206500,379300)]: T_(x,y,n,color='#0b4f8a',style='italic',fontsize=7)
for n,x,y in [('ישראל',196000,470000),('ירדן',244000,440000)]: T_(x,y,n,fontsize=15,weight='bold',color='#666',alpha=.8)
# max gap annotation
i=np.nanargmax(np.abs(DX)); ax.annotate(f'פער מרבי\n{abs(DX[i])/1000:.1f} ק"מ',xy=((XA[i]+XM[i])/2,Y[i]),xytext=(XM[i]+9000,Y[i]-9000),fontsize=8,weight='bold',ha='center',
  arrowprops=dict(arrowstyle='-',lw=.8),zorder=33,path_effects=[pe.withStroke(linewidth=2.6,foreground='white')])
ax.set_xlim(X0,X1); ax.set_ylim(Y0,Y1); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
sx,sy=X1-22000,Y0+4000
for k in range(2): ax.add_patch(plt.Rectangle((sx+k*10000,sy),10000,700,fc='k' if k%2==0 else 'w',ec='k',lw=.6,zorder=40))
for k in (0,1,2): ax.text(sx+k*10000,sy+1500,str(k*10),ha='center',fontsize=7,zorder=40,path_effects=[pe.withStroke(linewidth=2,foreground='white')])
ax.text(sx-1000,sy+350,'ק"מ',ha='right',va='center',fontsize=7.5,zorder=40,path_effects=[pe.withStroke(linewidth=2,foreground='white')])
ax.annotate('',xy=(X1-4000,Y1-3000),xytext=(X1-4000,Y1-11000),arrowprops=dict(arrowstyle='-|>',lw=2,color='k'),zorder=40)
ax.text(X1-4000,Y1-2600,'N',ha='center',va='bottom',fontsize=10,weight='bold',zorder=40)
# side graph
g=fig.add_axes([0.335+Wd+0.025,0.055,0.975-(0.335+Wd+0.025),H]); g.set_ylim(Y0,Y1); g.set_yticks([])
g.fill_betweenx(Y,0,DX/1000,where=ok&(DX>0),color='#f28e2b',lw=0); g.fill_betweenx(Y,0,DX/1000,where=ok&(DX<0),color='#59a14f',lw=0)
g.plot(np.where(ok,DX/1000,np.nan),Y,color='k',lw=.6); g.axvline(0,color='k',lw=.8)
for v in (-2,2,4,6): g.axvline(v,color='#bbb',lw=.4,ls=':')
g.set_xlim(-2.5,7); g.tick_params(labelleft=False,labelsize=7); 
g.set_title('פער אופקי (ק"מ)\nכתום: שביתת הנשק ממערב',fontsize=7.5)
for s in ('top','right','left'): g.spines[s].set_visible(False)
# text panel
fp=fig.add_axes([0.015,0.03,0.31,0.945]); fp.axis('off'); fp.set_xlim(0,1); fp.set_ylim(0,1)
fp.text(1,0.99,'קו שביתת הנשק מול',ha='right',va='top',fontsize=17,weight='bold')
fp.text(1,0.955,'קו הגבול במפת המנדט',ha='right',va='top',fontsize=17,weight='bold')
fp.text(1,0.918,'הערבה, מאילת עד צפון נחל הערבה',ha='right',va='top',fontsize=10,color='#444')
y=0.875; fp.text(1,y,'מקרא',ha='right',va='top',fontsize=11,weight='bold'); y-=0.035
def leg(kind,txt):
    global y
    if kind=='arm': fp.plot([0.84,0.98],[y-0.007]*2,color='#d7191c',lw=2)
    elif kind=='man': fp.plot([0.84,0.98],[y-0.007]*2,color='#1f4e9c',lw=1.6,ls=(0,(5,2)))
    else: fp.add_patch(plt.Rectangle((0.84,y-0.016),0.14,0.016,fc=kind,ec='none',alpha=.8))
    L=textwrap.wrap(txt,30)
    for k,l in enumerate(L): fp.text(0.81,y-k*0.021,l,ha='right',va='top',fontsize=8.5)
    y-=0.021*len(L)+0.014
leg('arm','קו שביתת הנשק כפי שסומן בגיליונות 1:100,000 הישראליים (1948–1958), מותאם לרשת')
leg('man','קו הגבול במפת Survey of Palestine 1:250,000, גיליון דרום (1942), שרטוט ידני')
leg('#f28e2b',f'קו שביתת הנשק ממערב לקו המנדט ({W:.0f} קמ"ר)')
leg('#59a14f',f'קו שביתת הנשק ממזרח לקו המנדט ({E_:.0f} קמ"ר)')
y-=0.01; fp.text(1,y,'ממצאים',ha='right',va='top',fontsize=11,weight='bold'); y-=0.033
txt=[f'הפער נמדד כל 100 מ\' לאורך {ok.sum()/10:.0f} ק"מ (מרחק אופקי מזרח–מערב בין שני הקווים).',
     f'פער חציוני {np.median(ad):.0f} מ\', ממוצע {ad.mean():.0f} מ\'. ב-{(ad<1000).mean()*100:.0f}% מהאורך הפער קטן מ-1 ק"מ.',
     'בדרך כלל קו שביתת הנשק עובר מעט ממערב לקו המנדט.',
     f'הפער הגדול ביותר, עד {abs(DX[i])/1000:.1f} ק"מ, בין יטבתה לקטורה: במפת המנדט הקו פונה מזרחה לעבר עין ע\'רנדל, ואילו קו שביתת הנשק נשאר במרכז העמק.',
     'באילת: קו המנדט (1942) יוצא מאום רשרש, כ-1.7 ק"מ ממערב לנקודת המוצא של קו שביתת הנשק, בהתאם לסימון הגבול ליד המפרץ ב-1946.',
     'בקטע של כ-7 ק"מ ליד פארן אין שרטוט של קו המנדט, ולכן לא נמדד שם פער.']
for t in txt:
    for l in textwrap.wrap(t,42): fp.text(1,y,l,ha='right',va='top',fontsize=8.3,color='#222'); y-=0.019
    y-=0.008
y=0.16
for s_ in ['רקע: מפת Survey of Palestine 1:250,000, גיליון דרום (הודפס 1942, נחלת הכלל, הספרייה הלאומית)','קו שביתת הנשק: Armistice_line_hist_maps_grid_ITM.gpkg','קו המנדט: Mandate_border_1942_digitized.gpkg','רשת ישראל החדשה (ITM)']:
    for l in textwrap.wrap(s_,52): fp.text(1,y,l,ha='right',va='top',fontsize=6.8,color='#444'); y-=0.015
fp.text(1,0.045,'שמעון פריש, הטכניון – עבודת דוקטורט',ha='right',va='top',fontsize=7,color='#444')
fp.text(1,0.03,'בהנחיית פרופ׳ מקסים שושני ופרופ׳ אביעד שפירא',ha='right',va='top',fontsize=7,color='#444')
fp.text(1,0.015,'© כל הזכויות שמורות',ha='right',va='top',fontsize=7,color='#444')
from shapely.geometry import Polygon
polys=[];sg=np.sign(np.where(ok,DX,0));k=0
while k<len(Y):
    if sg[k]==0: k+=1; continue
    j=k
    while j+1<len(Y) and sg[j+1]==sg[k]: j+=1
    if j>k:
        pts=list(zip(XA[k:j+1],Y[k:j+1]))+list(zip(XM[k:j+1],Y[k:j+1]))[::-1]; P=Polygon(pts).buffer(0)
        polys.append(dict(side='armistice_west_of_mandate' if sg[k]>0 else 'armistice_east_of_mandate',side_he='קו שביתת הנשק ממערב לקו המנדט' if sg[k]>0 else 'קו שביתת הנשק ממזרח לקו המנדט',y_from=Y[k],y_to=Y[j],max_gap_m=round(float(np.abs(DX[k:j+1]).max())),area_km2=round(P.area/1e6,3),geometry=P))
    k=j+1
gpd.GeoDataFrame(polys,crs=2039).to_file(OUT+'Armistice_vs_Mandate1942_gap.gpkg',layer='gap_polygons',driver='GPKG')
fig.savefig(OUT+'armistice_vs_mandate_gap.png',dpi=300); fig.savefig(OUT+'armistice_vs_mandate_gap.pdf')
