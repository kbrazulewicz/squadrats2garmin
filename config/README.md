# Configuring jobs for squadrats2garmin

Generating a Garmin IMG file with Squadrats grid is a two-phase process.

## Generate OSM XML files
The `squadrats2garmin` script invokes the `squadrats2osm` Python tool to generate [OSM XML](https://wiki.openstreetmap.org/wiki/OSM_XML) files for all the regions in the configuration file.

The format of the configuration file is as follows:

```
{
  "output": "dist/europe/squadrats-PL-poland.img",
  "mapname_prefix": "97616",
  "zoom_14": [
    "PL-*"
  ],
  "zoom_17": [
    "PL-*"
  ]
}
```

* `output`

    The name of the output IMG file.

* `mapname_prefix`

    If you want to keep multiple IMG files on your Garmin unit, this value needs to be unique for each IMG file.

    This value should be 5 digits long. For the country-specific grids the following pattern is used: `97[ISO_3166-1-numeric-code]`.

    For custom grids it is up to you.

* `zoom_14`

    List of regions for which the squadrats (zoom level 14) grid will be generated. Accepted values are:

    * ISO 3166-1 alpha-2 country codes (eg. `PL` for Poland)
    * ISO 3166-1 subdivision codes (eg. `PL-22` for the Pomeranian Voivodeship in Poland)
    * wildcard `*` combined with ISO 3166-1 alpha-2 country codes (eg `PL-*` for all voivodeships in Poland)

* `zoom_17`

    List of regions for which the squadratinhos (zoom level 17) grid will be generated. Accepted values are:

    * ISO 3166-1 alpha-2 country codes (eg. `PL` for Poland)
    * ISO 3166-1 subdivision codes (eg. `PL-22` for the Pomeranian Voivodeship in Poland)
    * wildcard `*` combined with ISO 3166-1 alpha-2 country codes (eg `PL-*` for all voivodeships in Poland)

    Be mindful that generating squadratinhos (zoom level 17) grid for the large regions will take a lot of time and might also impact Garmin unit performance.

## Convert OSM XML files to Garmin IMG files
The [mkgmap](https://www.mkgmap.org.uk/) tool is used to convert the [OSM XML](https://wiki.openstreetmap.org/wiki/OSM_XML) file to Garmin IMG file. This process uses the configuration in the `mkgmap` child element.