import argparse
import logging
import pathlib

from common.config import RegionConfig, OUTPUT_DIR
from common.job import Job
from common.mkgmap import generate_garmin_img
from common.region import RegionIndex
from common.squadrats import generate_osm
from common.zoom import ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS

logger = logging.getLogger(__name__)

def process_input_job(config_file: str, poly_index: RegionIndex) -> None:
    """Generate grid according to the config file and convert it into Garmin IMG file"""
    logger.info("Load input job")
    config = RegionConfig.parse(config_file, poly_index)

    jobs: list[Job] = []
    for zoom in [ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS]:
        for region in sorted(config.regions[zoom], key=lambda r: r.code):
            osm_file = OUTPUT_DIR / f'{region.code}-{zoom.zoom}.osm'
            job = Job(region=region, zoom=zoom, osm_file=osm_file)
            generate_osm(job)
            jobs.append(job)

    generate_garmin_img(config=config, jobs=jobs)


def remove_all_files(directory: pathlib.Path):
    """Remove all files from a directory"""
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_path.unlink()


def main():
    # parse arguments
    parser = argparse.ArgumentParser(description='Generate OSM files with Squadrats grid')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='verbose output')
    parser.add_argument('-k', '--keep-output', action='store_true',
                        help='keep output files after processing')
    parser.add_argument('-c', '--config-files', required=True, nargs='+', metavar='CONFIG_FILE',
                        help='list of config files to process')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # create poly index
    logger.info("Generate poly index")
    poly_index = RegionIndex("config/polygons")

    # create output directory
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)

    # process input jobs
    for config_file in args.config_files:
        # clear output directory before processing
        remove_all_files(OUTPUT_DIR)
        process_input_job(config_file=config_file, poly_index=poly_index)
        if not args.keep_output:
            remove_all_files(OUTPUT_DIR)

if __name__ == "__main__":
    main()