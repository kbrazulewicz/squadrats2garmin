# Polygon files
This folder contains polygon (boundaries) files for different countries and their subdivisions. Region boundaries are used to generate maps containing grid.

## How to add a new region
### Using built-in tool
1. Run `python3 bin/poly_download.py` and pass ISO codes for the regions to download (ie. `python3 bin/poly_download.py PL ES-CA`). 
2. Polygon files will be saved as `{iso code}-{name}.poly` in the current working directory (ie. `PL-22-Pomorskie.poly`).
3. Finally move them to the appropriate folder (ie. `europe/PL-Polska/PL-22-Pomorskie.poly`).

### Manually (country)
1. Find out the [ISO 3166-1](https://en.wikipedia.org/wiki/ISO_3166-1) alpha-2 code of the country. 
2. Search for the country code in the openstreetmap.org database (ie. `PL` for [Poland](https://www.openstreetmap.org/search?query=PL))
3. Copy the relation id (ie. `49715` for [Poland](https://www.openstreetmap.org/relation/49715)).
4. Enter the relation id on the https://polygons.openstreetmap.fr website and download the POLY file. 
5. Rename the downloaded file `{alpha-2 code}-{description}.poly` (ie. `PL-Polska.poly`)
6. For convenience move the POLY file to the appropriate continent folder (ie. `europe/PL-Polska.poly`)

### Manually (subdivision)
1. Locate the [list of subdivisions](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) for the country (ie. [Poland](https://en.wikipedia.org/wiki/ISO_3166-2:PL))
2. Search for the subdivision code in the openstreetmap.org database (ie. `PL-22` for [Pomeranian Voivodeship](https://www.openstreetmap.org/search?query=PL-22))
3. Copy the relation id of the subdivision (ie. `130975` for [Pomeranian Voivodeship](https://www.openstreetmap.org/relation/130975))
4. Enter the relation id on the https://polygons.openstreetmap.fr website and download the POLY file. 
5. Rename the downloaded file `{subdivision code}-{description}.poly` (ie. `PL-22-Pomorskie.poly`).
6. For convenience move the POLY file to the appropriate country folder (ie. `europe/PL-Polska/PL-22-Pomorskie.poly`).