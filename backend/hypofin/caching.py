from cachetools import TTLCache, cached


def refresh_daily(function):
    return cached(TTLCache(maxsize=float("inf"), ttl=24 * 60 * 60))(function)
