# Local (south) affine fit, project the map's dashed Wadi Araba border line + Gharandal to ITM, compare with 1994 border.
import numpy as np, json, geopandas as gpd
from shapely.geometry import LineString, Point
from pyproj import Transformer
J = json.load(open('/mnt/project-files/jordan-tourist-1965/inset_fit.json')); G = J['gcps']
T = Transformer.from_crs(4326, 2039, always_xy=True)
S = ['Aqaba', 'Rum', 'Quweira', 'Ras en Naqab', 'Petra', 'Wadi Musa', "Ma'an", 'Shaubak', 'Tafila', "Mu'tah", 'Karak', 'El Jafr', 'Mudawwara']
px = np.array([G[k][:2] for k in S]); xy = np.array([T.transform(G[k][3], G[k][2]) for k in S])
A = np.c_[np.ones(len(S)), px]; cx, *_ = np.linalg.lstsq(A, xy[:, 0], rcond=None); cy, *_ = np.linalg.lstsq(A, xy[:, 1], rcond=None)
r = np.hypot(A @ cx - xy[:, 0], A @ cy - xy[:, 1]); print('south affine RMS %.2f km, max %.1f (%s)' % (np.sqrt((r**2).mean())/1e3, r.max()/1e3, S[r.argmax()]))
f = lambda p: (cx[0] + cx[1]*p[0] + cx[2]*p[1], cy[0] + cy[1]*p[0] + cy[2]*p[1])
# dashed border as read on the scan (px), Dead Sea south end -> Aqaba
B = [(176, 941), (162.7, 1000), (149, 1036), (135.5, 1082), (122, 1127), (112.7, 1173), (110.5, 1214), (99, 1250), (90, 1286), (83, 1323), (76, 1359), (74, 1382)]
L = LineString([f(p) for p in B])
lab = LineString([f(p) for p in [(108, 1173), (145, 1036)]])  # "Wadi Araba" label baseline
b94 = gpd.read_file('/mnt/project-files/border-map/border1994.geojson').to_crs(2039).geometry.union_all()
d = [b94.distance(L.interpolate(t, normalized=True)) for t in np.linspace(0, 1, 101)]
# signed: + = map line east of 1994 border (by x at same northing)
sg = []
for t in np.linspace(0, 1, 101):
    p = L.interpolate(t, normalized=True); q = b94.interpolate(b94.project(p)); sg.append((p.x - q.x) / 1e3)
sg = np.array(sg); print('map border vs 1994: median |d| %.1f km, p90 %.1f, max %.1f; signed median %.1f km (+ = east)' % (np.median(d)/1e3, np.percentile(d, 90)/1e3, max(d)/1e3, np.median(sg)))
print('label vs 1994 median %.1f km' % (np.median([b94.distance(lab.interpolate(t, normalized=True)) for t in np.linspace(0, 1, 21)])/1e3))
g = Point(f((112, 1208))); print('Gharandal on map ->', round(g.x), round(g.y))
gpd.GeoDataFrame({'name': ['גבול ירדן בערבה לפי מפת התיירות של רסאס 1965 (1:2,500,000)', 'מיקום הכיתוב Wadi Araba'], 'geometry': [L, lab]}, crs=2039).to_file('/mnt/project-files/jordan-tourist-1965/Rassas1965_Arava_border.gpkg', driver='GPKG')
json.dump({'south_affine': [list(cx), list(cy)], 'rms_km': float(np.sqrt((r**2).mean())/1e3)}, open('/mnt/project-files/jordan-tourist-1965/south_fit.json', 'w'))
