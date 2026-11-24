# Apply the GMBA Definition v2.0 algorithm (Snethlage et al. 2022, Sci Data 9:149, step iii) to the Arava,
# then take the non-mountain corridor between Dead Sea and Gulf as "the valley" and compare it with the final valley.
# DEM: Copernicus GLO-30 (60 m, UTM36) aggregated by block median to 240 m (GMBA used GMTED2010 7.5" median, ~250 m).
import numpy as np, rasterio, geopandas as gpd, rasterio.features as rf, json
from scipy import ndimage as ndi
from shapely.geometry import shape
from shapely.ops import unary_union
OUT = '/mnt/project-files/gmba-test/'
src = rasterio.open('/mnt/project-files/non-israeli-maps/Copernicus_DEM_GLO30_Arava_60m_UTM36.tif')
z = src.read(1).astype('float32'); z[z == src.nodata] = np.nan
k = 4; H, W = (z.shape[0]//k)*k, (z.shape[1]//k)*k
zb = np.nanmedian(z[:H, :W].reshape(H//k, k, W//k, k).transpose(0, 2, 1, 3).reshape(H//k, W//k, k*k), axis=2)
T = src.transform * src.transform.scale(k, k); px = abs(T.a)
fill = np.where(np.isnan(zb), np.nanmean(zb), zb)
NAW = [(1, 3), (2, 12), (4, 78), (6, 126), (8, 184), (10, 279), (15, 352), (20, 404)]  # (radius px, min elevation range m)
mount = np.ones(zb.shape, bool)
for r, thr in NAW:
    yy, xx = np.mgrid[-r:r+1, -r:r+1]; fp = (xx**2 + yy**2) <= r*r
    rug = ndi.maximum_filter(fill, footprint=fp) - ndi.minimum_filter(fill, footprint=fp)
    mount &= rug >= thr
for _ in range(3):  # majority filter 3x3, three times
    mount = ndi.uniform_filter(mount.astype(float), 3) > 0.5
# inner flat areas < 100 km2 are part of the mountains
lab, n = ndi.label(~mount); sz = ndi.sum(np.ones_like(lab), lab, range(1, n+1)) * px * px
mount |= np.isin(lab, np.where(sz < 100e6)[0] + 1)
mount &= ~np.isnan(zb)
# valley = non-mountain components touching the straight Dead Sea - Eilat line, within 20 km of it (as for the geology maps)
FV = '/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
S = gpd.read_file(FV, layer='straight_line').to_crs(32636).geometry.iloc[0]
v = ~mount & ~np.isnan(zb) & rf.rasterize([(S.buffer(20000), 1)], out_shape=zb.shape, transform=T).astype(bool)
L, n = ndi.label(v); on = rf.rasterize([(S, 1)], out_shape=zb.shape, transform=T, all_touched=True).astype(bool)
keep = [i for i in np.unique(L[on & (L > 0)]) if i > 0]; v = np.isin(L, keep)
P = unary_union([shape(g) for g, _ in rf.shapes(v.astype('uint8'), mask=v, transform=T)]).simplify(30)
F = gpd.read_file(FV, layer='valley_polygon_auto_rule').to_crs(32636).geometry.union_all()
iou = P.intersection(F).area / P.union(F).area
res = {'gmba_valley_km2': round(P.area/1e6, 1), 'final_km2': round(F.area/1e6, 1), 'IoU': round(iou, 3),
       'final_inside_gmba_pct': round(100*P.intersection(F).area/F.area, 1), 'gmba_inside_final_pct': round(100*P.intersection(F).area/P.area, 1)}
print(res); json.dump(res, open(OUT + 'gmba_vs_final.json', 'w'), indent=1)
M = unary_union([shape(g) for g, _ in rf.shapes(mount.astype('uint8'), mask=mount, transform=T)]).simplify(30)
gpd.GeoDataFrame({'name': ['עמק לפי הגדרת ההרים של GMBA (v2.0, הוחלה על Copernicus)', 'הרים לפי הגדרת GMBA v2.0 (Copernicus 240 מ\')']},
                 geometry=[P, M], crs=32636).to_crs(2039).to_file(OUT + 'GMBA_def_v2_Arava.gpkg', driver='GPKG')
np.save('/tmp/claude-0/gmba_mount.npy', mount); json.dump(list(T)[:6], open('/tmp/claude-0/gmba_T.json', 'w'))
