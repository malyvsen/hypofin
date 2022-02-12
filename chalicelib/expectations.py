import chalicelib.data as data


def inflation() -> float:
    return data.euro_inflation()


def bond_returns() -> float:
    return data.bond_yield()


def stock_returns() -> float:
    return inflation() + 1 / data.global_cape_ratio()
