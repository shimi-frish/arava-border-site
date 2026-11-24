# Georeference Jordan 1:2,500,000 inset of Rassas 1965 tourist map by town positions; poly-1/poly-2 fit to ITM.
import numpy as np, json
from pyproj import Transformer
T = Transformer.from_crs(4326, 2039, always_xy=True)
G = {  # name: (px x, px y, lat, lon)
 'Jerusalem': (170, 730, 31.776, 35.234), 'Amman': (307.5, 709, 31.951, 35.934), 'Irbid': (304, 497, 32.556, 35.850),
 "Dera'a": (360.6, 495.6, 32.618, 36.102), 'Mafraq': (400, 577, 32.342, 36.208), 'Umm el Jimal': (470, 595, 32.327, 36.370),
 'Karak': (250, 906, 31.181, 35.702), 'Qatrana': (342.5, 903, 31.247, 36.046), 'Qasr Amra': (466, 746.5, 31.802, 36.586),
 'Qasr Kharana': (460, 769.5, 31.729, 36.463), 'Azraq': (536.7, 727, 31.879, 36.829), 'Qasr et Tuba': (501, 867, 31.317, 36.570),
 'Bayir': (508, 1039, 30.766, 36.677), 'El Jafr': (384, 1172, 30.324, 36.192), "Ma'an": (243.8, 1193.8, 30.196, 35.736),
 'Wadi Musa': (190.6, 1173, 30.322, 35.479), 'Petra': (171.9, 1168.8, 30.329, 35.441), 'Shaubak': (212.5, 1092.5, 30.531, 35.561),
 'Tafila': (235.6, 1008.8, 30.837, 35.604), "Mu'tah": (252, 935.6, 31.083, 35.700), 'Ras en Naqab': (206, 1253, 30.000, 35.494),
 'Quweira': (171.9, 1309, 29.802, 35.314), 'Rum': (181, 1367.5, 29.578, 35.420), 'Aqaba': (73.8, 1385, 29.527, 35.004),
 'Umm Qais': (255, 478, 32.656, 35.681), 'Mudawwara': (322, 1455, 29.322, 35.995)}
n = list(G); px = np.array([[G[k][0], G[k][1]] for k in n]); xy = np.array([T.transform(G[k][3], G[k][2]) for k in n])
def design(p, o):
    x, y = p[:, 0], p[:, 1]
    cols = [np.ones_like(x), x, y] + ([x*x, x*y, y*y] if o == 2 else [])
    return np.stack(cols, 1)
res = {}
for o in (1, 2):
    A = design(px, o); cx, *_ = np.linalg.lstsq(A, xy[:, 0], rcond=None); cy, *_ = np.linalg.lstsq(A, xy[:, 1], rcond=None)
    r = np.hypot(A @ cx - xy[:, 0], A @ cy - xy[:, 1]); res[o] = (cx, cy, r)
    print('poly', o, 'RMS km %.2f' % (np.sqrt((r**2).mean())/1000), 'max', n[r.argmax()], '%.1f' % (r.max()/1000))
for k, rr in sorted(zip(n, res[1][2]), key=lambda t: -t[1])[:8]: print('  ', k, '%.1f km' % (rr/1000))
json.dump({'gcps': G, 'poly1': [list(res[1][0]), list(res[1][1])], 'poly2': [list(res[2][0]), list(res[2][1])]}, open('/mnt/project-files/jordan-tourist-1965/inset_fit.json', 'w'), ensure_ascii=False, indent=0)
