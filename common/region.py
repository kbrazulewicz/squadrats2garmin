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
    return code if re.match(r'^[A-Z0-9]{1,3}$', code) else None

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

        super().__init__(iso_code=iso_code, name=subdivision.name, poly=poly)
        self.country = country

    def __repr__(self):
        return f'Subdivision("{self.iso_code}")'

    def get_country_code(self) -> str:
        return self.country.get_country_code()

    def get_country_name(self) -> str:
        return self.country.get_country_name()

    def get_name(self) -> str:
        """
        Returns the formatted name of the entity by appending the country name.

        Returns
        str
            A formatted string containing the country name followed by the name of the entity.
        """
        return f'{self.get_country_name()} - {self.name}'

class Country(Region):
    __country: pycountry.db.Country
    __subdivisions: dict[str, list[Subdivision]]

    def __init__(self, iso_code: str, poly: Poly = None) -> None:
        country = pycountry.countries.get(alpha_2=iso_code)
        if not country:
            raise ValueError(f'Illegal country ISO code {iso_code}')

        super().__init__(iso_code=iso_code, name=country.name, poly=poly)
        self.__country = country
        self.__subdivisions = {}

    def __repr__(self):
        return f'Country({self.iso_code}, {[subdivision for subdivision in self.get_all_subdivisions()]})'

    def get_country_code(self) -> str:
        return self.iso_code

    def get_country_name(self) -> str:
        return self.__country.name

    def add_subdivision(self, iso_code:str, poly: Poly):
        if iso_code not in self.__subdivisions:
            self.__subdivisions[iso_code] = []
        self.__subdivisions[iso_code].append(Subdivision(country=self, iso_code=iso_code, poly=poly))

    def get_all_subdivisions(self) -> list[Subdivision]:
        return [subdivision for sublist in self.__subdivisions.values() for subdivision in sublist]

    def get_subdivisions(self, iso_code: str) -> list[Subdivision]:
        if iso_code in self.__subdivisions:
            return self.__subdivisions[iso_code]
        else:
            return None


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

    def select_regions(self, regions: list[str]) -> list[Region]:
        result: list[Region] = []
        for region in regions:
            country_code, sep, subdivision_code = region.partition("-")

            # country_code not defined
            if not country_code:
                raise ValueError(f'Invalid region code: {region}')

            # country_code not in the POLY index
            if not country_code in self.country:
                raise ValueError(f'Missing border definitions for country {country_code}')

            country = self.country[country_code]
            if not subdivision_code:
                # selected country
                if country.poly:
                    result.append(country)
                else:
                    raise ValueError(f'Missing border definitions for country {country_code}')
            elif subdivision_code == "*":
                # selected all subdivisions in a country
                result.extend(country.get_all_subdivisions())
            else:
                # selected subdivision (which can have multiple polygons)
                subdivisions = country.get_subdivisions(subdivision_code)
                if subdivisions:
                    result.extend(subdivisions)
                else:
                    raise ValueError(f'Missing border definitions for subdivision {region} in country {country.name}')

        return result