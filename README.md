# Squadrats2Garmin tools
Squadrats2Garmin project is a set of tools that improves the experience of _Squadrats_ collectors who use Garmin bike computers and smartwatches.

## What are Squadrats?
That's right. [Explain](https://squadrats.com/explain) like I'm your grandpa, please!

## What does this project do?
It allows you to see borders of Squadrats and Squadratinhos right on your Garmin device. 
No more need to reach out for your phone to confirm a score! 

Here you can generate or download Squadrat- and Squadratinho-sized grid overlay for maps on your Garmin device.

### Supported devices
Basically all Garmin devices that can use custom maps in IMG format. That includes but is not limited to:

Bike computers:
- Edge 10x0 series
- Edge 8x0 series
- Edge 5x0 series (starting from Edge 520)

Smartwatches
- Garmin Descent
- Garmin epix
- Garmin Fenix 8, 7, 6, 5X and 5 Plus
- Garmin Forerunner 965, 945
- Garmin MARQ
- Garmin tactix

## Downloading pre-made grids
Please check [dist](dist) directory for pre-made grids.
Contact me if your country/province is missing, and you don't like playing around with commandline tools.

### How to upload pre-made grid to your Garmin device?
Upload the IMG files to your [Garmin Edge](https://www.dcrainmaker.com/2019/08/how-to-install-free-maps-on-your-garmin-edge.html) or [Garmin watch](https://www.dcrainmaker.com/2019/08/how-to-installing-free-maps-on-your-garmin-fenix-5-plus-forerunner-945-or-marq-series-watch.html)

## Generating your own grid
You can generate your own grid using this project. This will require knowledge of git, Python and bash.
```console
# install mkgmap tool
$ sudo apt install mkgmap

# clone the repository
$ git clone git@github.com:kbrazulewicz/squadrats2garmin.git
$ cd squadrats2garmin
```

Garmin compatible grids are created by running `squadrats2garmin` script with a configuration file, ie.
```console
# setup Python environment
$ python3 -m venv .venv
$ pip install -r requirements.txt

# activate Python environment
$ source .venv/bin/activate

# run the script
$ ./squadrats2garmin.sh config/PL-Polska.json
```
Read more about [configuration file format](config/README.md)  

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