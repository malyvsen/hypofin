from bs4 import BeautifulSoup
from io import BytesIO
import pandas as pd
import re
import requests
import yfinance as yf
from zipfile import ZipFile


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
