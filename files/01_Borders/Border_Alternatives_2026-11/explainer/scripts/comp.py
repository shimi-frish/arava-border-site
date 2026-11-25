exec(open('load.py').read())
import json, pandas as pd
from shapely.geometry import LineString
Ns=np.arange(385000,540001,250)
U={k:geom(g) for k,(n,g) in ALTS.items()}
def xs(u,N,ref=None):
    h=LineString([(150000,N),(300000,N)]); i=u.intersection(h)
    if i.is_empty: return np.nan
    pts=[p.x for p in getattr(i,'geoms',[i]) if p.geom_type=='Point'] or [c[0] for gg in getattr(i,'geoms',[i]) for c in gg.coords]
    if ref is None or np.isnan(ref): return np.median(pts)
    return min(pts,key=lambda x:abs(x-ref))
rows=[]
for N in Ns:
    r={'N':N}; r[6]=xs(U[6],N)
    for k in U:
        if k!=6: r[k]=xs(U[k],N,r[6])
    rows.append(r)
df=pd.DataFrame(rows); df.columns=[str(c) for c in df.columns]
df.to_csv('alts_x_per_250m.csv',index=False)
S={}
for k in ['1','2','3','4','5','7','8']:
    d=(df[k]-df['6']).dropna()
    S[k]=dict(n=len(d),median_abs_m=round(d.abs().median()),median_m=round(d.median()),p90_abs_m=round(d.abs().quantile(.9)),max_east_m=round(d.max()),max_west_m=round(d.min()),
      within500_pct=round((d.abs()<=500).mean()*100,1),
      area_east_km2=round(d.clip(lower=0).sum()*250/1e6,1), area_west_km2=round(-d.clip(upper=0).sum()*250/1e6,1))
# pairwise median abs diff
M={}
ks=[str(i) for i in range(1,9)]
for a in ks:
    M[a]={b:round((df[a]-df[b]).abs().median()) for b in ks}
json.dump({'per_alt_vs_1994':S,'pairwise_median_abs_m':M,'range_N':[385000,540000]},open('alts_compare.json','w'),ensure_ascii=False,indent=1)
for k,v in S.items(): print(k,ALTS[int(k)][0],v)
print(pd.DataFrame(M))
# by thirds
for a,b in [(385000,440000),(440000,495000),(495000,540000)]:
    sub=df[(df.N>=a)&(df.N<b)]
    print(a,b,{k:round((sub[k]-sub['6']).median()) for k in ['1','2','3','4','5','7','8']})
