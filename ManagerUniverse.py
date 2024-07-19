"""
This file performs the following tasks:

1. Initialize an empty ManagerUniverse, the core simulation for our algorithm.

2. Parse timeseries data and other information provided in the given data folder
to create Program objects (which populate the Universe and can be accessed through the Universe).

3. Perform various statistical operations on all Programs in the Universe, updating their attributes.

4. Create Clusters, which are groupings of Programs based on the results of the above statistical operations.
These Clusters are accessed through the Universe.

5: Results displayed in UI_EMP.py
"""
import os
from Entities import Program, Cluster
from DataParser import MonthlyRor
from StatsCalculations import calc_omega_score, calc_sharpe_ratio, calc_pearson_correlation, \
    calc_max_drawdown, calc_max_drawdown_length, calc_max_drawdown_duration
from sklearn import preprocessing
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import percentileofscore
import pandas as pd

class ManagerUniverse:
    """ Maintains all entities."""
    _programs: list
    _clusters: list
    # Prev: add cluster definite corr
    correlation_value: float

    def __init__(self, correlation_value=0.5) -> None:
        """Initialize a new Emerging Managers universe.
        The universe starts with no entities.
        """
        self._programs = []
        self._clusters = []
        self.corr = correlation_value

    def populate_programs(self, path: str, start_date=None, end_date=None, test_start_date=None, test_end_date=None) -> None:
        """
        Create Program objects from all CSVs in provided folder. Add them to Universe.

        Parameters:
            path: Filepath to data folder.
            start_date: Start date for filtering (inclusive), a string in 'YYYY-MM-DD' format.
            end_date: End date for filtering (inclusive), a string in 'YYYY-MM-DD' format.
            test_start_date: Flagged.
            test_end_date: 
        """
        for i, filename in enumerate(os.listdir(path)):
            if filename == '.DS_Store':
                continue
            # print(i, filename)

            monthly_ror_dao = MonthlyRor(path + '/' + filename)  # complete filepath to CSV from source
            monthly_ror_timeseries = monthly_ror_dao.get_timeseries(start_date=start_date, end_date=end_date)
            test_monthly_ror_timeseries = monthly_ror_dao.get_timeseries(start_date=test_start_date, end_date=test_end_date)

            # Flagged. Need to do something here to ensure both timeseries were properly initialized
            # before creating & adding the Program.
            manager_name: str = monthly_ror_dao.manager_name
            fund_name: str = monthly_ror_dao.fund_name

            # Generate a new Program object for each CSV and append this new program into the universe program list.

            new_program = Program(manager_name, fund_name, monthly_ror_timeseries, test_monthly_ror_timeseries)
            self._programs.append(new_program)


    def perform_program_stats_calculations(self):
        """
        Performs all stats calculations on each program in the universe.
        """
        for program in self._programs:
            rors = program.timeseries.rors
            program.omega_score = calc_omega_score(rors)
            if program.omega_score is None:
                print(f"Could not calculate Omega score for {program.name}")
            program.sharpe_ratio = calc_sharpe_ratio(rors)
            if program.omega_score is None:
                print(f"Could not calculate Sharpe ratio for {program.name}")
            if len(rors) < 2:
                print(f"Could not perform drawdown analysis for {program.name}")
            else:
                program.max_drawdown = calc_max_drawdown(rors)
                program.max_drawdown_length = calc_max_drawdown_length(rors)
                program.max_drawdown_duration = calc_max_drawdown_duration(rors)
        # Flagged. Need to establish algorithm's behaviour when a score can't be calculated.


    def populate_clusters(self):
        """
        For each program, create a set that contains all programs with corr > 0.65.
        Then, create a cluster object that contains the head program and the set we just created. 
        Add this cluster into the cluster list.

        Prev: create eq and hash function for Program class?
        """
        for head in self._programs:
            cluster = set()
            cluster.add(head)
            for others in self._programs:
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
        omega_rating = []
        sharpe_rating = []
        drawdown_rating = []
        score_score = []
        ratings_df = pd.DataFrame()
        
        # Calculate the performance of the each program relative to the others in its cluster
        for each_cluster in self._clusters:
            percentile_list = []
            
            omega_data = [program.omega_score for program in each_cluster.programs]
            head_omega_percentile = percentileofscore(omega_data, each_cluster.head.omega_score)
            percentile_list.append(head_omega_percentile)
            # Flagged. This seems to be assigning a better score to higher max drawdown?
            max_dd_data = [program.max_drawdown for program in each_cluster.programs]
            head_max_dd_percentile = percentileofscore(max_dd_data, each_cluster.head.max_drawdown)
            percentile_list.append(head_max_dd_percentile)

            sharpe_data = [program.sharpe_ratio for program in each_cluster.programs]
            head_sharpe_percentile = percentileofscore(sharpe_data, each_cluster.head.sharpe_ratio)
            percentile_list.append(head_sharpe_percentile)

            # Calculate the program's overall, unnormalized performance score and store it in a list
            each_cluster.head.overall_score = np.mean(percentile_list)/100
            program_score.append(each_cluster.head.overall_score)
            
            # Store each program's name and stats in lists
            program_name.append(each_cluster.head.name)
            program_omega_score.append(each_cluster.head.omega_score)
            program_sharpe_ratio.append(each_cluster.head.sharpe_ratio)
            program_maxdrawdown.append(each_cluster.head.max_drawdown)

        # Calculate the performance of each program relative to all other programs (score of 1-5)
        # Flagged. Why not iterate through self._programs instead of clusters?
        for each_cluster in self._clusters:
            omega_rating.append(self.calculate_percentile_rating(each_cluster.head.omega_score, program_omega_score))  # 1 to 5
            sharpe_rating.append(self.calculate_percentile_rating(each_cluster.head.sharpe_ratio, program_sharpe_ratio))  # 1 to 5
            drawdown_rating.append(6 - self.calculate_percentile_rating(each_cluster.head.max_drawdown, program_maxdrawdown))  # 5 to 1
            score_score.append(self.calculate_percentile_rating(each_cluster.head.overall_score, program_score))

        # Create dataframe 
        ratings_df = pd.DataFrame({
            "Name": program_name,
            "Omega Value": program_omega_score,
            "Omega Score": omega_rating,

            "Sharpe Ratio": program_sharpe_ratio,
            "Sharpe Score": sharpe_rating,

            "Drawdown Area": program_maxdrawdown,
            "Drawdown Score": drawdown_rating,
            
            "Score": program_score,
            "Overall Score": score_score
        })

        # Use the program names as the indices of the dataframe
        ratings_df.set_index("Name", inplace=True)

        # Normalize the overall program scores (from 0-100). 
        normalized_weights = program_score # Flagged. Redundant line?
        normalized_weights = normalized_weights / np.sum(normalized_weights)
        i = 0
        while i < len(self._programs):
            self._programs[i].overall_weight = normalized_weights[i]
            i += 1
        ratings_df["Weights"] = normalized_weights
    
        # Calculate the volatility of each fund
        # Flagged. Why not iterate through self._programs instead of clusters?
        program_volatility = []
        for each_cluster in self._clusters:
            program_volatility.append(np.std(each_cluster.head.timeseries.rors))
        
        # Invert the volatilities
        inv_vol_weights = [1 / vol if vol != 0 else 0 for vol in program_volatility]
        
        # Normalize the inverted volatilities
        total_inv_vol = sum(inv_vol_weights)
        normalized_vol_weights = [w / total_inv_vol if total_inv_vol !=0 else 0.0000001 for w in inv_vol_weights]
        
        normalized_vol_weights = normalized_vol_weights / np.sum(normalized_vol_weights)

        # Assign volatility scores to each program
        for i, program in enumerate(self._programs):
            program.vol_weight = normalized_vol_weights[i]
        ratings_df["Vol Weights"] = normalized_vol_weights

        return ratings_df


    def calculate_percentile_rating(self, metric_values, all_values):
        """
        Calculate rating based on percentile within all available values.

        Parameters:
            metric_values (float): Flagged. This should be a scalar value, but is being treated as a collection.
            all_values (list): The list of values to be compared with.

        Returns: 
            int: A score from 1-5 indicating relative performance level.
        """
        percentile = percentileofscore(all_values, np.mean(metric_values))
        if percentile >= 80:
            return 5
        elif percentile >= 60:
            return 4
        elif percentile >= 40:
            return 3
        elif percentile >= 20:
            return 2
        else:
            return 1


    def original_portfolio(self):
        """
        Creates a dataframe of the rate of returns for each program.

        Returns:
            pd.DataFrame: Rate of returns. Columns are programs, rows are months.
        """
        program_df = pd.DataFrame()
        
        for program in self._programs:
            df = pd.DataFrame({
                'Date': program.timeseries.dates,
                f'{program.name}': program.timeseries.rors,
            })
            # Merge this program's returns into the main DataFrame
            if program_df.empty:
                program_df = df
            else:
                program_df = pd.merge(program_df, df, on='Date', how='outer')
        
        program_df['Date'] = pd.to_datetime(program_df['Date'])
        program_df.set_index('Date', inplace=True)
        return program_df
    

    def returns_portfolio(self):
        """
        Flagged. Duplicate code. Just pass timeseries as a param to the previous method.
        Need to determine the usage of test_timeseries.
        Also, comments are wrong and seemingly copied from the next method.
        """
        # Create a DataFrame to hold the weighted returns
        returns_df = pd.DataFrame()

        for program in self._programs:
            # Calculate weighted returns for each program   
            program_df = pd.DataFrame({
                'Date': program.test_timeseries.dates,
                f'{program.name} Returns': program.test_timeseries.rors
            })
            # Merge this program's weighted returns into the main DataFrame
            if returns_df.empty:
                returns_df = program_df
            else:
                returns_df = pd.merge(returns_df, program_df, on='Date', how='outer')
            
        returns_df['Date'] = pd.to_datetime(returns_df['Date'])
        returns_df.set_index('Date', inplace=True)
        return returns_df  
    
    
    ####
    # Weighted Portfolios
    ####

    # FLAGGED. There is duplicate code below that may be mergeable. (Pass weights as parameter.)

    def weighted_returns_portfolio(self):
        """
        Creates a dataframe of performance-weighted rate of returns for each program.

        Returns:
            pd.DataFrame: Weighted rate of returns. Columns are program, rows are months.
        """
        # Create a DataFrame to hold the weighted returns
        weighted_returns_df = pd.DataFrame()

        for program in self._programs:
            # Calculate weighted returns for each program
            weighted_rors = [ror * (program.overall_weight) for ror in program.test_timeseries.rors]
            weighted_program_df = pd.DataFrame({
                'Date': program.test_timeseries.dates,
                f'{program.name} Weighted Returns': weighted_rors
            })
          
            # Merge this program's weighted returns into the main DataFrame
            if weighted_returns_df.empty:
                weighted_returns_df = weighted_program_df
            else:
                weighted_returns_df = pd.merge(weighted_returns_df, weighted_program_df, on='Date', how='outer')
            
        weighted_returns_df['Date'] = pd.to_datetime(weighted_returns_df['Date'])
        weighted_returns_df.set_index('Date', inplace=True)
        return weighted_returns_df    
    
    
    def volatility_weighted_returns_portfolio(self):
        """
        Creates a dataframe of volatility-weighted returns for each program.

        Returns:
            pd.DataFrame: Weighted rate of returns. Columns are program, rows are months.
        """
        # Create a DataFrame to hold the weighted returns
        vol_weighted_returns_df = pd.DataFrame()
        
        for program in self._programs:
            vol_weighted_rors = [ror * (program.vol_weight) for ror in program.test_timeseries.rors]
            weighted_program_df = pd.DataFrame({
                'Date': program.test_timeseries.dates,
                f'{program.name} Weighted Returns': vol_weighted_rors
            })
          
            if vol_weighted_returns_df.empty:
                vol_weighted_returns_df = weighted_program_df
            else:
                vol_weighted_returns_df = pd.merge(vol_weighted_returns_df, weighted_program_df, on='Date', how='outer')
            
        vol_weighted_returns_df['Date'] = pd.to_datetime(vol_weighted_returns_df['Date'])
        vol_weighted_returns_df.set_index('Date', inplace=True)
        return vol_weighted_returns_df    


    def equal_weighted_returns_portfolio(self):
        """
        Creates a dataframe of equal-weighted returns for each program.

        Returns:
            pd.DataFrame: Equal-weighted rate of returns. Columns are program, rows are months.
        """
        # Create a DataFrame to hold the weighted returns
        weighted_returns_df = pd.DataFrame()
        
        # Calculate equal weight
        num_programs = len(self._programs)
        equal_weight = 1 / num_programs
        
        for program in self._programs:
            # Calculate weighted returns using equal weight
            weighted_rors = np.array(program.test_timeseries.rors) * (equal_weight)
            weighted_program_df = pd.DataFrame({
                'Date': program.test_timeseries.dates,
                f'{program.name} Equal Weighted Returns': weighted_rors
            })
            
            if weighted_returns_df.empty:
                weighted_returns_df = weighted_program_df
            else:
                weighted_returns_df = pd.merge(weighted_returns_df, weighted_program_df, on='Date', how='outer')
        
        weighted_returns_df['Date'] = pd.to_datetime(weighted_returns_df['Date'])
        weighted_returns_df.set_index('Date', inplace=True)
        return weighted_returns_df

    
    ####
    # Analysis
    ####
    def calculate_metrics(df, risk_free_rate=0.03):
        """
        Calculates the cumulative returns, total return, annualized return, annualized standard deviation, 
        and Sharpe ratio of a timeseries. 

        Parameters: 
            df (pd.Series): A series of monthly returns.
            risk_free_rate (float): The risk-free rate used to calculate the Sharpe ratio. 

        Returns:
            Tuple (pd.Series, dict)
        """
        # Create series of cumulative returns
        cumulative_returns = (1 + df).cumprod() - 1
        # Get the total return and annual return rate (as a percentage)
        total_return = cumulative_returns.iloc[-1]  
        days = (df.index[-1] - df.index[0]).days
        months = np.round(days / 30.44)  # Average number of days in a month
        annualized_return = ((1 + total_return) ** (12 / months) - 1)
        
        monthly_returns = df.values
        annualized_std = monthly_returns.std() * np.sqrt(12)  # Annualize the standard deviation for monthly returns
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_std
        
        metrics = {
            'Total Return (%)': total_return,
            'Annualized Return (%)': annualized_return,
            'Annualized Std Dev (%)': annualized_std,
            'Sharpe Ratio': sharpe_ratio,
        }
        
        return cumulative_returns, metrics
    
    
    def Portfolio_Performance(df_list):
        """
        For each differently weighted dataframe of returns, create one portfolio and plot it. 

        Parameters: 
            df_list (list(pd.DataFrame)): List of differently weighted returns.
        """
        weight_order = ["EMP Weights", "Vol Weights", "Equal Weights"]
        plt.figure(figsize=(25, 10))
        for i, df in enumerate(df_list):
            monthly_returns_sum = df.sum(axis=1) # Sum across each column to get a single weighted sum for each date
            portfolio_monthly_performance, metric_dic = ManagerUniverse.calculate_metrics(monthly_returns_sum)    
            plt.plot(portfolio_monthly_performance.values.flatten())
            plt.xticks(range(len(portfolio_monthly_performance.index)), portfolio_monthly_performance.index.astype(str), rotation=45)
            plt.title("Cumulative Product")
            print(weight_order[i] + ": " + str(metric_dic))
        plt.legend(weight_order)
        plt.show()

    

if __name__ == '__main__':
    returns_folder = 'Data'

    # The param here can set to be the desired correlation.
    universe = ManagerUniverse(0.3)

    print("Initializing Universe...\n")
    universe.populate_programs(returns_folder)
    print("\nAdded all Programs. Performing calculations...")
    universe.perform_program_stats_calculations()
    print("\nFinished calculations. Correlating...")

    universe.populate_clusters()
    print("\nAll clusters have been created. Calculating Scores and Weights for all programs...")
    universe.ratings_df()
    print("\nThe weighted return portfolio is as followed: ")
    universe.weighted_returns_portfolio()












 