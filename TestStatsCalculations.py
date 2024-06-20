"""This file contains tests for the statistical calculations performed in 'StatsCalculations.py'.
"""

import pytest
from DataParser import MonthlyRor
from StatsCalculations import calc_drawdown_series, calc_max_drawdown, \
    calc_max_drawdown_length, calc_max_drawdown_duration

TEST_FOLDER = 'test'
TEST_FILE = 'Test_Manager.csv'


def test_calc_drawdown_series() -> None:
    """Tests the return drawdown series of a test manager. Testing values were calculated by hand and Excel formulas."""
    monthly_ror_dao = MonthlyRor(TEST_FOLDER + '/' + TEST_FILE)
    timeseries = monthly_ror_dao.get_timeseries()

    drawdowns = calc_drawdown_series(timeseries.rors)
    assert pytest.approx(drawdowns, 1.0001) == [0.0, 0.0, -0.0245, -0.0693, -0.0579, -0.0406, -0.0614,
                                                -0.0805, -0.0435, -0.0649]


def test_calc_max_drawdown() -> None:
    """Tests the max drawdown of a test manager."""
    monthly_ror_dao = MonthlyRor(TEST_FOLDER + '/' + TEST_FILE)
    timeseries = monthly_ror_dao.get_timeseries()

    max_drawdown = calc_max_drawdown(timeseries.rors)
    assert pytest.approx(max_drawdown, 1.0001) == -0.0805


def test_calc_max_drawdown_length() -> None:
    """Tests the max drawdown length of a test manager."""
    monthly_ror_dao = MonthlyRor(TEST_FOLDER + '/' + TEST_FILE)
    timeseries = monthly_ror_dao.get_timeseries()

    max_drawdown_length = calc_max_drawdown_length(timeseries.rors)
    assert max_drawdown_length == 6


def test_calc_max_drawdown_duration() -> None:
    """Tests the max drawdown length of a test manager."""
    monthly_ror_dao = MonthlyRor(TEST_FOLDER + '/' + TEST_FILE)
    timeseries = monthly_ror_dao.get_timeseries()

    max_drawdown_duration = calc_max_drawdown_duration(timeseries.rors)
    assert max_drawdown_duration == 6

if __name__ == '__main__':
    pytest.main(['TestStatsCalculations.py', '-v'])