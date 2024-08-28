"""
This file contains the following functions:

1. Initialize an empty ManagerUniverse, the core simulation for our algorithm.

2. Parse timeseries data and other information provided in the given data folder
to create Program objects (which populate the Universe and can be accessed through the Universe).

3. Perform various statistical operations on all Programs in the Universe, updating their attributes.

4. Create Clusters, which are groupings of Programs based on the results of the above statistical operations.
These Clusters are accessed through the Universe.

5: Calculate weights for each Program based on its performance relative to its cluster peers.
"""
import os
from Entities import Program, Cluster
from DataParser import DataParser
from StatsCalculations import *
from scipy.stats import percentileofscore
from itertools import chain
import numpy as np

import pandas as pd

OMEGA_ANNUALIZED_THRESHOLD = 0.01  

class ManagerUniverse:
    """ Maintains all entities.
    
    Instance Attributes:
    - _core_programs: The emerging managers that we are interested in buiding clusters around.
    - _other_programs: The other managers in the universe.
    - correlation_value: The minimum correlation between each program in a cluster.
    """
    _core_programs: list
    _other_programs: list
    _clusters: list
    # Prev: add cluster definite corr?
    correlation_value: float

    def __init__(self, correlation_value=0.5) -> None:
        """Initialize a new Emerging Managers universe.
        The universe starts with no entities.
        """
        self._core_programs = []
        self._other_programs = []
        self._clusters = []
        self.corr = correlation_value

    def populate_programs(self, path: str, is_core: bool, start_date=None, end_date=None, test_start_date=None, test_end_date=None) -> None:
        """
        Create Program objects from all CSVs in provided folder. Add them to Universe.

        Parameters:
            path: Filepath to data folder.
            start_date: Start date for filtering (inclusive), a string in 'YYYY-MM-DD' format.
            end_date: End date for filtering (inclusive), a string in 'YYYY-MM-DD' format.
            test_start_date: Start date for validation data.
            test_end_date: End date for validation data.
        """
        for i, filename in enumerate(os.listdir(path)):
            if filename == '.DS_Store':
                continue
            # print(i, filename)

            dp = DataParser(path + '/' + filename)  # complete filepath to CSV from source

            timeseries = dp.get_timeseries(start_date=start_date, end_date=end_date)
            if timeseries.get_len() < 2:
                print(f'Insufficient data for {dp.program_name}.')
                continue

            test_timeseries = dp.get_timeseries(start_date=test_start_date, end_date=test_end_date)
            if test_timeseries.get_len() < 1:
                test_timeseries = None

            manager_name: str = dp.manager_name
            fund_name: str = dp.program_name

            # Generate a new Program object for each CSV and append this new program into the universe program list.
            new_program = Program(manager_name, fund_name, timeseries, test_timeseries)
            if is_core:
                self._core_programs.append(new_program)
            else:
                self._other_programs.append(new_program)


    def perform_program_stats_calculations(self):
        """
        Performs all stats calculations on each program in the universe.
        """
        dp = DataParser("data/sp500.csv")
        s_and_p = dp.get_timeseries()

        for program in chain(self._core_programs, self._other_programs):
            rors = program.timeseries.get_rors()
            program.omega_score = calc_omega_score(rors, OMEGA_ANNUALIZED_THRESHOLD)
            if program.omega_score is None:
                print(f"Could not calculate Omega score for {program.name}")
            program.sharpe_ratio = calc_sharpe_ratio(rors)
            if program.sharpe_ratio is None:
                print(f"Could not calculate Sharpe ratio for {program.name}")
            if len(rors) < 2:
                print(f"Could not perform drawdown analysis for {program.name}")
            else:
                program.max_drawdown = calc_weighted_drawdown_area(rors, False, True)
            program.pop_to_drop = calc_pop_to_drop(rors, 95, 5)
            program.gain_to_pain = calc_gain_to_pain(program.timeseries, s_and_p)
            
        # Flagged. Need to establish algorithm's behaviour when a score can't be calculated.


    def populate_clusters(self):
        """
        For each program, create a set that contains all programs with corr > 0.65.
        Then, create a cluster object that contains the head program and the set we just created. 
        Add this cluster into the cluster list.

        Prev: create eq and hash function for Program class?
        """
        for head in self._core_programs:
            cluster = set()
            cluster.add(head)
            for others in chain(self._core_programs, self._other_programs):
                if others.name != head.name:
                    # Get correlation between two program' synced rors
                    corr = calc_pearson_correlation(head.timeseries, others.timeseries)
                    if corr > self.corr:
                        cluster.add(others)
                
            new_cluster = Cluster(head, cluster)
            self._clusters.append(new_cluster)


    def ratings_df(self):
        """
        Assigns scores to each program based on performance relative to the others.

        Returns:
            pd.DataFrame: Pandas DataFrame of programs, performance measures, and scores.
        """
        program_score = []
        program_name = []
        program_omega_score = []
        program_sharpe_ratio = []
        program_maxdrawdown = []
        ratings_df = pd.DataFrame()
        
        # Calculate the performance of the each program relative to the others in its cluster
        for each_cluster in self._clusters:
            percentile_list = []
            
            omega_data = [program.omega_score for program in each_cluster.programs]
            head_omega_percentile = percentileofscore(omega_data, each_cluster.head.omega_score)
            percentile_list.append(head_omega_percentile)

            max_dd_data = [program.max_drawdown for program in each_cluster.programs]
            head_max_dd_percentile = percentileofscore(max_dd_data, each_cluster.head.max_drawdown)
            percentile_list.append(head_max_dd_percentile)

            sharpe_data = [program.sharpe_ratio for program in each_cluster.programs]
            head_sharpe_percentile = percentileofscore(sharpe_data, each_cluster.head.sharpe_ratio)
            percentile_list.append(head_sharpe_percentile)

            ptd_data = [program.pop_to_drop for program in each_cluster.programs]
            gtp_data = [program.gain_to_pain for program in each_cluster.programs]
            head_ptd_percentile = percentileofscore(ptd_data, each_cluster.head.pop_to_drop)
            head_gtp_percentile = percentileofscore(gtp_data, each_cluster.head.gain_to_pain)
            percentile_list.append((head_ptd_percentile + head_gtp_percentile)/2)

            # Calculate the program's overall, unnormalized performance score and store it in a list
            each_cluster.head.overall_score = self.assign_score(np.mean(percentile_list))
            program_score.append(each_cluster.head.overall_score)
            
            # Store each program's name and stats in lists
            program_name.append(each_cluster.head.name)
            program_omega_score.append(each_cluster.head.omega_score)
            program_sharpe_ratio.append(each_cluster.head.sharpe_ratio)
            program_maxdrawdown.append(each_cluster.head.max_drawdown)

        # Create dataframe 
        ratings_df = pd.DataFrame({
            "Name": program_name,
            "Omega Value": program_omega_score,
            "Sharpe Ratio": program_sharpe_ratio,
            "Max Drawdown": program_maxdrawdown,
            "Score": program_score
        })

        # Use the program names as the indices of the dataframe
        ratings_df.set_index("Name", inplace=True)

        # Normalize the overall program scores (from 0-100). 
        normalized_weights = program_score / np.sum(program_score)
        for i, program in enumerate(self._core_programs):
            program.overall_weight = normalized_weights[i]

        ratings_df["Weights"] = normalized_weights
    
        # Calculate volatility-based weights of each program
        self.calculate_vol_weights(ratings_df)

        return ratings_df
    
    
    def calculate_vol_weights(self, ratings_df):
        """
        Calculate volatility-based weights for each program.

        Parameters:
            ratings_df (pd.Dataframe): The dataframe that stores the weights.
        """
        program_volatility = []
        for program in self._core_programs:
            program_volatility.append(np.std(program.timeseries.get_rors()))
        
        # Invert the volatilities
        inv_vol_weights = [1 / vol if vol != 0 else 0 for vol in program_volatility]
        
        # Normalize the inverted volatilities
        total_inv_vol = sum(inv_vol_weights)
        normalized_vol_weights = [w / total_inv_vol if total_inv_vol !=0 else 0.0000001 for w in inv_vol_weights]
        
        normalized_vol_weights = normalized_vol_weights / np.sum(normalized_vol_weights)

        # Assign volatility scores to each program
        for i, program in enumerate(self._core_programs):
            program.vol_weight = normalized_vol_weights[i]
        # ratings_df["Vol Weights"] = normalized_vol_weights


    def assign_score(self, mean):
        """
        Assign an integer score from 1 - 3 based on the input.

        Parameters: 
            mean (float): A program's average performance from 0 - 100.

        Returns:
            int: A score from 1 - 3 based on the program's performance.
        """
        num_bins = 3
        bins = np.linspace(0, 100, num_bins + 1) 
        scores = list(range(1, num_bins + 1))   
        index = np.digitize(mean, bins, right=True)
        return scores[index - 1] 


    def original_portfolio(self):
        """
        Creates a dataframe of the rate of returns for each program.

        Returns:
            pd.DataFrame: Rate of returns. Columns are programs, rows are months.
        """
        program_df = pd.DataFrame({'Date': pd.to_datetime([])})
        
        for program in self._core_programs:
            df = pd.DataFrame({
                'Date': program.timeseries.get_dates(),
                f'{program.name}': program.timeseries.get_rors(),
            })
            program_df = pd.merge(program_df, df, on='Date', how='outer')
        
        program_df['Date'] = pd.to_datetime(program_df['Date'])
        program_df.set_index('Date', inplace=True)
        return program_df
    
    
    ####
    # Weighted Portfolios
    ####
    # FLAGGED. There is duplicate code below that may be mergeable. (Pass weight type as param?)

    def weighted_returns_portfolio(self, iter: bool):
        """
        Creates a dataframe of performance-weighted rate of returns for each program.

        Returns:
            pd.DataFrame: Weighted rate of returns. Columns are program, rows are months.
        """
        # Create a DataFrame to hold the weighted returns
        weighted_returns_df = pd.DataFrame({'Date': pd.to_datetime([])})
        
        for program in self._core_programs:
            # Calculate weighted returns for each program
            if iter:
                timeseries = program.test_timeseries
            else:
                timeseries = program.timeseries

            weighted_rors = program.overall_weight * timeseries.get_rors()
            weighted_program_df = pd.DataFrame({
                'Date': timeseries.get_dates(),
                f'{program.name} Weighted Returns': weighted_rors
            })
          
            # Merge this program's weighted returns into the main DataFrame
            weighted_returns_df = pd.merge(weighted_returns_df, weighted_program_df, on='Date', how='outer')
            
        weighted_returns_df['Date'] = pd.to_datetime(weighted_returns_df['Date'])
        weighted_returns_df.set_index('Date', inplace=True)
        return weighted_returns_df    
    
    
    def volatility_weighted_returns_portfolio(self, iter: bool):
        """
        Creates a dataframe of volatility-weighted returns for each program.

        Returns:
            pd.DataFrame: Weighted rate of returns. Columns are program, rows are months.
        """
        vol_weighted_returns_df = pd.DataFrame({'Date': pd.to_datetime([])})
        
        for program in self._core_programs:
            if iter:
                timeseries = program.test_timeseries
            else:
                timeseries = program.timeseries

            vol_weighted_rors = program.vol_weight * timeseries.get_rors()

            weighted_program_df = pd.DataFrame({
                'Date': timeseries.get_dates(),
                f'{program.name} Weighted Returns': vol_weighted_rors
            })
          
            vol_weighted_returns_df = pd.merge(vol_weighted_returns_df, weighted_program_df, on='Date', how='outer')
            
        vol_weighted_returns_df['Date'] = pd.to_datetime(vol_weighted_returns_df['Date'])
        vol_weighted_returns_df.set_index('Date', inplace=True)
        return vol_weighted_returns_df    


    def equal_weighted_returns_portfolio(self, iter: bool):
        """
        Creates a dataframe of equal-weighted returns for each program.

        Returns:
            pd.DataFrame: Equal-weighted rate of returns. Columns are program, rows are months.
        """
        weighted_returns_df = pd.DataFrame({'Date': pd.to_datetime([])})
        
        num_programs = len(self._core_programs)
        equal_weight = 1 / num_programs
        
        for program in self._core_programs:
            if iter:
                timeseries = program.test_timeseries
            else:
                timeseries = program.timeseries

            weighted_rors = equal_weight * timeseries.get_rors()  

            weighted_program_df = pd.DataFrame({
                'Date': timeseries.get_dates(),
                f'{program.name} Equal Weighted Returns': weighted_rors
            })
            
            weighted_returns_df = pd.merge(weighted_returns_df, weighted_program_df, on='Date', how='outer')
        
        weighted_returns_df['Date'] = pd.to_datetime(weighted_returns_df['Date'])
        weighted_returns_df.set_index('Date', inplace=True)
        return weighted_returns_df