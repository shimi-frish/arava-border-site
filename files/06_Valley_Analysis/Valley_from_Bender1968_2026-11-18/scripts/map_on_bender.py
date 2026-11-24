import pickle, numpy as np, geopandas as gpd, rasterio, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import patheffects as pe
from rasterio.windows import from_bounds
plt.rcParams['font.family']=['Noto Sans Hebrew','DejaVu Sans']
OUT='/mnt/project-files/valley-from-bender1968/'
P=gpd.read_file(OUT+'Arava_valley_from_Bender1968.gpkg',layer='valley_polygon_bender1968').geometry.iloc[0]
def u(lo,la): q=gpd.GeoSeries(gpd.points_from_xy([lo],[la]),crs=4326).to_crs(2039).iloc[0]; return q.x,q.y
PL=[('אילת',34.951,29.557,'w'),('עקבה',35.006,29.532,'e'),('יטבתה',35.062,29.887,'w'),('פארן',35.151,30.356,'w'),
 ('ספיר',35.187,30.617,'w'),('חצבה',35.255,30.783,'w'),('נאות הכיכר',35.373,30.932,'w'),('פינאן',35.493,30.627,'e'),('עין ע\'רנדל',35.177,30.090,'e')]
PAN=[(186000,232000,378000,470000),(208000,254000,468000,560000)]
fig=plt.figure(figsize=(16.54,11.69))  # A3 landscape
H=0.90; W=H*11.69*46/92/16.54
for k,(x0,x1,y0,y1) in enumerate(PAN):
    ax=fig.add_axes([0.975-(k+1)*W-k*0.02,0.035,W,H])
    for f,ya,yb in [('Aqaba-Maan',y0,min(y1,546400)),('Amman',max(y0,546400),y1)]:
        if yb<=ya: continue
        r=rasterio.open(f'/mnt/project-files/jordan-geology/Bender1968_250k_{f}_ITM.tif')
        img=r.read(window=from_bounds(x0,ya,x1,yb,r.transform),boundless=True,fill_value=255).transpose(1,2,0)
        ax.imshow(img,extent=(x0,x1,ya,yb),interpolation='bilinear',zorder=1)
    for g in getattr(P,'geoms',[P]):
        for ring in [g.exterior]+list(g.interiors):
            x,y=ring.xy; ax.plot(x,y,color='white',lw=3.6,zorder=5); ax.plot(x,y,color='#e0007a',lw=1.8,zorder=6)
    for n,lo,la,s in PL:
        x,y=u(lo,la)
        if not (x0<x<x1 and y0<y<y1): continue
        ax.plot(x,y,'o',ms=4,mfc='white',mec='#111',mew=1,zorder=32)
        ax.text(x+(-700 if s=='w' else 700),y,n,ha='right' if s=='w' else 'left',va='center',fontsize=9,weight='bold',zorder=31,path_effects=[pe.withStroke(linewidth=3,foreground='white')])
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(['חלק דרומי: אילת – פארן','חלק צפוני: פארן – בריכות ים המלח'][k],fontsize=12,weight='bold')
    sx,sy=x1-14000,y0+2500
    for i in range(2): ax.add_patch(plt.Rectangle((sx+i*5000,sy),5000,450,fc='k' if i%2==0 else 'w',ec='k',lw=.6,zorder=40))
    for i in (0,1,2): ax.text(sx+i*5000,sy+1100,str(i*5),ha='center',fontsize=8,zorder=40,path_effects=[pe.withStroke(linewidth=2,foreground='white')])
    ax.text(sx-600,sy+225,'ק"מ',ha='right',va='center',fontsize=8,zorder=40,path_effects=[pe.withStroke(linewidth=2,foreground='white')])
    ax.annotate('',xy=(x0+2500,y1-2000),xytext=(x0+2500,y1-7000),arrowprops=dict(arrowstyle='-|>',lw=2,color='k'),zorder=40)
    ax.text(x0+2500,y1-1700,'N',ha='center',va='bottom',fontsize=11,weight='bold',zorder=40,path_effects=[pe.withStroke(linewidth=2,foreground='white')])
fp=fig.add_axes([0.015,0.03,0.975-2*W-0.04,0.94]); fp.axis('off'); fp.set_xlim(0,1); fp.set_ylim(0,1)
import textwrap
fp.text(1,0.99,'עמק הערבה',ha='right',va='top',fontsize=18,weight='bold')
fp.text(1,0.955,'על רקע מפת Bender 1968',ha='right',va='top',fontsize=13,weight='bold')
y=0.90; fp.plot([0.80,0.98],[y]*2,color='#e0007a',lw=2.4)
for i,l in enumerate(textwrap.wrap(f'העמק כפי שנקלט מהמפה, {P.area/1e6:,.0f} קמ"ר',30)): fp.text(0.76,y+0.008-i*0.022,l,ha='right',va='top',fontsize=9.5)
y=0.84; fp.text(1,y,'יחידות העמק במקרא של Bender:',ha='right',va='top',fontsize=9.5,weight='bold'); y-=0.03
for t in ['סחף נחלים וּואדיות, חול (q5)','משקעי בוץ בשטחי הצפה (q4)','מניפות ומדרוני טאלוס (q3)','חצץ נחלי פלייסטוקני (q2 עם עיגולים)','חוואר הלשון (q2)']:
    for l in textwrap.wrap(t,40): fp.text(1,y,l,ha='right',va='top',fontsize=8.8); y-=0.022
    y-=0.006
y=0.14
for s_ in ["F. Bender et al. 1968, Geologische Karte von Jordanien 1:250,000, Blätter Aqaba–Ma'an, Amman. BfB Hannover. סריקה: הספרייה הלאומית של אוסטרליה. לשימוש מחקרי."]:
    for l in textwrap.wrap(s_,46): fp.text(1,y,l,ha='right',va='top',fontsize=7,color='#444'); y-=0.016
fp.text(1,0.045,'שמעון פריש, הטכניון – עבודת דוקטורט',ha='right',va='top',fontsize=7.5,color='#444')
fp.text(1,0.03,'בהנחיית פרופ׳ מקסים שושני ופרופ׳ אביעד שפירא',ha='right',va='top',fontsize=7.5,color='#444')
fp.text(1,0.015,'© כל הזכויות שמורות',ha='right',va='top',fontsize=7.5,color='#444')
fig.savefig(OUT+'valley_on_bender1968_A3.png',dpi=250); fig.savefig(OUT+'valley_on_bender1968_A3.pdf')
print(H)
