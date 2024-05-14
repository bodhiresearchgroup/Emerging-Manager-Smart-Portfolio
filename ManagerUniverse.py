"""
This file performs the following tasks:

1. Initialize an empty ManagerUniverse, the core simulation for our algorithm.

2. Parse timeseries data and other information provided in the given data folder
to create Manager objects (which populate the Universe and can be accessed through the Universe).

3. TODO: Perform various statistical operations on all Managers in the Universe, updating their attributes.

4. TODO: Create Clusters, which are groupings of Managers based on the results of the above statistical operations.
These Clusters are accessed through the Universe.

5: TODO: Display results
"""

import os
from Entities import Manager, Cluster
from DataParser import MonthlyRor
from StatsCalculations import calc_omega_score, calc_sharpe_ratio, calc_overall_score, calc_pearson_correlation, \
    calc_max_drawdown, calc_max_drawdown_length, calc_max_drawdown_duration


class ManagerUniverse:
    """ Maintains all entities."""
    _managers: list[Manager]
    _clusters: list[Cluster]

    def __init__(self) -> None:
        """Initialize a new emerging managers universe.
        The universe starts with no entities.
        """
        self._managers = []
        self._clusters = []

    def populate_managers(self, path: str) -> None:
        """ Create Manager objects from all CSVs in provided folder. Add them to Universe.

        :param path: filepath to folder
        """
        for filename in os.listdir(path):
            monthly_ror_dao = MonthlyRor(path + '/' + filename)  # complete filepath to CSV from source
            monthly_ror_timeseries = monthly_ror_dao.get_timeseries()
            manager_name = monthly_ror_dao.manager_name
            fund_name = monthly_ror_dao.fund_name

            if manager_name not in self._managers:
                new_manager = Manager(manager_name, fund_name, monthly_ror_timeseries)
                self._managers.append(new_manager)

            print(f"Added {manager_name}")

    def perform_manager_stats_calculations(self):
        for manager in self._managers:
            rors = manager.timeseries.rors
            manager.omega_score = calc_omega_score(rors)
            if manager.omega_score is None:
                print(f"Could not calculate Omega score for {manager.name}")
            manager.sharpe_ratio = calc_sharpe_ratio(rors)
            if manager.omega_score is None:
                print(f"Could not calculate Sharpe ratio for {manager.name}")

            if len(rors) < 2:
                print(f"Could not perform drawdown analysis for {manager.name}")
            else:
                manager.max_drawdown = calc_max_drawdown(rors)
                manager.max_drawdown_length = calc_max_drawdown_length(rors)
                manager.max_drawdown_duration = calc_max_drawdown_duration(rors)
            manager.overall_score = calc_overall_score(manager)

    def populate_clusters(self):
        for manager in self._managers:
            for other_manager in self._managers:
                if other_manager.name != manager.name:
                    corr = calc_pearson_correlation(manager.timeseries, other_manager.timeseries)
                    if corr > 0.65:
                        print(f'{manager.name} - {other_manager.name} corr: {corr}')


if __name__ == '__main__':
    returns_folder = 'manager_returns'
    universe = ManagerUniverse()

    print("Initializing Universe...\n")
    universe.populate_managers(returns_folder)
    print("\nAdded all Managers. Performing calculations...")
    universe.perform_manager_stats_calculations()
    print("\nFinished calculations. Correlating...")
    universe.populate_clusters()

