from bs4 import BeautifulSoup
from cachetools import cached, TTLCache
import pandas as pd
import re
import requests
import yfinance as yf


@cached(cache=TTLCache(maxsize=1, ttl=24 * 60 * 60))
def global_cape_ratio() -> float:
    return pd.read_html("https://siblisresearch.com/data/world-cape-ratio/")[0][
        "Global Stock Markets CAPE Ratio"
    ][0]


@cached(cache=TTLCache(maxsize=1, ttl=24 * 60 * 60))
def euro_inflation() -> float:
    text_percent = (
        pd.read_html(
            "https://www.rateinflation.com/inflation-rate/euro-area-historical-inflation-rate/"
        )[0]["Annual"]
        .dropna()
        .iloc[0]
    )
    assert text_percent[-1] == "%"
    return float(text_percent[:-1]) / 100


@cached(cache=TTLCache(maxsize=1, ttl=24 * 60 * 60))
def bond_yield() -> float:
    html = requests.get(
        "http://www.worldgovernmentbonds.com/country/united-states/"
    ).text
    text = BeautifulSoup(html, features="lxml").text
    text_percent = re.findall(
        "The United States 10Y Government Bond has a (\d+\.\d+)% yield.", text
    )[0]
    return float(text_percent) / 100


@cached(cache=TTLCache(maxsize=1, ttl=24 * 60 * 60))
def stock_prices() -> pd.Series:
    return yf.Ticker("^GSPC").history(period="max", interval="1mo")["Close"]
