from app import response
from cProfile import Profile
from pstats import Stats, SortKey


payload = {
    "risk_preference": 36,
    "monthly_savings": 5,
    "goal_price": 1300,
    "current_savings": 180,
    "country": "netherlands",
}
_ = response(payload)
with Profile() as profile:
    response(payload)
stats = Stats(profile).sort_stats(SortKey.CUMULATIVE)
_ = stats.print_stats(16)
