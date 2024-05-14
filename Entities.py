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
    dates: list[datetime.date]
    rors: list[float]

    def __init__(self, dates: list[datetime.date] = None, rors: list[float] = None) -> None:
        self.dates = dates or []
        self.rors = rors or []

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
    omega_score: float
    sharpe_ratio: float
    overall_score: float
    max_drawdown: float
    max_drawdown_length: int
    max_drawdown_duration: int

    def __init__(self, name: str, fund_name: str, timeseries: Timeseries, omega_score=None,
                 sharpe_ratio=None, overall_score=None, max_drawdown=None, max_drawdown_length=None,
                 max_drawdown_duration=None) -> None:
        self.name = name
        self.fund_name = fund_name
        self.timeseries = timeseries
        self.omega_score = omega_score or 0
        self.sharpe_ratio = sharpe_ratio or 0
        self.overall_score = overall_score or 0
        self.max_drawdown = max_drawdown or 0
        self.max_drawdown_length = max_drawdown_length or 0
        self.max_drawdown_duration = max_drawdown_duration or 0


@dataclass
class Cluster:
    """
    Contains information for a cluster of Managers.

    Instance Attributes:
    - managers: the set of Managers in this Cluster
    - head: head Manager in this Cluster
    - TODO: add a correlation matrix for all managers in Cluster?
    """

    managers: set[Manager]
    head: Manager
