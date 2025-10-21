import argparse
import logging
import os
import pathlib
import subprocess

from common.config import Config
from common.job import Job
from common.region import RegionIndex, Subdivision
from common.squadrats import generate_osm
from common.zoom import ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS

OUTPUT_PATH = pathlib.Path("output")

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
        config_file.write(f'output-dir={OUTPUT_PATH.name}\n')

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

def generate_garmin_img(config: Config, jobs: list[Job]):
    # generate mkgmap config file
    mkgmap_config = OUTPUT_PATH / 'mkgmap.conf'
    generate_mkgmap_config(output=mkgmap_config, config=config, jobs=jobs)

    # generate Garmin IMG file
    logger.info(f'Creating Garmin IMG file {config.output}')
    result = subprocess.run(
        ['mkgmap', f'--read-config={str(mkgmap_config)}'],
        cwd=os.getcwd(),
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f'mkgmap failed: {result.stderr}')

    gmapsupp_img = OUTPUT_PATH / 'gmapsupp.img'
    if not gmapsupp_img.exists():
        raise RuntimeError(f'gmapsupp.img not found')

    gmapsupp_img.move(config.output)


def process_input_job(config_file: str, poly_index: RegionIndex) -> None:
    logger.info("Load input job")
    config = Config.parse(config_file, poly_index)

    jobs: list[Job] = []
    for zoom in [ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS]:
        for region in sorted(config.regions[zoom], key=lambda r: r.iso_code):
            osm_file = OUTPUT_PATH / f'{region.iso_code}-{zoom.zoom}.osm'
            job = Job(region=region, zoom=zoom, osm_file=osm_file)
            generate_osm(job)
            jobs.append(job)

    generate_garmin_img(config=config, jobs=jobs)

def remove_all_files(directory: pathlib.Path):
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_path.unlink()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # parse arguments
    parser = argparse.ArgumentParser(description='Generate OSM files with Squadrats grid')
    parser.add_argument('-k', '--keep-output', action='store_true', help='Keep output files after processing')
    parser.add_argument('-c', '--config-files', nargs='+', metavar='CONFIG_FILE', help='List of config files to process')
    args = parser.parse_args()

    # create poly index
    logger.info("Generate poly index")
    poly_index = RegionIndex("config/polygons")

    # create output directory
    if not OUTPUT_PATH.exists():
        OUTPUT_PATH.mkdir(parents=True)

    # process input jobs
    for config_file in args.config_files:
        # clear output directory before processing
        remove_all_files(OUTPUT_PATH)
        process_input_job(config_file, poly_index)
        if not args.keep_output:
            remove_all_files(OUTPUT_PATH)