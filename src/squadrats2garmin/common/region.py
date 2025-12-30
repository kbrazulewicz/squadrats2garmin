"""Classes and functions to handle ISO-3166 regions
"""
import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path

import pycountry
from pygeoif import MultiPolygon

from squadrats2garmin.common.poly import parse_poly_file

logger = logging.getLogger(__name__)

def get_country_code(code: str) -> str:
    """Match the input string with a pattern for ISO 3166-1 alpha-2 country code
    """
    return code if re.match(r'^[A-Z]{2}$', code) else None

def get_subdivision_code(code: str) -> str:
    """Match the input string with a pattern for ISO 3166-2 subdivision code.
    """
    return code if re.match(r'^[A-Z0-9]{1,3}$', code) else None


class Region(ABC):
    """Abstract base class for regions
    """
    _iso_code: str
    _name: str
    _geoms: MultiPolygon

    def __init__(self, iso_code: str, name: str, coordinates: MultiPolygon):
        self._iso_code = iso_code
        self._name = name
        self._geoms = coordinates

    @property
    def code(self) -> str:
        """Get region code
        """
        return self._iso_code

    @property
    def name(self) -> str:
        """Get region name
        """
        return self._name

    @property
    def coords(self) -> MultiPolygon:
        """Get region coordinates
        """
        return self._geoms

    @abstractmethod
    def get_country_code(self) -> str:
        """Get region country code
        """

    @abstractmethod
    def get_country_name(self) -> str:
        """Get region country name
        """


class Subdivision(Region):
    """Representation of the ISO 3166-2 subdivision
    """
    country: Region

    def __init__(self, country: Region, iso_code: str, coordinates: MultiPolygon):
        subdivision = pycountry.subdivisions.get(code=iso_code)
        if not subdivision:
            raise ValueError(f'Illegal subdivision ISO code {iso_code}')

        super().__init__(iso_code=iso_code, name=subdivision.name, coordinates=coordinates)
        self.country = country

    def __repr__(self):
        return f'Subdivision("{self.code}")'

    def get_country_code(self) -> str:
        return self.country.get_country_code()

    def get_country_name(self) -> str:
        return self.country.get_country_name()

    @property
    def name(self) -> str:
        """
        Returns the formatted name of the entity by appending the country name.

        Returns
        str
            A formatted string containing the country name followed by the name of the entity.
        """
        return f'{self.get_country_name()} - {self._name}'


class Country(Region):
    """Representation of the ISO 3166-1 country
    """
    __country: pycountry.db.Country
    __subdivisions: dict[str, list[Subdivision]]
    """subdivisions multimap (should be a regular dictionary but Norway was special)"""

    def __init__(self, iso_code: str, coordinates: MultiPolygon = None) -> None:
        country = pycountry.countries.get(alpha_2=iso_code)
        if not country:
            raise ValueError(f'Illegal country ISO code {iso_code}')

        super().__init__(iso_code=iso_code, name=country.name, coordinates=coordinates)
        self.__country = country
        self.__subdivisions = {}

    def __repr__(self):
        return f'Country({self._iso_code}, {self.get_all_subdivisions()})'

    def get_country_code(self) -> str:
        return self.code

    def get_country_name(self) -> str:
        return self.__country.name

    def add_subdivision(self, iso_code: str, coordinates: MultiPolygon):
        """Register a subdivision poly file
        """
        if iso_code not in self.__subdivisions:
            self.__subdivisions[iso_code] = []
        self.__subdivisions[iso_code].append(
            Subdivision(country=self, iso_code=iso_code, coordinates=coordinates)
        )

    def get_all_subdivisions(self) -> list[Subdivision]:
        """Get the list of all subdivisions"""
        return [subdivision for sublist in self.__subdivisions.values() for subdivision in sublist]

    def get_subdivisions(self, iso_code: str) -> list[Subdivision]:
        """Get the list of subdivisions for a subdivision code"""
        if iso_code in self.__subdivisions:
            return self.__subdivisions[iso_code]
        return None


class RegionIndex:
    """Loads polygons for all regions found in the filesystem
    """
    country: dict[str, Country]
    subdivision: dict[str, Subdivision]

    def __init__(self, root_path: str):
        self.country = {}
        self.subdivision = {}

        root = Path(root_path)
        logging.debug('Building polygon index from "%s"', root)
        for path in root.rglob('*.poly'):
            codes = path.stem.split("-", maxsplit=2)

            country_code = get_country_code(codes[0])
            if not country_code:
                logging.debug('File "%s" does not contain country code in the name - skipping',
                              path)
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
        self.country[country_code] = Country(iso_code=country_code, coordinates=parse_poly_file(poly_path))

    def _add_subdivision(self, country_code: str, subdivision_code: str, poly_path: Path):
        iso_code = "-".join([country_code, subdivision_code])

        if not country_code in self.country:
            self.country[country_code] = Country(iso_code=country_code)

        self.country[country_code].add_subdivision(iso_code=iso_code, coordinates=parse_poly_file(poly_path))

    def select_regions(self, regions: list[str]) -> list[Region]:
        """Select regions from index according to the given list of regions.
        Regions can be specified by:
        - country code (country is returned)
        - country wildcard ie PL-* (all subdivisions of a country are returned)
        - subdivision code (subdivision is returned)
        """
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
                if country.coords:
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
                    raise ValueError(
                        f'Missing border definitions for subdivision {region} '
                        f'in country {country.name}'
                    )

        return result
