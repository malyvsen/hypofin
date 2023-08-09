from datetime import date

import numpy as np
import pandas as pd


def prices_to_returns(prices: pd.Series):
    return prices.iloc[1:] / prices.shift(1).iloc[1:] - 1


def returns_to_prices(initial_date: date, initial_price: float, returns: pd.Series):
    if initial_date >= returns.index.min():
        raise ValueError("The initial date must be before the returns series starts")
    return pd.Series(
        index=[initial_date] + list(returns.index),
        data=[initial_price] + list(initial_price * np.cumprod(returns.values + 1)),
    )


def annual_to_monthly(
    annual_return: float | np.ndarray | pd.Series | pd.DataFrame,
) -> float | np.ndarray | pd.Series | pd.DataFrame:
    return (1 + annual_return) ** (1 / 12) - 1
