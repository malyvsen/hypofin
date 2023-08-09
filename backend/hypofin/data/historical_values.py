from datetime import date, timedelta
from io import BytesIO
from zipfile import ZipFile

import pandas as pd
import requests
import yfinance as yf

from hypofin.caching import refresh_daily

PLN_CONCEPTION = date(year=1995, month=1, day=1)


@refresh_daily
def historical_prices_pln(yfinance_code: str):
    """The historical prices of a security, in PLN, monthly."""
    return (
        (historical_prices_usd(yfinance_code) * historical_usd_pln())
        .rename(f"{yfinance_code} (PLN)")
        .dropna()
    )


def historical_prices_usd(yfinance_code: str) -> pd.Series:
    """The historical prices of a security, in USD, monthly."""
    # use open instead of close price to match with currency rates
    data = yf.Ticker(yfinance_code).history(period="max", interval="1mo")["Open"]
    return pd.Series(
        name=f"{yfinance_code} (USD)", index=data.index.date, data=data.values
    )


def historical_usd_pln() -> pd.Series:
    """The value of 1 USD in PLN, monthly."""
    data = pd.read_csv(
        "https://stooq.com/q/d/l/?s=usdpln&i=m", parse_dates=["Date"], index_col="Date"
    )["Close"]
    # add timedelta to match with historical prices
    return pd.Series(
        name="USD/PLN", index=data.index.date + timedelta(days=1), data=data.values
    )[PLN_CONCEPTION:]


@refresh_daily
def historical_inflation_pln() -> pd.Series:
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
            for index, value in selected.loc[str(PLN_CONCEPTION.year) :]
            .dropna()
            .items()
        }
    )
