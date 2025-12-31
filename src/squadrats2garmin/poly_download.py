#!/usr/bin/env python3
import argparse
import logging
import re
import time
from pathlib import Path

import overpy
import pycountry
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger(__name__)


class PolyDownloader:
    def __init__(self, base_url: str = "http://polygons.openstreetmap.fr", poly_format: str = "json") -> None:
        self._poly_format = poly_format
        self._base_url = base_url
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'OSM-PolyDownloader/1.0'
        })

        retry = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount('http://', adapter)
        self._session.mount('https://', adapter)

    def download(self, relation_id: int, output_path: Path):
        """Download POLY file with retries"""
        url: str
        if self._poly_format == "json":
            url = f"{self._base_url}/get_geojson.py"
        elif self._poly_format == "poly":
            url = f"{self._base_url}/get_poly.py"
        else:
            raise ValueError(f"Unsupported download format {self._poly_format}")

        params = {
            "id": relation_id,
            "params": "0.020000-0.020000-0.020000"
        }

        try:
            response = self._session.get(url, params=params, timeout=30)
            response.raise_for_status()

            # Check if the response is actually a POLY file
            # if not response.text.startswith('polygon\n'):
            #     raise ValueError("Response is not a valid POLY file")

            # Create the parent directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return True

        except Exception as e:
            return False


class OsmIdResolver:
    def __init__(self):
        self.api = overpy.Overpass()

    def get_id(self, iso_code: str, retry_count: int = 5) -> int:
        query: str
        if "-" in iso_code:
            query = f'''
             relation["ISO3166-2"="{iso_code}"]["boundary"="administrative"];
             out ids;
             '''
        else:
            query = f'''
             relation["ISO3166-1:alpha2"="{iso_code}"]["boundary"="administrative"];
             out ids;
             '''

        for attempt in range(retry_count):
            try:
                result: overpy.Result = self.api.query(query)

                if len(result.relations) == 0:
                    logger.error("Unable to find relation for %s", iso_code)
                    return False
                elif len(result.relations) > 1:
                    logger.error("Multiple relations found for %s", iso_code)
                    return False
                else:
                    return result.relations[0].id

            except Exception as e:
                logger.warning("Attempt %d failed: %s", attempt + 1, e)
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff

        return False


class PolyNameResolver:
    def __init__(self, poly_format: str):
        self._poly_format: str = poly_format

    def resolve(self, code: str) -> Path:
        def resolve_name(code: str, file_ext: str) -> str:
            if "-" in code:
                subdivision = pycountry.subdivisions.get(code=code)
                if subdivision:
                    return f"{code}-{subdivision.name.replace(" ", "-")}.{file_ext}"
                else:
                    return f"{code}.{file_ext}"
            else:
                country = pycountry.countries.get(alpha_2=code)
                if country:
                    return f"{code}-{country.name.replace(" ", "-")}.{file_ext}"
                else:
                    return f"{code}.{file_ext}"

        return Path(resolve_name(code=code, file_ext=self._poly_format))

def download_poly(downloader: PolyDownloader, name_resolver: PolyNameResolver, code: str, osm_id: int):
    output_path = name_resolver.resolve(code=code)

    if downloader.download(relation_id=osm_id, output_path=output_path):
        logger.info("Successfully downloaded %s", output_path)

def parse_args():
    parser = argparse.ArgumentParser(description="Download polygon for OpenStreetMap relation")

    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('-p', '--poly', dest='format', action='store_const', const='poly', help="Download POLY file")
    action.add_argument('-j', '--json', dest='format', action='store_const', const='json', help="Download JSON file")

    parser.add_argument('-r', '--regions', required=True, nargs='+', metavar='REGION',
                        help="list of regions to download")
    parser.add_argument('-v', '--verbose', action='store_true', help="verbose output")

    return parser.parse_args()

def main():

    args = parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    osm_id_resolver = OsmIdResolver()
    poly_downloader = PolyDownloader(poly_format=args.format)
    name_resolver = PolyNameResolver(poly_format=args.format)

    for arg in args.regions:
        # relation id
        if arg.isdigit():
            download_poly(downloader=poly_downloader, name_resolver=name_resolver, code=arg, osm_id=int(arg))
            continue

        # country wildcard (all subdivisions)
        match = re.match(r'^([A-Z]{2})-\*$', arg)
        if match:
            country_code = match.group(1)
            subdivisions = pycountry.subdivisions.get(country_code=country_code)
            if not subdivisions:
                raise ValueError(f'No subdivisions defined for country {match.group(1)}')
            for subdivision in sorted(subdivisions, key=lambda subdivision: subdivision.code):
                code = subdivision.code
                osm_id = osm_id_resolver.get_id(code)
                download_poly(downloader=poly_downloader, name_resolver=name_resolver, code=code, osm_id=osm_id)
        else:
            osm_id = osm_id_resolver.get_id(arg)
            download_poly(downloader=poly_downloader, name_resolver=name_resolver, code=arg, osm_id=osm_id)

if __name__ == "__main__":
    main()
