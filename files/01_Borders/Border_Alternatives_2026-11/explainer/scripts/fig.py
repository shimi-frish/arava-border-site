exec(open('load.py').read())
from bidi.algorithm import get_display as _gd
import matplotlib as _m; from matplotlib import font_manager as _fm; [_fm.fontManager.addfont('/usr/share/fonts/truetype/culmus/DavidCLM-'+x+'.otf') for x in ('Medium','Bold')]; _m.rcParams['font.family']=['David CLM','DejaVu Sans']; _m.rcParams['font.size']=11
H=lambda s:s
import pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D; from matplotlib.patches import Patch
from shapely.geometry import Point, box
df=pd.read_csv('alts9_x_per_250m.csv')
ALTS[7]=('Sharon de facto',gpd.read_file(P+'alt7_settlement/Border_alternative_7_Sharon_line_settlement.gpkg',layer='alt7_settlement_line').to_crs(2039))
ALTS['7a']=('official',gpd.read_file(P+'Border_alternative_7_Sharon_line.gpkg',layer='alt7_sharon_line').to_crs(2039))
STY={1:('#8c564b','-',1.4,H('1  קו המנדט (מפת 1942)')),2:('#1b7a3a','-',1.5,H('2  מרכז העמק, מקורות זרים (ירדניים ובין-לאומיים)')),3:('#1f5fbf','-',1.2,H('3  מרכז העמק, SRTM')),
4:('#d95f02','-',1.5,H('4  תלווג, מפות היסטוריות')),5:('#56b4e9','--',1.2,H('5  תלווג, SRTM')),6:('#dc2626','-',2.0,H('6  גבול הסכם השלום 1994')),
7:('#7b2cbf','-',1.4,H('7  קו שרון – מצב דה-פקטו בשטח')),'7a':('#e377c2','--',1.1,H('8  קו רשמי ישראלי טרם ההסכם')),8:('#111111',':',1.6,H('9  הקו הירוק (שביתת הנשק 1949)'))}
Hv=gpd.read_file(P+'Border_alternatives_2_4_historical.gpkg',layer='historical_valley_polygon').to_crs(2039)
Vv=gpd.read_file(V,layer='valley_polygon_auto_rule').to_crs(2039)
pl=[(H('אילת'),34.951,29.557,-1),(H('עקבה'),35.006,29.53,1),(H('יטבתה'),35.06,29.89,-1),(H("ע'רנדל"),35.18,30.03,1),(H('יהל'),35.13,30.06,-1),(H('פארן'),35.15,30.35,-1),(H('עין יהב'),35.23,30.65,-1),(H('ואדי פידאן'),35.37,30.65,1),(H('חצבה'),35.25,30.78,-1),(H('ים המלח'),35.42,31.08,1)]
PP=gpd.GeoSeries([Point(x,y) for _,x,y,_ in pl],crs=4326).to_crs(2039)
def draw(a,clip=None,lw=1):
    Hv.plot(ax=a,color='#efe6c8',lw=0); Vv.boundary.plot(ax=a,color='#9e9e9e',lw=.6,ls=':')
    for k in [2,3,4,5,1,8,'7a',7,6]:
        c,ls,w,l=STY[k]; g=ALTS[k][1]
        g.plot(ax=a,color=c,ls=ls,lw=w*lw,zorder=3+(k==6))
# fig 1 overview + 2 zooms
fig=plt.figure(figsize=(10.5,11))
a=fig.add_axes([0.01,0.03,0.45,0.94]); draw(a)
for (n,_,_,s),p in zip(pl,PP):
    a.plot(p.x,p.y,'ko',ms=2.5,zorder=6); a.annotate(n,(p.x,p.y),xytext=(5*s,1),textcoords='offset points',ha='left' if s>0 else 'right',fontsize=7.5,bbox=dict(fc='white',ec='none',alpha=.8,pad=.4),zorder=7)
Z=[(218000,240000,490000,522000,'B'),(205000,225000,425000,455000,'C')]
for x0,x1,y0,y1,t in Z:
    a.add_patch(plt.Rectangle((x0,y0),x1-x0,y1-y0,fill=False,ec='k',lw=.8,zorder=8)); a.text(x1+700,y1-1500,t,fontsize=10,weight='bold')
