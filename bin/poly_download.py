#!/usr/bin/env python3

import re
import sys
import time
from pathlib import Path

import overpy
import pycountry
import requests

class PolyDownloader:
    def __init__(self, base_url="http://polygons.openstreetmap.fr"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSM-PolyDownloader/1.0'
        })

    def download(self, relation_id: int, output_path: str, retry_count: int = 5):
        """Download POLY file with retries"""

        url = f"{self.base_url}/get_poly.py"
        params = {
            "id": relation_id,
            "params": "0.020000-0.020000-0.020000"
        }
        output_path = Path(output_path)

        for attempt in range(retry_count):
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()

                # Check if the response is actually a POLY file
                if not response.text.startswith('polygon\n'):
                    raise ValueError("Response is not a valid POLY file")

                # Create the parent directory if needed
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Write file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                return True

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff

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
                    print(f'Unable to find relation for {iso_code}')
                    return False
                elif len(result.relations) > 1:
                    print(f'Multiple relations found for {iso_code}')
                    return False
                else:
                    return result.relations[0].id

            except Exception as e:
                print(f'Attempt {attempt + 1} failed: {e}')
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff

        return False


def get_output_path(code: str):
    if "-" in code:
        subdivision = pycountry.subdivisions.get(code=code)
        if subdivision:
            return f'{code}-{subdivision.name.replace(" ", "-")}.poly'
        else:
            return f'{code}.poly'
    else:
        country = pycountry.countries.get(alpha_2=code)
        if country:
            return f'{code}-{country.name.replace(" ", "-")}.poly'
        else:
            return f'{code}.poly'


def download_poly(code: str, osm_id: int):
    output_path = get_output_path(code=code)
    if poly_downloader.download(relation_id=osm_id, output_path=output_path):
        print(f'{code}: {output_path}')

osm_id_resolver = OsmIdResolver()
poly_downloader = PolyDownloader()

for arg in sys.argv[1:]:
    # relation id
    if arg.isdigit():
        download_poly(code=arg, osm_id=int(arg))
        continue

    # country wildcard (all subdivisions)
    match = re.match(r'^([A-Z]{2})-\*$', arg)
    if match:
        subdivisions = pycountry.subdivisions.get(country_code=match.group(1))
        for subdivision in sorted(subdivisions, key=lambda subdivision: subdivision.code):
            code = subdivision.code
            osm_id = osm_id_resolver.get_id(code)
            download_poly(code=code, osm_id=osm_id)
    else:
        osm_id = osm_id_resolver.get_id(arg)
        download_poly(code=arg, osm_id=osm_id)