#### [🇵🇱 po polsku](README.pl-PL.MD)
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

Handheld devices:
- GPSMAP 62, 65

Smartwatches
- Garmin Descent
- Garmin Enduro
- Garmin epix
- Garmin Fenix 8, 7, 6, 5X and 5 Plus
- Garmin Forerunner 965, 945
- Garmin MARQ
- Garmin tactix

## Pre-made grids
Please check [dist](dist) directory for pre-made grids. Use the [instructions](dist/README.md) and go explore!

Contact me if your country/province is missing.

## Generating your own grid
You can generate your own grid using this project. 
This will require knowledge of `git`, `Python` `bash` and access to a Linux or macOS computer. 
```shell
# install mkgmap tool
$ sudo apt install mkgmap

# clone the repository
$ git clone git@github.com:kbrazulewicz/squadrats2garmin.git
$ cd squadrats2garmin

# setup Python environment
$ python3 -m venv .venv
$ pip install -r requirements.txt

# activate Python environment
$ source .venv/bin/activate
```

Garmin-compatible grids are created by running `squadrats2garmin` script, passing a configuration file as an argument, ie.
```shell
# run the script
$ ./squadrats2garmin.sh config/PL-Polska.json
```
Read more about [configuration file format](config/README.md)  

## FAQ

### Can I see the collected Squadrats?
No. At the moment you are able to see the Squadrats grid without the information about the collected ones.

### How do I use the generated grids?
You can use them on your Garmin device by following the [instructions](dist/README.md).

### How do I generate my own grids?
See [generating your own grid](#generating-your-own-grid) section.

### How do I display the grid in a different color?
To change the default colors you need to generate a custom grid.
- see [generating your own grid](#generating-your-own-grid) section for details how to generate your own grid
- see `typ/squadrats.typ.txt` file for customization options
  - `Type=0x11400` - Squadratinhos grid
  - `Type=0x11410` - Squadrats grid (zoomed out)
  - `Type=0x11411` - Squadrats grid (zoomed in)

### How do I contact you?
Create a new [issue](https://github.com/kbrazulewicz/squadrats2garmin/issues) in this project.

### How can I support you?
Buy me a coffee:

<a href="https://buycoffee.to/cykloprzygoda" target="_blank"><img src="https://buycoffee.to/img/share-button-primary.png" style="width: 156px; height: 40px" alt="Postaw mi kawę na buycoffee.to"></a>