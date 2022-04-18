from bs4 import BeautifulSoup
from datetime import date
from io import BytesIO
import numpy as np
import pandas as pd
import re
import requests
from typing import List
import yfinance as yf
from zipfile import ZipFile

from .return_utils import annual_to_monthly


def global_cape_ratio() -> float:
    return pd.read_html("https://siblisresearch.com/data/world-cape-ratio/")[0][
        "Global Stock Markets CAPE Ratio"
    ][0]


def historical_inflation(country: str) -> pd.Series:
    """The yearly inflation since 1960"""
    response = requests.get(
        "https://api.worldbank.org/v2/en/indicator/FP.CPI.TOTL.ZG",
        params=dict(downloadformat="csv"),
    )
    zip_data = BytesIO(response.content)
    with ZipFile(zip_data) as zip_file:
        file_name = next(name for name in zip_file.namelist() if name.startswith("API"))
        with zip_file.open(file_name) as csv_file:
            data = pd.read_csv(csv_file, header=2)
    data["Country Name"] = data["Country Name"].str.lower()
    selected = data.set_index("Country Name").loc[country]
    return pd.Series(
        {int(index): value / 100 for index, value in selected.iloc[3:-1].iteritems()}
    )


def euro_inflation_predictions():
    """Monthly inflation predictions for the near future."""
    current_forecasts = pd.read_html(
        "https://www.ecb.europa.eu/stats/ecb_surveys/survey_of_professional_forecasters/html/table_hist_hicp.en.html"
    )[0].iloc[-1]
    return gather_inflation_predictions(
        [
            current_forecasts[key] / 100
            for key in [
                "Current calendar year",
                "Next calendar year",
                "Calendar yearafter next",
            ]
        ]
    )


def pln_inflation_predictions():
    """Monthly inflation predictions for the near future."""
    tables = pd.read_html(
        "https://www.nbp.pl/home.aspx?f=/polityka_pieniezna/dokumenty/projekcja_inflacji.html"
    )
    field_name = "Inflacja CPI r/r (%)"
    inflation_table = next(
        table
        for table in tables
        if table[table.columns[0]].iloc[0] == field_name and len(table) > 2
    )
    predictions = inflation_table.set_index(inflation_table.columns[0]).loc[field_name]
    return gather_inflation_predictions(
        [prediction / 1000 for prediction in predictions]
    )


def gather_inflation_predictions(per_calendar_year: List[float]) -> np.array:
    end_of_year = date(year=date.today().year, month=12, day=31)
    months_left = (end_of_year - date.today()).days // 30
    return np.array(
        [annual_to_monthly(per_calendar_year[0])] * months_left
        + [
            annual_to_monthly(yearly)
            for yearly in per_calendar_year[1:]
            for _ in range(12)
        ]
    )


def bond_yield(country: str) -> float:
    html = requests.get(f"http://www.worldgovernmentbonds.com/country/{country}/").text
    text = BeautifulSoup(html, features="lxml").text
    text_percent = re.findall(
        "10Y Government Bond has a (-{0,1}\\d+\\.\\d+)% yield.", text
    )[0]
    return float(text_percent) / 100


def default_probability(country: str) -> float:
    """The 5-year probability of default"""
    html = requests.get(f"http://www.worldgovernmentbonds.com/country/{country}/").text
    text = BeautifulSoup(html, features="lxml").text
    text_percent = re.findall(
        "Current 5-Years Credit Default Swap quotation is [\\d\\.]+ and implied probability of default is (\\d+\\.\\d+)%\\.",
        text,
    )[0]
    return float(text_percent) / 100


def stock_prices() -> pd.Series:
    return yf.Ticker("^GSPC").history(period="max", interval="1mo")["Close"]
