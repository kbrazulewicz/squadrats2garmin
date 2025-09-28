import json
import sys

from common.region import Region, RegionIndex


def select_regions(poly_index: RegionIndex, regions: list[str]) -> list[Region]:
    result: list[Region] = []
    for region in regions:
        country_code, sep, subdivision_code = region.partition("-")

        # country_code not defined
        if not country_code:
            raise ValueError(f"Invalid region code: {region}")

        if not country_code in poly_index.country:
            raise ValueError(f"Missing border definitions for country {country_code}")

        country = poly_index.country[country_code]
        if not subdivision_code:
            result.append(country)
        elif subdivision_code == "*":
            result.extend(country.subdivisions.values())
        else:
            if region in country.subdivisions:
                result.append(country.subdivisions[region])
            else:
                raise ValueError(f"Missing border definitions for subdivision {region} in country {country.name}")

    return result


def process_config(filename: str, poly_index: RegionIndex):
    print(f'Processing input job from "{filename}"')
    output_file: str
    regions_14: list[Region] = []
    regions_17: list[Region] = []
    with open(filename) as configFile:
        config = json.load(configFile)
        output_file = config['output']
        print(f"Output file: {output_file}")
        regions_14 = select_regions(poly_index=poly_index, regions=config['zoom_14'])
        print(f"Zoom 14: {len(regions_14)} regions")
        print([region.get_name() for region in regions_14])
        regions_17 = select_regions(poly_index=poly_index, regions=config['zoom_17'])
        print(f"Zoom 17: {len(regions_17)} regions")
        print([region.get_name() for region in regions_17])


def main(config_file: str) -> None:
    poly_index = RegionIndex("config/polygons")
    process_config(config_file, poly_index)

if __name__ == "__main__":
    match len(sys.argv):
        case 2:
            main(sys.argv[1])
        case _:
            main("config/config-01.json")