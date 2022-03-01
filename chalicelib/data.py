from bs4 import BeautifulSoup
import pandas as pd
import re
import requests
import yfinance as yf


def global_cape_ratio() -> float:
    return pd.read_html("https://siblisresearch.com/data/world-cape-ratio/")[0][
        "Global Stock Markets CAPE Ratio"
    ][0]


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


def bond_yield() -> float:
    html = requests.get("http://www.worldgovernmentbonds.com/country/germany/").text
    text = BeautifulSoup(html, features="lxml").text
    text_percent = re.findall(
        "10Y Government Bond has a (-{0,1}\\d+\\.\\d+)% yield.", text
    )[0]
    return float(text_percent) / 100


def stock_prices() -> pd.Series:
    return yf.Ticker("^GSPC").history(period="max", interval="1mo")["Close"]
