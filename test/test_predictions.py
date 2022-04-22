from chalicelib.predictions import stocks


def test_stocks():
    predictions = stocks()
    example_returns = predictions.return_source.return_sources[
        0
    ].premium_source.example_returns
    assert len(example_returns) > 20 * 12
    assert -0.5 < example_returns.min() < 0
    assert 0 < example_returns.max() < 0.5
