# Squadrats2Garmin tools
Squadrats2Garmin project is a set of tools that improves experience of _squadrats_ collectors using Garmin bike computers and smartwatches.

## What are Squadrats?
That's right. [Explain](https://squadrats.com/explain) like I'm your grandpa, please!

## What does this project do?
It allows you to see borders of squadrats and squadratinhos right on your Garmin device. 
No more need to reach out for your phone to confirm a score! 

Here you can generate or [download](dist/README.md) a transparent, squadrat- or squadratinho-sized grid overlay for maps on your Garmin device.

### Supported devices
Basically all Garmin devices which can use custom maps in IMG format. That includes but is not limited to:

Bike computers:
- Edge 10x0 series
- Edge 8x0 series
- Edge 5x0 series (starting from Edge 520)

Smartwatches
- Garmin Descent
- Garmin epix
- Garmin Fenix 7, 6, 5X and 5 Plus
- Garmin Forerunner 965, 945
- Garmin MARQ
- Garmin tactix

## Downloading pre-made grids
Please check [dist](dist) directory for pre-made grids.
Contact me if your country/province is missing, and you don't like playing around with command line tools.

### How to upload pre-made grid to your Garmin device?

1. Upload chosen area(s) to your [Garmin Edge](https://www.dcrainmaker.com/2019/08/how-to-install-free-maps-on-your-garmin-edge.html) or [Garmin watch](https://www.dcrainmaker.com/2019/08/how-to-installing-free-maps-on-your-garmin-fenix-5-plus-forerunner-945-or-marq-series-watch.html)
2. Enable _Draw Contours_ option in the _Map_ menu:
    - on [Edge 830](https://www8.garmin.com/manuals/webhelp/edge830/EN-US/GUID-2ADCD0D5-D5CB-4C29-9ACB-EE8BA1FDCC64.html)
    - on [Fenix 5 Plus/5X](https://www8.garmin.com/manuals/webhelp/fenix5plus/EN-US/GUID-60C3B7A5-51ED-4E4D-A2DC-8578234EF279.html)
    - on [Fenix 6 Pro](https://www8.garmin.com/manuals/webhelp/fenix66s6xpro/EN-US/GUID-1EC71AD3-CBE2-47A6-9759-B3188923C7BF.html)

## Generating your own grid
Garmin compatible grids are created by running `squadrats2garmin` script with a configuration file, ie.
```console
$ ./squadrats2garmin.sh config/france.json
```
The configuration file can define multiple jobs, each of them generating a Garmin-compatible IMG file. 
Read more about [configuration file format](config/README.md)  

### Requirements
- bash-compatible shell
- python 3.10
- mkgmap (sudo install mkgmap)

<!--
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
-->