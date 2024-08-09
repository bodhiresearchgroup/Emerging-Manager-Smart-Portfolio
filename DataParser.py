"""
This file parses a CSV with given filepath to create a data object containing manager info.

Each CSV must adhere to the specific headers:
Manager    Fund    Date    Change

The date format used in the 'Date' column of all CSVs is written below in the constant variable CSV_DATETIME_FORMAT.
This format MUST apply to the CSV being parsed.
Formatting reference: https://docs.python.org/3/library/time.html#time.strftime

CSV_TYPE_FORMAT refers to the CSV column name containing the decimal ror value.

All functions assume the CSV has NO missing values!
"""

from Entities import Timeseries
import pandas as pd
from datetime import datetime

CSV_DATETIME_FORMAT = '%Y-%m-%d'
CSV_TYPE_FORMAT = {'Change': 'float64'}

class DataParser:
    """Data Access Object that contains information parsed from monthly ror CSVs.

    Instance Attributes:
    - path: filepath to CSV
    - manager_name: name of the manager in the CSV
    - fund_name: name of the fund in the CSV
    - time_series: a list of Ror entities, parsed from CSV
    """

    path: str
    manager_name: str
    program_name: str
    time_series: Timeseries

    def __init__(self, path: str, manager_name=None, program_name=None, time_series=None):
        self.path = path
        self.manager_name = manager_name or ''
        self.program_name = program_name or ''
        self.time_series = time_series or []
    
    def get_timeseries(self, start_date=None, end_date=None):
        """
        Parses CSV with filepath self.path and updates self.manager_name, self.program_name, and self.time_series
        with parsed information, optionally filtering by start and end date.

        Parameters:
            start_date: Start date for filtering (inclusive), a string in 'YYYY-MM-DD' format.
            end_date: End date for filtering (inclusive), a string in 'YYYY-MM-DD' format.

        Returns:
            Timeseries: Timeseries object containing dates and rors for the fund.
        """
        df = pd.read_csv(self.path, header=0)
        df = df.astype(CSV_TYPE_FORMAT)  # Prev: Ensure the 'Change' column is converted correctly
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Get manager and program name from first row
        self.manager_name = df.iloc[0, 0]
        self.program_name = df.iloc[0, 1]
        
        if start_date:
            df = df[df['Date'] >= start_date]
        if end_date:
            df = df[df['Date'] <= end_date]

        dates = df['Date'].tolist()
        rors = df['Change'].tolist()
        time_series = Timeseries(dates=dates, rors=rors)

        self.time_series = time_series
        return self.time_series
