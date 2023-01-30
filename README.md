## Requirements
- python 3.10
- mkgmap (sudo install mkgmap)

## Notes
### Getting the POLY file
- use https://www.openstreetmap.org/ to identify relation id of your area (ie. for województwo pomorskie it will be https://www.openstreetmap.org/relation/130975)
- use http://polygons.openstreetmap.fr/index.py?id=130975 to download the POLY file (different levels of detail are available)


### Polygon clipping
- convex polygon (wypukły)
- concave polygon (wklęsły)
- [Point in polygon](https://en.wikipedia.org/wiki/Point_in_polygon)
- [Line clipping](https://en.wikipedia.org/wiki/Line_clipping)
- [Weiler–Atherton clipping algorithm](https://en.wikipedia.org/wiki/Weiler%E2%80%93Atherton_clipping_algorithm)
- [Sutherland–Hodgman clipping algorithm](https://en.wikipedia.org/wiki/Sutherland%E2%80%93Hodgman_algorithm) (convex only)
- [Vatti clipping algorithm](https://en.wikipedia.org/wiki/Vatti_clipping_algorithm)
- [Greiner–Hormann clipping algorithm](https://en.wikipedia.org/wiki/Greiner%E2%80%93Hormann_clipping_algorithm)
