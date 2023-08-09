import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from hypofin.caching import refresh_daily


@dataclass(frozen=True)
class BondYield:
    first_year: float
    inflation_premium: float

    @classmethod
    @refresh_daily
    def polish_four_year(cls):
        response = requests.get(
            "https://www.obligacjeskarbowe.pl/oferta-obligacji/obligacje-4-letnie-coi"
        )
        text = (
            BeautifulSoup(response.text, features="lxml")
            .find("strong", string="Oprocentowanie:")
            .find_next_sibling()
            .text.strip()
        )
        regex = (
            r"(\d+),(\d+)%, w kolejnych rocznych okresach odsetkowych: "
            r"marża (\d+),(\d+)% \+ inflacja, z wypłatą odsetek co roku"
        )
        groups = re.match(regex, text).groups()

        def value(whole: str, fractional: str):
            return float(f"{whole}.{fractional}") / 100

        return cls(
            first_year=value(whole=groups[0], fractional=groups[1]),
            inflation_premium=value(whole=groups[2], fractional=groups[3]),
        )
