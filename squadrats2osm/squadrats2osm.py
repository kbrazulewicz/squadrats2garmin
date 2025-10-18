import logging
import pathlib
import sys

from common.config import Config
from common.job import Job
from common.region import RegionIndex, Subdivision
from common.squadrats import generate_osm
from common.zoom import ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS

OUTPUT_PATH = "output"

IMG_FAMILY_ID = 9724
IMG_MAPNAME_PREFIX_LENGTH = 5
IMG_FAMILY_NAME = "Squadrats2Garmin 2025"
IMG_SERIES_NAME = "Squadrats grid"

logger = logging.getLogger(__name__)


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
    config = Config.parse(config_file, poly_index)

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