a.set_xlim(186000,252000); a.set_ylim(380000,560000); a.set_aspect('equal'); a.set_xticks([]); a.set_yticks([]); a.set_xlabel(''); a.set_ylabel(''); a.set_title(H('A  כל החלופות, מים המלח עד אילת'),fontsize=10)
a.legend(handles=[Line2D([],[],color=c,ls=ls,lw=w,label=l) for c,ls,w,l in STY.values()]+[Patch(color='#efe6c8',label=H('העמק לפי מקורות זרים')),Line2D([],[],color='#9e9e9e',ls=':',label=H('העמק הסופי (SRTM)'))],loc='lower right',fontsize=6.6,framealpha=.92)
for (x0,x1,y0,y1,t),pos in zip(Z,[[0.49,0.525,0.50,0.43],[0.49,0.03,0.50,0.43]]):
    c=fig.add_axes(pos); draw(c,lw=1.3)
    for (n,_,_,s),p in zip(pl,PP):
        if x0<p.x<x1 and y0<p.y<y1: c.plot(p.x,p.y,'ko',ms=3,zorder=6); c.annotate(n,(p.x,p.y),xytext=(5*s,1),textcoords='offset points',ha='left' if s>0 else 'right',fontsize=8,bbox=dict(fc='white',ec='none',alpha=.8,pad=.4),zorder=7)
    c.set_xlim(x0,x1); c.set_ylim(y0,y1); c.set_aspect('equal'); c.set_xticks([]); c.set_yticks([]); c.set_xlabel(''); c.set_ylabel('')
    c.add_artist(plt.Line2D([x0+1000,x0+6000],[y0+1200,y0+1200],color='k',lw=2)); c.text(x0+3500,y0+1700,H('5 ק"מ'),ha='center',fontsize=7)
    c.set_title(t+'  '+(H('עין יהב – חצבה – ואדי פידאן') if t=='B' else H("יהל – ע'רנדל – פארן (דרום)")),fontsize=9)
fig.text(.5,.008,H('מחקר לתואר דוקטור של שמעון פריש, הטכניון (מנחים: פרופ\' מקסים שושני ופרופ\' אביעד שפירא). כל הזכויות שמורות.'),ha='center',fontsize=7,color='0.4')
plt.savefig('fig1_alternatives_map.png',dpi=150)
# fig 2 offsets
fig,ax=plt.subplots(1,2,figsize=(11,8),sharey=True)
y=df.N/1000
for a,ks,t in [(ax[0],[2,3,4,5],H('חלופות גאוגרפיות (מרכז העמק / תלווג)')),(ax[1],[1,'7a',7,8],H('חלופות היסטוריות ומדיניות'))]:
    a.axvspan(-.5,.5,color='0.92'); a.axvline(0,color=STY[6][0],lw=1.5)
    for k in ks:
        c,ls,w,l=STY[k]; a.plot((df[str(k)]-df['6'])/1000,y,color=c,ls=ls if k!=8 else '-',lw=1,label=l)
    a.set_title(t,fontsize=10); a.set_xlabel(H('מרחק מגבול 1994 (ק"מ); חיובי = ממזרח לגבול (יותר שטח לישראל)')); a.grid(alpha=.3); a.legend(fontsize=8,loc='lower right',framealpha=.95)
ax[0].set_xlim(-6,10); ax[1].set_xlim(-3,7); ax[0].set_ylabel(H('צפון ITM (ק"מ): אילת (למטה) עד ים המלח (למעלה)')); ax[0].set_ylim(385,540)
for n,yy in [(H('אילת'),387),(H('יטבתה'),422.4),(H('יהל'),441.2),(H('פארן'),473.4),(H('עין יהב'),506.6),(H('חצבה'),521)]:
    ax[1].axhline(yy,color='0.6',lw=.5,ls='--'); ax[0].axhline(yy,color='0.6',lw=.5,ls='--'); ax[0].text(-5.9,yy+.6,n,fontsize=8.5,color='0.3'); (ax[1].text(6.9,yy+.6,n,ha='right',va='bottom',fontsize=7.5,color='0.3') if n!=H('אילת') else None)
fig.text(.5,.005,H('מחקר לתואר דוקטור של שמעון פריש, הטכניון (מנחים: פרופ\' מקסים שושני ופרופ\' אביעד שפירא). כל הזכויות שמורות.'),ha='center',fontsize=7,color='0.4')
plt.tight_layout(rect=(0,.015,1,1)); plt.savefig('fig2_offsets_vs_1994.png',dpi=150)
