import re
from dataclasses import dataclass
from io import BytesIO
from zipfile import ZipFile

import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup


def quotes(yfinance_code) -> pd.Series:
    return yf.Ticker(yfinance_code).history(period="max", interval="1mo")["Close"]


def global_cape_ratio() -> float:
    return pd.read_html("https://siblisresearch.com/data/world-cape-ratio/")[0][
        "Global Stock Markets CAPE Ratio"
    ][0]


def historical_inflation() -> pd.Series:
    """The yearly inflation of PLN since its conception in 1995."""
    response = requests.get(
        "https://api.worldbank.org/v2/en/indicator/FP.CPI.TOTL.ZG",
        params=dict(downloadformat="csv"),
    )
    zip_data = BytesIO(response.content)
    with ZipFile(zip_data) as zip_file:
        file_name = next(name for name in zip_file.namelist() if name.startswith("API"))
        with zip_file.open(file_name) as csv_file:
            data = pd.read_csv(csv_file, header=2)
    selected = data.set_index("Country Name").loc["Poland"]
    return pd.Series(
        {
            int(index): value / 100
            for index, value in selected.loc["1995":].dropna().items()
        }
    )


@dataclass(frozen=True)
class BondYield:
    first_year: float
    inflation_premium: float

    @classmethod
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
