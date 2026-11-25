import numpy as np,geopandas as gpd,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
L='/tmp/claude-0/ls/'; U='/mnt/user-data/uploads/Israel-Jordan-Arava/'; DL='/mnt/user-data/uploads/Downloads/'
F=gpd.read_file(L+'alt7_new.gpkg',layer='fields')
b94=gpd.read_file('/tmp/claude-0/alts/Gvul_Nayad.gpkg',layer='גבול יפית 2012').to_crs(2039)
arm=gpd.read_file(U+'01_Borders/Armistice_line_hist_maps_grid_ITM.gpkg').to_crs(2039)
JN={41:1,72:2,39:3,54:4,79:5,81:6,89:7,96:8,95:9,100:10,284:11,289:12,306:13,307:14}
NAT={72,79,81,89,96,100}
IMG={'A':'road_A_194500_382500_202500_393500_2909x4000.jpg','B':'roadv2_B_204000_419500_210500_432500_2000x4000.jpg',
'D':'roadv2_D_219000_491000_226500_498500_3000x3000.jpg','E':'roadv2_E_220000_504000_230500_516500_3360x4000.jpg',
'F':'roadv2_F_226500_517500_233500_526500_2800x3600.jpg','G':'roadv3_G_233500_532500_245500_543500_4000x3667.jpg'}
W='#ffd400'; E='#00e5ff'
P=[('G','(a) Neot Hakikar (G) and Ghor Fifa (H)',[235500,535300,243700,541800],
    [((235900,539700),(237300,539300),W,'from W\n(Neot Hakikar)'),((243500,539900),(242600,539400),E,'from E\n(Ghor Fifa)'),((241900,536900),(240150,536450),E,'from E')],
    [((238200,535600),'7, 8, 10: no road, natural vegetation'),((239000,538900),'2, 5, 6: natural\nvegetation')]),
   ('D','(b) Zofar enclave (D)',[219000,493000,225500,497000],
    [((219500,495900),(221700,495300),W,'1990s access\nfrom Israel (gate)'),((225300,496300),(223600,495200),E,'link to Jordan\nhighway (today)')],[]),
   ('E','(c) Ein Yahav, plots east of the channel (E)',[226000,512600,229500,515400],
    [((226300,514900),(227300,513850),W,'track from W\nacross the channel')],[]),
   ('F','(d) Hatzeva (F)',[226800,518500,233200,525000],
    [((226900,519600),(228300,519400),W,'from W'),((227600,524900),(229000,523700),W,'from W')],[]),
   ('B','(e) Yotvata (B)',[204500,420200,210300,432000],
    [((204700,425300),(206300,425200),W,'from W'),((204700,421300),(206500,421500),W,'from W'),((204700,428600),(206300,428300),W,'from W')],[]),
   ('A','(f) Eilat and Aqaba (A, I)',[195200,383300,202000,392000],
    [((195800,387200),(197000,386500),W,'from W\n(Eilat)'),((201600,385400),(199600,386500),E,'from E\n(Aqaba streets)'),((196300,391300),(198700,390400),W,'from W')],[])]
import time;T0=time.time()
fig,axs=plt.subplots(2,3,figsize=(16,13.5))
for a,(k,t,bb,arrows,notes) in zip(axs.flat,P):
    fn=IMG[k]; p=fn.split('_'); b=list(map(float,p[2:6]))
    a.imshow(np.asarray(Image.open(DL+fn)),extent=[b[0],b[2],b[1],b[3]])
    from shapely.geometry import box; bx=box(*bb).buffer(200)
    for G_,c_,l_ in ((b94,'magenta','--'),(arm,'#7CFC00',':')):
        for gg in G_.geometry.intersection(bx):
            for ln in getattr(gg,'geoms',[gg]):
                if not ln.is_empty: xx,yy=ln.xy; a.plot(xx,yy,color=c_,lw=1.3,ls=l_)
    for _,r in F.iterrows():
        g=r.geometry
        if r.kind=='israeli': c,ls='orange','-'
        elif r.kind=='zofar_enclave': c,ls='red','-'
        elif r.id in NAT: c,ls='white','--'
        else: c,ls='cyan','-'
        if not g.intersects(box(*bb)): continue
        for poly in getattr(g,'geoms',[g]):
            x,y=poly.exterior.xy; a.plot(x,y,color=c,lw=1.3,ls=ls)
        q=g.representative_point()
        if r.id in JN and r.kind!='israeli' and bb[0]<q.x<bb[2] and bb[1]<q.y<bb[3]:
            a.annotate(str(JN[r.id]),(q.x,q.y),xytext=(7,7),textcoords='offset points',color=c,fontsize=9,weight='bold',
                       bbox=dict(boxstyle='round,pad=0.15',fc='black',alpha=.55,lw=0))
    for (s,e,c,lab) in arrows:
        a.annotate('',xy=e,xytext=s,arrowprops=dict(arrowstyle='-|>',color=c,lw=2.4,mutation_scale=18))
        a.text(s[0],s[1],lab,color='black',fontsize=8,ha='left',va='center',bbox=dict(boxstyle='round,pad=0.2',fc=c,alpha=.85,lw=0))
    for (xy,lab) in notes:
        a.text(xy[0],xy[1],lab,fontsize=8,color='black',ha='left',va='center',bbox=dict(boxstyle='round,pad=0.2',fc='white',alpha=.85,lw=0))
    dx=bb[2]-bb[0]; sb=1000 if dx>4000 else 500
    x0=bb[0]+dx*.05; y0=bb[1]+(bb[3]-bb[1])*.04
    a.plot([x0,x0+sb],[y0,y0],color='white',lw=3); a.text(x0+sb/2,y0+(bb[3]-bb[1])*.02,f'{sb/1000:g} km',color='white',ha='center',fontsize=8,weight='bold')
    print(k,time.time()-T0,flush=True)
    a.set_xlim(bb[0],bb[2]); a.set_ylim(bb[1],bb[3]); a.set_xticks([]); a.set_yticks([]); a.set_title(t,fontsize=11)
fig.legend(handles=[Line2D([],[],color='magenta',ls='--',label='1994 treaty border'),Line2D([],[],color='#7CFC00',ls=':',label='1949 armistice line'),
 Line2D([],[],color='orange',label='Israeli fields east of armistice line'),Line2D([],[],color='red',label='Zofar enclave fields'),
 Line2D([],[],color='cyan',label='Jordanian fields (confirmed by road access)'),Line2D([],[],color='white',ls='--',label='Reclassified: natural vegetation, no road'),
 Line2D([],[],color=W,lw=3,label='Access from the west'),Line2D([],[],color=E,lw=3,label='Access from the east')],loc='lower center',bbox_to_anchor=(.5,.022),ncol=4,fontsize=9,facecolor='#555',labelcolor='white')
fig.text(.5,.005,'Imagery: Esri World Imagery (current); field outlines: Landsat 5 NDVI 1987-1994. PhD research of Shimon Frish, Technion (supervisors Prof. Maxim Shoshany, Prof. Aviad Shapira). All rights reserved.',ha='center',fontsize=7.5,color='.3')
plt.tight_layout(rect=[0,.075,1,1]); fig.savefig('road_access_test.png',dpi=130)
