# Per cross-section (250 m): distance from the valley centre to the first GMBA-v2 mountain cell, east and west,
# compared with the distance to the final valley edge. + = GMBA mountain starts outside our edge (valley wider).
import numpy as np, geopandas as gpd, json
from shapely.geometry import Point
FV = '/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
X = gpd.read_file(FV, layer='cross_sections_250m')
C = gpd.read_file(FV, layer='valley_centre_points').set_index('section')
M = gpd.read_file('/mnt/project-files/gmba-test/GMBA_def_v2_Arava.gpkg').to_crs(32636).geometry.iloc[1]
from shapely.prepared import prep; Mp = prep(M)
rows = []
for _, r in X.iterrows():
    L0 = r.geometry; c = C.loc[r.section].geometry
    a, b = np.array(L0.coords[0]), np.array(L0.coords[-1]); u = (b - a) / np.linalg.norm(b - a)
    if u[0] < 0: u = -u   # u points east
    from shapely.geometry import LineString
    L = LineString([tuple(np.array(c.coords[0]) - 25000*u), tuple(np.array(c.coords[0]) + 25000*u)]); t0 = 25000.0; east_sign = 1
    out = {'section': int(r.section), 's_km': r.s_km}
    for side, sg, edge in (('E', east_sign, r.centre_off_km - r.east_edge_off_km), ('W', -east_sign, r.west_edge_off_km - r.centre_off_km)):
        d = None
        for s in np.arange(0, 25000, 60):
            t = t0 + sg * s
            if t < 0 or t > L.length: break
            if Mp.contains(L.interpolate(t)): d = s / 1000; break
        out[side + '_gmba_km'] = d; out[side + '_edge_km'] = edge
        out[side + '_diff_km'] = None if d is None else round(d - edge, 3)
    rows.append(out)
import pandas as pd
D = pd.DataFrame(rows); D.to_csv('/mnt/project-files/gmba-test/gmba_edges_per_section.csv', index=False)
res = {}
for s in 'EW':
    v = D[s + '_diff_km'].dropna()
    res[s] = {'n': int(len(v)), 'of': len(D), 'median_km': round(v.median(), 2), 'within_1km_pct': round(100*(v.abs() <= 1).mean(), 1),
              'within_2km_pct': round(100*(v.abs() <= 2).mean(), 1), 'outside_pct': round(100*(v > 0).mean(), 1)}
print(res); json.dump(res, open('/mnt/project-files/gmba-test/gmba_edges_summary.json', 'w'), indent=1)
