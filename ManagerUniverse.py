"""
This file performs the following tasks:

1. Initialize an empty ManagerUniverse, the core simulation for our algorithm.

2. Parse timeseries data and other information provided in the given data folder
to create Manager objects (which populate the Universe and can be accessed through the Universe).

3. Perform various statistical operations on all Managers in the Universe, updating their attributes.

4. Create Clusters, which are groupings of Managers based on the results of the above statistical operations.
These Clusters are accessed through the Universe.

5: Results displayed in UI_EMP.py
"""
import os
from Entities import Manager, Cluster
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
    _managers: list
    _clusters: list
    # Prev: add cluster definite corr
    correlation_value: float

    def __init__(self, correlation_value=0.5) -> None:
        """Initialize a new emerging managers universe.
        The universe starts with no entities.
        """
        self._managers = []
        self._clusters = []
        self.corr = correlation_value

    def populate_managers(self, path: str, start_date=None, end_date=None, test_start_date=None, test_end_date=None) -> None:
        """
        Create Manager objects from all CSVs in provided folder. Add them to Universe.

        path: filepath to data folder
        """
        for i, filename in enumerate(os.listdir(path)):
            if filename == '.DS_Store':
                continue
            # print(i, filename)

            monthly_ror_dao = MonthlyRor(path + '/' + filename)  # complete filepath to CSV from source
            monthly_ror_timeseries = monthly_ror_dao.get_timeseries(start_date=start_date, end_date=end_date)
            test_monthly_ror_timeseries = monthly_ror_dao.get_timeseries(start_date=test_start_date, end_date=test_end_date)

            # Flagged. Need to do something here to ensure both timeseries were properly initialized
            # before creating & adding manager.
            manager_name: str = monthly_ror_dao.manager_name
            fund_name: str = monthly_ror_dao.fund_name

            # Generate a new Manager object for each CSV and append this new manager into the universe manager list.

            # if manager_name not in self._managers: # Flagged. This statement does not serve intended purpose.
            # Flagged. Need to establish behaviour when we have managers with multiple funds. 
            new_manager = Manager(manager_name, fund_name, monthly_ror_timeseries, test_monthly_ror_timeseries)
            self._managers.append(new_manager)

            # print(f"Added {manager_name}")
            

    def perform_manager_stats_calculations(self):
        """
        Performs all stats calculations on each manager in the universe.
        """
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
        # Flagged. Need to establish algorithm's behaviour when a score can't be calculated.


    def populate_clusters(self):
        """
        For each manager, create a set which contains all managers that has corr > 0.65.
        and then create a cluster object that contains the head manager and the set we just created. 
        Then, add this cluster into the cluster list.

        Prev: create eq and hash function for Manager class
        """
        for head_manager in self._managers:
            managers = set()
            managers.add(head_manager)
            for other_manager in self._managers:
                if other_manager.name != head_manager.name and other_manager.fund_name != head_manager.fund_name:
                    # Get correlation between two managers' synced rors
                    corr = calc_pearson_correlation(head_manager.timeseries, other_manager.timeseries)
                    if corr > self.corr:
                        managers.add(other_manager)
                        #print(f'{head_manager.name} - {other_manager.name} corr: {corr}')
                
            new_cluster = Cluster(head_manager, managers)
            self._clusters.append(new_cluster)
            #print(f"Added {head_manager.name} centered cluster")


    def ratings_df(self):
        """
        Assigns scores to each manager based on performance relative to the others.

        Returns:
            DataFrame: Pandas DataFrame of managers, performance measures, and scores
        """
        manager_score = []
        manager_name = []
        manager_omega_score = []
        manager_sharpe_ratio = []
        manager_maxdrawdown = []
        omega_rating = []
        sharpe_rating = []
        drawdown_rating = []
        score_score = []
        ratings_df = pd.DataFrame()
        
        # Calculate the performance of the each manager relative to the others in its cluster
        for each_cluster in self._clusters:
            percentile_list = []
            
            omega_data = [manager.omega_score for manager in each_cluster.managers]
            head_omega_percentile = percentileofscore(omega_data, each_cluster.head.omega_score)
            percentile_list.append(head_omega_percentile)
            # Flagged. This seems to be assigning a better score to higher max drawdown?
            max_dd_data = [manager.max_drawdown for manager in each_cluster.managers]
            head_max_dd_percentile = percentileofscore(max_dd_data, each_cluster.head.max_drawdown)
            percentile_list.append(head_max_dd_percentile)

            sharpe_data = [manager.sharpe_ratio for manager in each_cluster.managers]
            head_sharpe_percentile = percentileofscore(sharpe_data, each_cluster.head.sharpe_ratio)
            percentile_list.append(head_sharpe_percentile)

            # Calculate the manager's overall, unnormalized performance score and store it in a list
            each_cluster.head.overall_score = np.mean(percentile_list)/100
            manager_score.append(each_cluster.head.overall_score)
            
            # Store each manager's name and stats in lists
            manager_name.append(each_cluster.head.name)
            manager_omega_score.append(each_cluster.head.omega_score)
            manager_sharpe_ratio.append(each_cluster.head.sharpe_ratio)
            manager_maxdrawdown.append(each_cluster.head.max_drawdown)

        # Calculate the performance of each manager relative to all other managers (score of 1-5)
        # Flagged. Why not iterate through self._managers instead of clusters?
        for each_cluster in self._clusters:
            omega_rating.append(self.calculate_percentile_rating(each_cluster.head.omega_score, manager_omega_score))  # 1 to 5
            sharpe_rating.append(self.calculate_percentile_rating(each_cluster.head.sharpe_ratio, manager_sharpe_ratio))  # 1 to 5
            drawdown_rating.append(6 - self.calculate_percentile_rating(each_cluster.head.max_drawdown, manager_maxdrawdown))  # 5 to 1
            score_score.append(self.calculate_percentile_rating(each_cluster.head.overall_score, manager_score))

        # Create dataframe 
        ratings_df = pd.DataFrame({
            "Name": manager_name,
            "Omega Value": manager_omega_score,
            "Omega Score": omega_rating,

            "Sharpe Ratio": manager_sharpe_ratio,
            "Sharpe Score": sharpe_rating,

            "Drawdown Area": manager_maxdrawdown,
            "Drawdown Score": drawdown_rating,
            
            "Score": manager_score,
            "Overall Score": score_score
        })

        # Use the manager names as the indices of the dataframe
        ratings_df.set_index("Name", inplace=True)

        # Normalize the overall manager scores (from 0-100)
        normalized_manager_weights = manager_score
        normalized_manager_weights = normalized_manager_weights / np.sum(normalized_manager_weights)
        i = 0
        while i < len(self._managers):
            self._managers[i].overall_weight = normalized_manager_weights[i]
            i += 1
        ratings_df["Weights"] = normalized_manager_weights
    
        # Calculate the volatility of each fund
        # Flagged. Why not iterate through self._managers instead of clusters?
        manager_volatility = []
        for each_cluster in self._clusters:
            manager_volatility.append(np.std(each_cluster.head.timeseries.rors))
        
        # Invert the volatilities
        inv_vol_weights = [1 / vol if vol != 0 else 0 for vol in manager_volatility]
        
        # Normalize the inverted volatilities
        total_inv_vol = sum(inv_vol_weights)
        normalized_vol_weights = [w / total_inv_vol if total_inv_vol !=0 else 0.0000001 for w in inv_vol_weights]
        
        normalized_vol_weights = normalized_vol_weights / np.sum(normalized_vol_weights)

        # Assign volatility scores to each manager
        for i, manager in enumerate(self._managers):
            manager.vol_weight = normalized_vol_weights[i]
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
        Creates a dataframe of the rate of returns for each manager/fund.

        Returns:
            DataFrame: Rate of returns. Columns are managers/funds, rows are months.
        """
        manager_df = pd.DataFrame()
        
        for manager in self._managers:
            # Flagged. Multiple Manager objects currently have the same name. Use fund name instead?
            df = pd.DataFrame({
                'Date': manager.timeseries.dates,
                f'{manager.name}': manager.timeseries.rors,
            })
            # Merge this manager's returns into the main DataFrame
            if manager_df.empty:
                manager_df = df
            else:
                manager_df = pd.merge(manager_df, df, on='Date', how='outer')
        
        manager_df['Date'] = pd.to_datetime(manager_df['Date'])
        manager_df.set_index('Date', inplace=True)
        return manager_df
    

    def returns_portfolio(self):
        """
        Flagged. Duplicate code. Just pass timeseries as a param to the previous method.
        Need to determine the usage of test_timeseries.
        Also, comments are wrong and seemingly copied from the next method.
        """
        # Create a DataFrame to hold the weighted returns
        returns_df = pd.DataFrame()

        for manager in self._managers:
            # Calculate weighted returns for each manager   
            manager_df = pd.DataFrame({
                'Date': manager.test_timeseries.dates,
                f'{manager.name} Returns': manager.test_timeseries.rors
            })
            # Merge this manager's weighted returns into the main DataFrame
            if returns_df.empty:
                returns_df = manager_df
            else:
                returns_df = pd.merge(returns_df, manager_df, on='Date', how='outer')
            
        returns_df['Date'] = pd.to_datetime(returns_df['Date'])
        returns_df.set_index('Date', inplace=True)
        return returns_df  
    
    
    ####
    # Weighted Portfolios
    ####

    # FLAGGED. There is duplicate code below that may be mergeable.

    def weighted_returns_portfolio(self):
        """
        Creates a dataframe of the weighted rate of returns for each manager/fund.

        Returns:
            DataFrame: Weighted rate of returns. Columns are managers/funds, rows are months.
        """
        # Create a DataFrame to hold the weighted returns
        weighted_returns_df = pd.DataFrame()

        for manager in self._managers:
            # Calculate weighted returns for each manager
            weighted_rors = [ror * (manager.overall_weight) for ror in manager.test_timeseries.rors]
            # Flagged. Multiple Manager objects with same name.
            weighted_manager_df = pd.DataFrame({
                'Date': manager.test_timeseries.dates,
                f'{manager.name} Weighted Returns': weighted_rors
            })
          
            # Merge this manager's weighted returns into the main DataFrame
            if weighted_returns_df.empty:
                weighted_returns_df = weighted_manager_df
            else:
                weighted_returns_df = pd.merge(weighted_returns_df, weighted_manager_df, on='Date', how='outer')
            
        weighted_returns_df['Date'] = pd.to_datetime(weighted_returns_df['Date'])
        weighted_returns_df.set_index('Date', inplace=True)
        return weighted_returns_df    
    
    
    def volatility_weighted_returns_portfolio(self):
        """
        Creates a dataframe of the weighted volatilities for each manager/fund.

        Returns:
            DataFrame: Weighted rate of returns. Columns are managers/funds, rows are months.
        """
        # Create a DataFrame to hold the weighted returns
        vol_weighted_returns_df = pd.DataFrame()
        
        for manager in self._managers:
            # Calculate weighted returns for each manager
            vol_weighted_rors = [ror * (manager.vol_weight) for ror in manager.test_timeseries.rors]
            # Flagged. Multiple Manager objects with same name.
            weighted_manager_df = pd.DataFrame({
                'Date': manager.test_timeseries.dates,
                f'{manager.name} Weighted Returns': vol_weighted_rors
            })
          
            # Merge this manager's weighted returns into the main DataFrame
            if vol_weighted_returns_df.empty:
                vol_weighted_returns_df = weighted_manager_df
            else:
                vol_weighted_returns_df = pd.merge(vol_weighted_returns_df, weighted_manager_df, on='Date', how='outer')
            
        vol_weighted_returns_df['Date'] = pd.to_datetime(vol_weighted_returns_df['Date'])
        vol_weighted_returns_df.set_index('Date', inplace=True)
        return vol_weighted_returns_df    


    def equal_weighted_returns_portfolio(self):
        # Create a DataFrame to hold the weighted returns
        weighted_returns_df = pd.DataFrame()
        
        # Calculate equal weight
        num_managers = len(self._managers)
        equal_weight = 1 / num_managers
        
        for manager in self._managers:
            # Calculate weighted returns using equal weight
            weighted_rors = np.array(manager.test_timeseries.rors) * (equal_weight)
            # Flagged. Multiple Manager objects with same name.
            weighted_manager_df = pd.DataFrame({
                'Date': manager.test_timeseries.dates,
                f'{manager.name} Equal Weighted Returns': weighted_rors
            })
            
            # Merge this manager's weighted returns into the main DataFrame
            if weighted_returns_df.empty:
                weighted_returns_df = weighted_manager_df
            else:
                weighted_returns_df = pd.merge(weighted_returns_df, weighted_manager_df, on='Date', how='outer')
        
        weighted_returns_df['Date'] = pd.to_datetime(weighted_returns_df['Date'])
        weighted_returns_df.set_index('Date', inplace=True)
        return weighted_returns_df

    
    ####
    # Analysis
    ####
    def calculate_metrics(df, risk_free_rate=0.03):
        # Assuming the input is period returns, first convert to cumulative returns
        cumulative_returns = (1 + df).cumprod() - 1
        
        total_return = cumulative_returns.iloc[-1]   # Convert to percentage
        days = (df.index[-1] - df.index[0]).days
        months = np.round(days / 30.44)  # Average number of days in a month
        annualized_return = ((1 + total_return) ** (12 / months) - 1)
        
        monthly_returns = df.values
        annualized_std = monthly_returns.std() * np.sqrt(12)  # Annualize the standard deviation for monthly returns
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_std
        
        dic = {
            'Total Return (%)': total_return,
            'Annualized Return (%)': annualized_return,
            'Annualized Std Dev (%)': annualized_std,
            'Sharpe Ratio': sharpe_ratio,
        }
        
        return cumulative_returns, dic
    
    
    def Portfolio_Performance(df_list):
        weight_order = ["EMP Weights", "Vol Weights", "Equal Weights"]
        plt.figure(figsize=(25, 10))
        for i, df in enumerate(df_list):
            monthly_returns_manager_sum = df.sum(axis=1)
            portfolio_monthly_performance, metric_dic = ManagerUniverse.calculate_metrics(monthly_returns_manager_sum)    
            plt.plot(portfolio_monthly_performance.values.flatten())
            plt.xticks(range(len(portfolio_monthly_performance.index)), portfolio_monthly_performance.index.astype(str), rotation=45)
            plt.title("Cumulative Product")
            print(weight_order[i] + ": " + str(metric_dic))
        plt.legend(weight_order)
        plt.show()

    

if __name__ == '__main__':
    returns_folder = 'Data'

    # the para here can set to be the desired correlation.
    universe = ManagerUniverse(0.3)

    print("Initializing Universe...\n")
    universe.populate_managers(returns_folder)
    print("\nAdded all Managers. Performing calculations...")
    universe.perform_manager_stats_calculations()
    print("\nFinished calculations. Correlating...")

    universe.populate_clusters()
    print("\nAll clusters have been created. Calculating Scores and Weights for all managers...")
    universe.ratings_df()
    print("\nThe weighted return portfolio is as followed: ")
    universe.weighted_returns_portfolio()












 