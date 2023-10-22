# Configuring jobs for squadrats2garmin

Generating a Garmin compatible IMG file with Squadrats grid is a two-phase process.

## Generate OSM XML files
The `squadrats2garmin` script invokes the `squadrats2osm` Python tool to generate [OSM XML](https://wiki.openstreetmap.org/wiki/OSM_XML) files for all the `jobs` in the configuration file.

This process uses the top level configuration in the `job` element:

```
{
    "id": "616-14",
    "poly": "config/polygons/europe/poland.poly",
    "zoom": "squadrats",
    "osm": "output/europe/squadrats-PL-{name}.osm",
    "mkgmap": { ... }
}
```

* `id`

    The job id. Must be unique in the scope of a configuration file. In the pre-made configuration files the following pattern is used:

    * `[country-code-ISO_3166-1]-[zoom-level]` for the country-level grids (ie. `616-14` for squadrats-level grid for Poland)
    * `[country-code-ISO_3166-1]-[numerical-province-code]-[zoom-level]` for the province-level grids (ie. `616-22-17` for squadratinhos-level grid for Pomeranian voivodeship in Poland)

* `poly`

    The path to the input [POLY](polygons/README.md) file.

* `zoom`

    Zoom level. Accepted values are:

    * `squadrats` which corresponds to OSM zoom level 14
    * `squadratinhos` which corresponds to OSM zoom level 17

* `osm`

    The path to the output [OSM XML](https://wiki.openstreetmap.org/wiki/OSM_XML) file.
    
    The following name substitutions can be used:
    
    * `{name}`

        The base name of the POLY file.


## Convert OSM XML files to Garmin IMG files
The [mkgmap](https://www.mkgmap.org.uk/) tool is used to convert the [OSM XML](https://wiki.openstreetmap.org/wiki/OSM_XML) file to Garmin IMG file. This process uses the configuration in the `mkgmap` child element.

```
{
    "id": "616-14",
    ...
    "mkgmap": {
        "mapName": "96160001",
        "description": "europe/poland Squadrats",
        "familyId": "9616",
        "familyName": "Squadrats Poland",
        "productId": "1",
        "seriesName": "Squadrats",
        "areaName": "europe/poland",
        "countryName": "Poland",
        "countryAbbr": "PL",
        "imgFile": "dist/europe/squadrats-PL-{name}.img"
    }
}
```

* `familyId`

    As per [mkgmap documentation](https://www.mkgmap.org.uk/doc/options#:~:text=Product%20description%20options):

    > This is an integer that identifies a family of products. Range: [1..65535] Default: 6324

    In the pre-made configuration files the following pattern is used: `9[country-code-ISO_3166-1]` and it is the same value for all the jobs in the configuration file (ie. `9616` for jobs related to Poland).

    🤔 To be verified: use the same value for all the squadrats grids.

* `familyName`

    Similar meaning to `familyId` but it is a text description.

    🤔 To be verified: use the same value for all the squadrats grids.

* `productId`

    As per [mkgmap documentation](https://www.mkgmap.org.uk/doc/options#:~:text=Product%20description%20options):

    > This is an integer that identifies a product within a family. It is often just 1, which is the default.

    In the pre-made configuration files the following pattern is used:

    * `1` 

        for the squadrats-level grid for the entire country

    * `101` 

        for the squadratinhos-level grid for the entire country

    * `1[numerical-province-code]` 

        for the squadratinhos-level grid for the country's province

    🤔 To be verified: are different values necessary? Is this configuration option needed?

* `seriesName`

    As per [mkgmap documentation](https://www.mkgmap.org.uk/doc/options#:~:text=Product%20description%20options):

    > This name will be displayed by Garmin PC programs in the map selection drop-down.

* `mapName`

    As per [mkgmap documentation](https://www.mkgmap.org.uk/doc/options#:~:text=Product%20description%20options):

    > Set the name of the map. Garmin maps are identified by an 8 digit number. The default is 63240001. It is best to use a different name if you are going to be making a map for others to use so that it is unique and does not clash with others.

    In the pre-made configuration files the following pattern is used: `[familyId][zero-padded-productId]`.

    🤔 To be verified: does this value need to be unique?

* `description`

    This is map description which you'll see in your Garmin unit.

* `countryName`
* `countryAbbr`

    Country name and abbreviated country name.

    🤔 To be verified: are those values used by the Garmin units?

* `regionName`
* `regionAbbr`

    Region name and abbreviated region name. Skip those for the country-level grids.

    🤔 To be verified: are those values used by the Garmin units?
