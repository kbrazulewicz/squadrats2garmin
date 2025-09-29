import logging
from abc import ABC, abstractmethod

import pycountry
import re

from common.poly import Poly
from pathlib import Path

logger = logging.getLogger(__name__)

def get_country_code(code: str) -> str:
    return code if re.match(r'^[A-Z]{2}$', code) else None

def get_subdivision_code(code: str) -> str:
    return code if re.match(r'^[A-Z0-9]{2,3}$', code) else None

class Region(ABC):
    iso_code: str
    name: str
    poly: Poly

    def __init__(self, iso_code: str, name: str, poly: Poly):
        self.iso_code = iso_code
        self.name = name
        self.poly = poly

    def get_code(self) -> str:
        return self.iso_code

    def get_name(self) -> str:
        return self.name

    @abstractmethod
    def get_country_code(self) -> str:
        pass

    @abstractmethod
    def get_country_name(self) -> str:
        pass



class Subdivision(Region):
    country: Region

    def __init__(self, *, country: Region, iso_code: str, poly: Poly):
        subdivision = pycountry.subdivisions.get(code=iso_code)
        if not subdivision:
            raise ValueError(f'Illegal subdivision ISO code {iso_code}')

        super().__init__(iso_code, subdivision.name, poly)
        self.country = country

    def __repr__(self):
        return f'Subdivision("{self.iso_code}")'

    def get_country_code(self) -> str:
        return self.country.get_country_code()

    def get_country_name(self) -> str:
        return self.country.get_country_name()

    def get_name(self) -> str:
        return f'{self.country.get_name()} - {self.name}'


class Country(Region):
    subdivisions: dict[str, Subdivision]
    __country: pycountry.db.Country

    def __init__(self, iso_code: str, poly: Poly = None) -> None:
        country = pycountry.countries.get(alpha_2=iso_code)
        if not country:
            raise ValueError(f'Illegal country ISO code {iso_code}')

        super().__init__(iso_code=iso_code, name=country.name, poly=poly)
        self.__country = country
        self.subdivisions = {}

    def __repr__(self):
        return f'Country({self.iso_code}, {[subdivision for subdivision in self.subdivisions.values()]})'

    def get_country_code(self) -> str:
        return self.iso_code

    def get_country_name(self) -> str:
        return self.__country.name

    def add_subdivision(self, iso_code, poly: Poly):
        self.subdivisions[iso_code] = Subdivision(country=self, iso_code=iso_code, poly=poly)

class RegionIndex:
    country: dict[str, Country]
    subdivision: dict[str, Subdivision]

    def __init__(self, root_path: str):
        self.country = {}
        self.subdivision = {}

        root = Path(root_path)
        logging.debug(f'Building polygon index from "{root}"')
        for path in root.rglob('*.poly'):
            codes = path.stem.split("-", maxsplit=2)

            country_code = get_country_code(codes[0])
            if not country_code:
                logging.debug(f'File {path} does not contain country code in the name - skipping')
                continue

            # country poly
            if len(codes) == 1:
                self._add_country(country_code, path)
                continue

            subdivision_code = get_subdivision_code(codes[1])
            if not subdivision_code:
                self._add_country(country_code, path)
                continue

            self._add_subdivision(country_code, subdivision_code, path)

    def _add_country(self, country_code: str, poly_path: Path):
        self.country[country_code] = Country(iso_code=country_code, poly=Poly(poly_path))

    def _add_subdivision(self, country_code: str, subdivision_code: str, poly_path: Path):
        iso_code = "-".join([country_code, subdivision_code])

        if not country_code in self.country:
            self.country[country_code] = Country(iso_code=country_code)

        self.country[country_code].add_subdivision(iso_code=iso_code, poly=Poly(poly_path))


def select_regions(poly_index: RegionIndex, regions: list[str]) -> list[Region]:
    result: list[Region] = []
    for region in regions:
        country_code, sep, subdivision_code = region.partition("-")

        # country_code not defined
        if not country_code:
            raise ValueError(f'Invalid region code: {region}')

        # country_code not in the POLY index
        if not country_code in poly_index.country:
            raise ValueError(f'Missing border definitions for country {country_code}')

        country = poly_index.country[country_code]
        if not subdivision_code:
            # selected country
            if country.poly:
                result.append(country)
            else:
                raise ValueError(f'Missing border definitions for country {country_code}')
        elif subdivision_code == "*":
            # selected all subdivisions in a country
            result.extend(country.subdivisions.values())
        else:
            # selected subdivision
            if region in country.subdivisions:
                result.append(country.subdivisions[region])
            else:
                raise ValueError(f'Missing border definitions for subdivision {region} in country {country.name}')

    return result