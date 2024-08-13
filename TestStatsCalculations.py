"""
This file contains tests for the statistical calculations performed in 'StatsCalculations.py'.
"""

import pytest
from DataParser import DataParser
from StatsCalculations import calc_drawdown_series, calc_max_drawdown, \
    calc_max_drawdown_length, calc_max_drawdown_duration, calc_omega_score, \
    calc_cumulative_returns, calc_ann_return, calc_sharpe_ratio

TEST_FOLDER = 'tests'
TEST_FILE = 'Test Program.csv'

class TestStatsCalculations:


    def setup_method(self):
        monthly_ror_dao = DataParser(TEST_FOLDER + '/' + TEST_FILE)
        timeseries = monthly_ror_dao.get_timeseries()
        self.rors = timeseries.get_rors()


    def test_calc_omega_score(self) -> None:
        """Tests the Omega ratio of a test manager."""
        omega_ratio = calc_omega_score(self.rors)
        assert pytest.approx(omega_ratio, 1e-3) == 1.284


    def test_calc_cumulative_returns(self) -> None:
        """Tests the cumulative returns of a test manager."""
        cumulative_returns = calc_cumulative_returns(self.rors)
        assert pytest.approx(cumulative_returns, 1e-2) == [-0.0251, 0.0627, 0.1120, 0.1340, 0.0559, -0.0167, -0.1036,
                                                            -0.0380, -0.0186, 0.0222, -0.0758, 0.0111, 0.0783]


    def test_calc_ann_return(self) -> None:
        """Tests the annual return of a test manager."""
        annualized_return = calc_ann_return(self.rors)
        assert pytest.approx(annualized_return, 1e-2) == 0.07209


    def test_calc_sharpe_ratio(self) -> None:
        """Tests the Sharpe ratio of a test manager."""
        sharpe_ratio = calc_sharpe_ratio(self.rors)
        assert pytest.approx(sharpe_ratio, 1e-2) == 0.3124


    def test_calc_drawdown_series(self) -> None:
        """Tests the return drawdown series of a test manager. Testing values were calculated by hand and Excel formulas."""
        drawdowns = calc_drawdown_series(self.rors)
        assert pytest.approx(drawdowns, 1e-3) == [-0.0251, 0, 0, 0, -0.0688, -0.1329, -0.2095, -0.1517, -0.1345,
                                                    -0.0985, -0.185, -0.1084, -0.0491]


    def test_calc_max_drawdown(self) -> None:
        """Tests the max drawdown of a test manager."""
        max_drawdown = calc_max_drawdown(self.rors)
        assert pytest.approx(max_drawdown, 1e-3) == -0.209521156


###
# Currently unused functions
###

# def test_calc_max_drawdown_length() -> None:
#     """Tests the max drawdown length of a test manager."""
#     monthly_ror_dao = DataParser(TEST_FOLDER + '/' + TEST_FILE)
#     timeseries = monthly_ror_dao.get_timeseries()

#     max_drawdown_length = calc_max_drawdown_length(timeseries.get_rors())
#     assert max_drawdown_length == 6


# def test_calc_max_drawdown_duration() -> None:
#     """Tests the max drawdown length of a test manager."""
#     monthly_ror_dao = DataParser(TEST_FOLDER + '/' + TEST_FILE)
#     timeseries = monthly_ror_dao.get_timeseries()

#     max_drawdown_duration = calc_max_drawdown_duration(timeseries.get_rors())
#     assert max_drawdown_duration == 6

if __name__ == '__main__':
    pytest.main(['TestStatsCalculations.py', '-v'])