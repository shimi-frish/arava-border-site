import geopandas as gpd, numpy as np
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge
U='/mnt/user-data/uploads/Israel-Jordan-Arava/'
P='/mnt/project-files/border-alternatives/'
V='/mnt/project-files/valley-final/Arava_valley_final_2026-11-17.gpkg'
def rd(f,l): return gpd.read_file(f,layer=l).to_crs(2039)
ALTS={
1:('קו המנדט (מפת 1942, גיליון דרום)',rd(U+'01_Borders/Mandate_border_1942_digitized.gpkg','Mandate_border_1942_digitized')),
2:('מרכז העמק לפי מפות היסטוריות',rd(P+'Border_alternatives_2_4_historical.gpkg','alt2_historical_centre_line')),
3:('מרכז העמק לפי SRTM',rd(V,'valley_centre_line')),
4:('תלווג לפי מפות היסטוריות',rd(P+'Border_alternatives_2_4_historical.gpkg','alt4_historical_thalweg_line')),
5:('תלווג לפי SRTM',rd(V,'thalweg_line')),
6:('גבול הסכם השלום 1994',rd('Gvul_Nayad.gpkg','גבול יפית 2012')),
7:('קו שרון (הקו בפועל, שנות ה-80–90)',rd(P+'Border_alternative_7_Sharon_line.gpkg','alt7_sharon_line')),
8:('הקו הירוק – קו שביתת הנשק 1949',rd(U+'01_Borders/Armistice_line_hist_maps_grid_ITM.gpkg','Armistice_line_hist_maps_grid_ITM')),
}
def geom(g): 
    u=g.geometry.union_all()
    return u
