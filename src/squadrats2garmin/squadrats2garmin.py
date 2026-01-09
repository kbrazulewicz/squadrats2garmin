import argparse
import logging
import tempfile
from pathlib import Path

from squadrats2garmin.common.job import Job
from squadrats2garmin.common.mkgmap import RegionConfig
from squadrats2garmin.common.region import RegionIndex
from squadrats2garmin.common.squadrats import generate_osm
from squadrats2garmin.common.tile import ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS
from squadrats2garmin.common.timer import timeit

logger = logging.getLogger(__name__)

def process_input_job(config_file: str, poly_index: RegionIndex, output_dir: Path) -> None:
    """Generate grid according to the config file and convert it into Garmin IMG file"""
    logger.info("Load input job")
    config = RegionConfig.parse(filename=config_file, poly_index=poly_index, output_dir=output_dir)

    jobs: list[Job] = []
    for zoom in [ZOOM_SQUADRATS, ZOOM_SQUADRATINHOS]:
        for region in sorted(config.regions[zoom], key=lambda r: r.code):
            osm_file = output_dir / f"{region.code}-{zoom.zoom}.osm"
            job = Job(region=region, zoom=zoom, osm_file=osm_file)
            with timeit(f"{job}: generate_osm"):
                generate_osm(job)
            jobs.append(job)

    config.build_garmin_img(jobs=jobs)


def parse_args():
    parser = argparse.ArgumentParser(description="Generate OSM files with Squadrats grid")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="verbose output")
    parser.add_argument('-k', '--keep', action='store_true',
                        help="keep output files after processing")
    parser.add_argument('-c', '--config-files', required=True, nargs='+', metavar='CONFIG_FILE',
                        help="list of config files to process")
    return parser.parse_args()


def main():
    # parse arguments
    args = parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # create poly index
    logger.info("Generate poly index")
    poly_index = RegionIndex(Path("config/polygons"))

    # process input jobs
    for config_file in args.config_files:
        with tempfile.TemporaryDirectory(prefix="mkgmap-", delete=(not args.keep)) as tmp_dir_name:
            tmp_dir = Path(tmp_dir_name)

            with timeit(msg=f"Processing {config_file}"):
                process_input_job(config_file=config_file, poly_index=poly_index, output_dir=tmp_dir)

            if args.keep:
                logger.info(f"Keeping output files in {tmp_dir_name}")

if __name__ == "__main__":
    main()