"""
This file contains all Entity classes.
"""

from datetime import datetime
from dataclasses import dataclass
import pandas as pd


@dataclass
class Timeseries:
    """
    A simple class for representing a timeseries.
    """
    data: pd.Series

    def __init__(self, data=None, dates=None, rors=None) -> None:
        if data is not None:
            self.data = data
        else:
            if dates is None:
                dates = []
            if rors is None:
                rors = []
            self.data = pd.Series(rors, index=dates)

    def get_dates(self):
        if not isinstance(self.data.index, pd.DatetimeIndex):
            print("Index is not a DatetimeIndex. The current index is:")
            print(self.data.index)
        return self.data.index.date
    
    def get_rors(self):
        return self.data.values
    
    def get_ror_by_date(self, date):
        date = pd.Timestamp(date)
        return self.data.get(date, None)

    def add_to_series(self, date: datetime, ror: float):
        """
        Add a new date and rate of return to the series.

        Parameters:
            date: A datetime object representing the date.
            ror: A float representing the rate of return for the date.
        """
        # Convert date to pandas.Timestamp for compatibility with the index
        timestamp = pd.Timestamp(date)
        
        # Check if the date already exists in the series
        if timestamp in self.data.index:
            # Update the existing value 
            self.data[timestamp] = ror
        else: # Add new entry
            self.data.at[timestamp] = ror
            # Re-sort the index to maintain chronological order
            self.data.sort_index(inplace=True)

    def get_len(self):
        return len(self.data)


class Program:
    """
    Contains all necessary information for an emerging manager.
    TODO: Prev: add equality functions? Like to see whether Manager 1 > Manager 2. Maybe based on overall_score.

    Instance Attributes:
    - name: the name of the program
    - manager: the name of the manager
    - timeseries: monthly ror timeseries
    - test_timeseries: validation data used to test weights
    - omega_score: omega score
    - sharpe_ratio: modified sharpe ratio
    - overall_score: manager's overall score (before normalization)
    - overall_weight: manager's overall score (after normalization)
    - max_drawdown: manager's maximum drawdown
    - max_drawdown_length: length (in months) of maximum drawdown. Measured from peak to trough.
    - max_drawdown_duration: duration/recovery time (in months) of maximum drawdown
    """
    name: str
    manager: str
    full_timeseries: Timeseries
    timeseries: Timeseries
    test_timeseries: Timeseries
    omega_score: float
    sharpe_ratio: float
    scores: list
    overall_score: float
    overall_weight:float
    vol_weight:float
    max_drawdown: float
    max_drawdown_length: int
    max_drawdown_duration: int
    pop_to_drop: float
    gain_to_pain: float

    def __init__(self, manager: str, fund_name: str,
                 full_timeseries: Timeseries, timeseries: Timeseries, test_timeseries=None) -> None:
        self.name = fund_name
        self.manager = manager
        self.full_timeseries = full_timeseries
        self.timeseries = timeseries
        self.test_timeseries = test_timeseries or None
        self.omega_score = None
        self.sharpe_ratio = None
        self.scores = []
        self.overall_score = None
        self.overall_weight = None
        self.vol_weight = None
        self.max_drawdown = None
        self.max_drawdown_length = None
        self.max_drawdown_duration = None
        self.pop_to_drop = None
        self.gain_to_pain = None

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
    - programs: the set of Programs in this Cluster
    - head: head Program in this Cluster
    - TODO: Prev: add a correlation matrix for all programs in Cluster?
    """

    programs: set
    head: Program

    def __init__(self, head_program, programs) -> None:
        self.head = head_program
        self.programs = programs
