# Warp the 1:2,500,000 Jordan inset to ITM (EPSG:2039) with an inverse 2nd-order polynomial from the town GCPs. 250 m pixels.
import numpy as np, json, rasterio
from rasterio.transform import from_origin
from PIL import Image
from pyproj import Transformer
SRC = '/mnt/project-files/jordan-tourist-1965/Jordan_Tourist_Maps_Rassas_1965_Jordan_inset_scan.jpg'
OUT = '/mnt/project-files/jordan-tourist-1965/georef/Rassas1965_Jordan_inset_ITM.tif'  # write locally then copy if the target is a network mount
G = json.load(open('/mnt/project-files/jordan-tourist-1965/inset_fit.json'))['gcps']
T = Transformer.from_crs(4326, 2039, always_xy=True)
px = np.array([v[:2] for v in G.values()]); xy = np.array([T.transform(v[3], v[2]) for v in G.values()])
def D(x, y): return np.stack([np.ones_like(x), x, y, x*x, x*y, y*y], -1)
s = 1e5; A = D(xy[:, 0]/s, xy[:, 1]/s)
ci, *_ = np.linalg.lstsq(A, px[:, 0], rcond=None); cj, *_ = np.linalg.lstsq(A, px[:, 1], rcond=None)
im = np.asarray(Image.open(SRC).convert('RGB')); H, W, _ = im.shape
x0, x1, y0, y1, r = 100000, 560000, 330000, 860000, 250
nx, ny = int((x1-x0)/r), int((y1-y0)/r)
X, Y = np.meshgrid(x0 + (np.arange(nx)+.5)*r, y1 - (np.arange(ny)+.5)*r)
Dg = D(X/s, Y/s); I = Dg @ ci; Jp = Dg @ cj
ok = (I >= 55) & (I < 1135) & (J := Jp, Jp >= 262)[1] & (Jp < 1475)   # inside the inset frame
Ii = np.clip(I.round().astype(int), 0, W-1); Ji = np.clip(Jp.round().astype(int), 0, H-1)
out = im[Ji, Ii].transpose(2, 0, 1).copy(); m = (ok * 255).astype('uint8')
import os; os.makedirs(os.path.dirname(OUT), exist_ok=True)
with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True):
    with rasterio.open(OUT, 'w', driver='GTiff', width=nx, height=ny, count=3, dtype='uint8', crs='EPSG:2039',
                       transform=from_origin(x0, y1, r, r), compress='JPEG', photometric='YCBCR', tiled=True) as d:
        d.write(out); d.write_mask(m)
# Note: the project copy was then rewritten as RGBA + DEFLATE (alpha = mask) because the JPEG internal mask did not survive the network copy.
print('ok', nx, ny, os.path.getsize(OUT))
