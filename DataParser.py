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

class MonthlyRor:
    """Data Access Object that contains information parsed from monthly ror CSVs.

    Instance Attributes:
    - path: filepath to CSV
    - manager_name: name of the manager in the CSV
    - fund_name: name of the fund in the CSV
    - time_series: a list of Ror entities, parsed from CSV
    """

    path: str
    manager_name: str
    fund_name: str
    time_series: Timeseries

    def __init__(self, path: str, manager_name=None, fund_name=None, time_series=None):
        self.path = path
        self.manager_name = manager_name or ''
        self.fund_name = fund_name or ''
        self.time_series = time_series or []
    
    def get_timeseries(self, start_date=None, end_date=None):
            """Parses CSV with filepath self.path and updates self.manager_name, self.fund_name, and self.time_series
            with parsed information, optionally filtering by start and end date.

            :param start_date: Start date for filtering (inclusive), as a string in 'YYYY-MM-DD' format.
            :param end_date: End date for filtering (inclusive), as a string in 'YYYY-MM-DD' format.
            :return: Timeseries
            """
            df = pd.read_csv(self.path, header=0)
            df = df.astype(CSV_TYPE_FORMAT)  # Ensure the 'Change' column is converted correctly
            df["date"] = pd.to_datetime(df["Date"])
            #print(df)
            if start_date:
                df = df[df['date'] >= start_date]
            if end_date:
                df = df[df['date'] <= end_date]

            time_series = Timeseries()
            for row in df.itertuples(index=False, name=None):
                date = datetime.strptime(row[2], CSV_DATETIME_FORMAT).date()
                time_series.dates.append(date)
                time_series.rors.append(row[3])

                # Update manager_name and fund_name from the first row if they are empty
                if self.manager_name == '':
                    self.manager_name = row[0]  # Assuming the first element is the manager name
                if self.fund_name == '':
                    self.fund_name = row[1]  # Assuming the second element is the fund name

            self.time_series = time_series
            return self.time_series
    # def get_timeseries(self):
    #     """ Parses CSV with filepath self.path and updates self.manager_name, self.fund_name, and self.time_series
    #     with parsed information.

    #     :return: Timeseries
    #     """
    #     df = pd.read_csv(self.path, header=0)


    #     df.astype(CSV_TYPE_FORMAT)  # convert ror column values from str to float

    #     time_series = Timeseries()
    #     for row in df.itertuples(index=False, name=None):  # each row is a (manager, fund, date, ror) tuple
    #         date = (datetime.strptime(row[2], CSV_DATETIME_FORMAT)).date()  # formats date str into datetime.date obj.
    #         time_series.dates.append(date)
    #         time_series.rors.append(row[3])

    #         if self.manager_name == '':
    #             self.manager_name = row[1]
    #         if self.fund_name == '':
    #             self.fund_name = row[1]

    #     self.time_series = time_series
    #     return self.time_series
