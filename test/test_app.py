from app import response


def test_response_fields():
    payload = {
        "risk_preference": 36,
        "monthly_savings": 5,
        "goal_price": 1300,
        "current_savings": 180,
        "tax_system": "netherlands",
    }
    test_me = response(payload)
    assert len(test_me["strata"]) == 3
    assert set(test_me.keys()) == {
        "strata",
        "bank_variant",
        "example_evolutions",
        "allocation",
    }