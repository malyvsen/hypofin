def annual_to_monthly(annual_return: float) -> float:
    return (1 + annual_return) ** (1 / 12) - 1
