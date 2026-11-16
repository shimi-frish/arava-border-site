# חבילת QGIS בסגנון OSM-like

החבילה נוצרה עבור הקובץ העדכני:
`merged_osm_layers_deduplicated(1).geojson`

## קבצים מרכזיים

- `current_merged_osm_with_style_class.geojson` — הקובץ המאוחד עם שדות סגנון.
- `current_osm_polygons_with_style_class.geojson` — שכבת פוליגונים.
- `current_osm_lines_with_style_class.geojson` — שכבת קווים.
- `current_osm_points_with_style_class.geojson` — שכבת נקודות.
- `current_osm_polygons_osm_like_style.qml` — סגנון לפוליגונים.
- `current_osm_lines_osm_like_style.qml` — סגנון לקווים.
- `current_osm_points_osm_like_style.qml` — סגנון לנקודות.

## איך להשתמש ב-QGIS

1. טען את שלוש השכבות המפוצלות:
   - פוליגונים
   - קווים
   - נקודות

2. לכל שכבה טען את קובץ ה-QML המתאים:
   Layer Properties → Symbology → Style → Load Style → From File

3. סדר שכבות מומלץ:
   - פוליגונים למטה
   - קווים מעליהם
   - נקודות מעל הכול

## הערה

הסימבולוגיה מבוססת על שדה `style_class`, שנוצר מתוך תגיות OSM כגון:
`building`, `highway`, `landuse`, `natural`, `place`, `power`, `man_made`.
