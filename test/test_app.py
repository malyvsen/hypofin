import json
from app import response
from chalicelib import User, countries


def test_netherlands():
    user = User(
        risk_preference=36,
        monthly_savings=5,
        goal_price=230,
        current_savings=180,
        country=countries["netherlands"],
    )
    test_me = response(user)
    assert len(test_me["aggregate_trajectories"]) == 4
    assert set(test_me.keys()) == {
        "aggregate_trajectories",
        "example_trajectories",
        "allocation",
    }


def test_poland():
    user = User(
        risk_preference=36,
        monthly_savings=5,
        goal_price=230,
        current_savings=180,
        country=countries["poland"],
    )
    test_me = response(user)
    assert len(test_me["aggregate_trajectories"]) == 4
    assert set(test_me.keys()) == {
        "aggregate_trajectories",
        "example_trajectories",
        "allocation",
    }


def test_impossible_goal():
    user = User(
        risk_preference=36,
        monthly_savings=5,
        goal_price=999999,
        current_savings=180,
        country=countries["netherlands"],
    )
    response(user)


def test_serialization():
    user = User(
        risk_preference=36,
        monthly_savings=5,
        goal_price=230,
        current_savings=180,
        country=countries["netherlands"],
    )
    test_me = response(user)
    json.dumps(test_me)
