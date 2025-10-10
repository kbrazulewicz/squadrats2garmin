import json
import logging
import pathlib
import sys
import xml.etree.ElementTree as ET

from common.job import Job
from common.region import Region, RegionIndex, Subdivision
from common.squadrats import generate_tiles, generate_grid
from common.timer import timeit
from common.zoom import Zoom, ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS

OUTPUT_PATH = "output"

IMG_FAMILY_ID = 9724
IMG_MAPNAME_PREFIX_LENGTH = 5
IMG_FAMILY_NAME = "Squadrats2Garmin 2025"
IMG_SERIES_NAME = "Squadrats grid"

logger = logging.getLogger(__name__)

class Config:
    output: str
    description: str
    mapname_prefix: str
    regions: dict[Zoom, list[Region]]

    def __init__(self, config:dict, regions_14: list[Region], regions_17: list[Region]) -> None:
        self.output = config['output']
        self.description = config['description']
        if 'mapname_prefix' in config:
            self.mapname_prefix = config['mapname_prefix']
        else:
            self.mapname_prefix = str(IMG_FAMILY_ID).ljust(IMG_MAPNAME_PREFIX_LENGTH, '0')
        if len(self.mapname_prefix) > IMG_MAPNAME_PREFIX_LENGTH:
            raise ValueError(f'Mapname prefix "{self.mapname_prefix}" is too long')

        self.regions = {
            ZOOM_SQUADRATS: regions_14,
            ZOOM_SQUADRATINHOS: regions_17
        }


def process_config(filename: str, poly_index: RegionIndex) -> Config:
    logger.debug(f'Processing input job from "{filename}"')
    with open(filename) as configFile:
        config = json.load(configFile)

        regions_14: list[Region] = poly_index.select_regions(regions=config['zoom_14'])
        regions_17: list[Region] = poly_index.select_regions(regions=config['zoom_17'])

        return Config(config=config, regions_14=regions_14, regions_17=regions_17)


def generate_osm(job: Job):
    logger.info(f'Generating OSM: {job} -> {job.osm_file}')

    with timeit(f'{job}: generate_tiles'):
        tiles = generate_tiles(poly=job.region.poly, job=job)

    logger.debug(f'{job}: {sum(map(len, tiles.values()))} tiles')

    with timeit(f'{job}: generate_grid'):
        ways = generate_grid(tiles=tiles, job=job)

    logger.debug(f'{job}: {len(ways)} ways')

    unique_nodes = set()
    with timeit(f'{job}: collect unique nodes'):
        for w in ways:
            unique_nodes.update(w.nodes)

    logger.debug(f'{job}: {len(unique_nodes)} unique nodes')

    with timeit(f'{job}: build OSM document'):
        document = ET.Element("osm", {"version": '0.6'})
        document.extend(n.to_xml() for n in sorted(unique_nodes, key=lambda node: node.id))
        document.extend(w.to_xml() for w in sorted(ways, key=lambda way: way.id))
        ET.indent(document)

    with timeit(f'{job}: write OSM document {job.osm_file}'):
        job.osm_file.parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(document).write(job.osm_file, encoding='utf-8', xml_declaration=True)


def generate_mkgmap_config(output: pathlib.Path, config: Config, jobs: list[Job]):
    with (open(output, "w", encoding="utf-8") as config_file):
        # images with 'unicode' encoding are not displayed on Garmin
        config_file.write("latin1\n")
        config_file.write("transparent\n")
        config_file.write(f'output-dir={OUTPUT_PATH}\n')

        config_file.write(f'family-id={IMG_FAMILY_ID}\n')
        config_file.write(f'family-name={IMG_FAMILY_NAME}\n')
        config_file.write("product-id=1\n")
        config_file.write(f'series-name={IMG_SERIES_NAME}\n')

        config_file.write("style-file=style/squadrats-default.style\n")

        sequence_number = 1
        for job in jobs:
            # mapname_prefix is 5 characters long, and we're adding 3 digits of a sequence number
            if sequence_number > 999:
                raise ValueError("Too many mapfiles to merge")
            config_file.write(f'mapname={config.mapname_prefix}{sequence_number:03d}\n')
            config_file.write(f'country-name={job.region.get_country_name()}\n')
            config_file.write(f'country-abbr={job.region.get_country_code()}\n')
            if isinstance(job.region, Subdivision):
                config_file.write(f'region-name={job.region.get_name()}\n')
                config_file.write(f'region-abbr={job.region.get_code()}\n')


            description = (f'{job.region.get_name()} @{job.zoom.zoom}'
                # country name replacements
                .replace(", Republic of", "")
                .replace("Bosnia and Herzegovina", "BiH")
                # region name replacements
                .replace(", Unitatea teritorială autonomă (UTAG)", "")
                .replace(", unitatea teritorială din", "")
                           )
            config_file.write(f'description={description}\n')
            config_file.write(f'input-file={job.osm_file.relative_to(OUTPUT_PATH)}\n')

            sequence_number += 1

        config_file.write("input-file=../typ/squadrats.typ.txt\n")

        config_file.write(f'description={config.description}\n')
        config_file.write("gmapsupp\n")


def main(config_file: str) -> None:
    logger.info("Generate poly index")
    poly_index = RegionIndex("config/polygons")
    logger.info("Load input job")
    config = process_config(config_file, poly_index)

    jobs: list[Job] = []
    for zoom in [ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS]:
        for region in sorted(config.regions[zoom], key=lambda r: r.iso_code):
            output = f'{OUTPUT_PATH}/{region.iso_code}-{zoom.zoom}.osm'
            job = Job(region=region, zoom=zoom, osm_file=pathlib.Path(output))
            generate_osm(job)
            jobs.append(job)

    mkgmap_config = pathlib.Path(f'{OUTPUT_PATH}/mkgmap.conf')
    generate_mkgmap_config(output=mkgmap_config, config=config, jobs=jobs)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    match len(sys.argv):
        case 2:
            main(sys.argv[1])
        case _:
            main("config/squadrats2osm.json")