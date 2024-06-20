
"""
This file contains all Entity classes.
"""

from datetime import datetime
from dataclasses import dataclass


@dataclass
class Timeseries:
    """
    A simple class for representing a timeseries.
    """
    dates: list
    rors: list

    def __init__(self, dates: list = None, rors: list= None) -> None:
        self.dates = dates or []
        self.rors = rors or []
        self.weighted_rors = []

    def add_to_series(self, date: datetime.date, ror: float):
        self.dates.append(date)
        self.rors.append(ror)


class Manager:
    """
    Contains all necessary information for an emerging manager.
    TODO: add equality functions? Like to see whether Manager 1 > Manager 2. Maybe based on overall_score.

    Instance Attributes:
    - name: the name of the manager
    - fund_name: fund name of the manager
    - monthly_ror: monthly ror timeseries
    - omega_score: omega score
    - sharpe_ratio: modified sharpe ratio
    - overall_score: manager's overall score
    - max_drawdown: manager's maximum drawdown
    - max_drawdown_length: length (in months) of maximum drawdown. Measured from peak to trough.
    - max_drawdown_duration: duration/recovery time (in months) of maximum drawdown
    """

    name: str
    fund_name: str
    timeseries: Timeseries
    test_timeseries: Timeseries
    omega_score: float
    sharpe_ratio: float
    overall_score: float
    # overall_weights is after normalization
    overall_weight:float
    vol_weight:float
    max_drawdown: float
    max_drawdown_length: int
    max_drawdown_duration: int
    weighted_returns: float

    def __init__(self, name: str, fund_name: str, 
                 timeseries: Timeseries, test_timeseries: Timeseries, 
                 omega_score=None, sharpe_ratio=None, max_drawdown=None, max_drawdown_length=None,
                 max_drawdown_duration=None) -> None:
        self.name = name
        self.fund_name = fund_name
        self.timeseries = timeseries
        self.test_timeseries = test_timeseries
        self.omega_score = omega_score or 0
        self.sharpe_ratio = sharpe_ratio or 0
        # self.overall_score = overall_score or 0
        self.max_drawdown = max_drawdown or 0
        self.max_drawdown_length = max_drawdown_length or 0
        self.max_drawdown_duration = max_drawdown_duration or 0
        self.overall_weight = 1
        self.vol_weight = 1


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __hash__(self):

        return hash(self.name)


@dataclass
class Cluster:
    """
    Contains information for a cluster of Managers.

    Instance Attributes:
    - managers: the set of Managers in this Cluster
    - head: head Manager in this Cluster
    - TODO: add a correlation matrix for all managers in Cluster?
    """

    managers: set([])
    head: Manager

    def __init__(self, head_manager, managers) -> None:
        self.managers = managers
        self.head = head_manager
