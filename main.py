"""
This file handles the main workflow for running the algorithm.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from StatsCalculations import calc_cumulative_returns, calc_ann_return, calc_sharpe_ratio
from ManagerUniverse import ManagerUniverse
from datetime import datetime

####
# Analysis
####
def export_portfolio(df):
    monthly_returns = df.sum(axis=1)
    # Convert the Series to a DataFrame
    df = monthly_returns.reset_index()
    df.columns = ['Date', 'Change']
    df['Change'] = df['Change'].round(4)
    # Get today's date in YYYY-MM-DD format
    today = datetime.today().strftime('%Y-%m-%d')
    file_name = f'output/Hypothetical Portfolio {today}.csv'
    # Export to CSV
    df.to_csv(file_name, index=False)


def calculate_metrics(df):
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
    cumulative_returns = calc_cumulative_returns(df)
    # Get the total return and annual return rate (as a percentage)
    total_return = cumulative_returns.iloc[-1]
    monthly_returns = df.values
    annualized_return = calc_ann_return(monthly_returns)
    annualized_std = monthly_returns.std() * np.sqrt(12)  # Annualize the standard deviation for monthly returns
    sharpe_ratio = calc_sharpe_ratio(monthly_returns)
    
    metrics = {
        'Total Ret (%)': round(total_return, 3),
        'Ann Ret (%)': round(annualized_return, 3),
        'Ann Std Dev (%)': round(annualized_std, 3),
        'Sharpe Ratio': round(sharpe_ratio, 3)
    }
    return cumulative_returns, metrics


def Portfolio_Performance(df_list):
    """
    Creates one portfolio for each dataframe of weighted timeseries.

    Parameters: 
        df_list (list(pd.DataFrame)): List of differently weighted timeseries.

    Returns:
        matplotlib.figure.Figure: A linechart with one or more lines. Each line represents a hypothetical portfolio
            created using a certain weighing style.
        string: An output string summarizing the stats of each portfolio.
    """
    weight_order = ["EMP Weights", "Vol Weights", "Equal Weights"]
    plt.figure(figsize=(25, 10))
    output_string = ""
    for i, df in enumerate(df_list):
        monthly_returns_sum = df.sum(axis=1) # Sum across each column to get a single hypothetical return for each date
        portfolio_monthly_performance, metric_dic = calculate_metrics(monthly_returns_sum)    
        plt.plot(portfolio_monthly_performance.values.flatten())
        plt.xticks(range(len(portfolio_monthly_performance.index)), portfolio_monthly_performance.index.astype(str), rotation=45)
        plt.title("Cumulative Product")
        output_string += weight_order[i] + ": " + str(metric_dic) + "\n"
    plt.legend(weight_order)
    return plt, output_string


def Static_Performance(corr, start_date, end_date, emerging_programs, other_programs):
    """
    Runs the main algorithm once based on data from start date to end date.

    Parameters: 
        corr (int): The minimum correlation between each program in a cluster.
        start_date (string): The start date for each program's timeseries.
        end_date (string): The end date for each program's timeseries.
        emerging_programs (string): File path to folder containing the emerging programs' csvs.
        other_programs (string): File path to folder containing other programs' csvs.

    Returns:
        list(pd.Dataframe): A list of dataframes. Each dataframe has every program's weighted timeseries.
        pd.Dataframe: A dataFrame of programs, performance measures, and scores.
    """
    # Create universe and run main algorithm
    universe = ManagerUniverse(corr)
    # Populate the universe with all programs
    universe.populate_programs(emerging_programs, is_emerging=True, start_date=start_date, end_date=end_date)
    universe.populate_programs(other_programs, is_emerging=False, start_date=start_date, end_date=end_date)
    # Create clusters and evaluate programs based on the program's timeseries up to a specified date
    universe.perform_program_stats_calculations(full_timeseries=False)
    universe.populate_clusters(full_timeseries=False)
    universe.assign_scores()
    # Create clusters and evaluate programs based on the program's full timeseries
    universe.perform_program_stats_calculations(full_timeseries=True)
    universe.populate_clusters(full_timeseries=True)
    universe.assign_scores()
    # Get dataframes of stats and all weighted timeseries
    scores_df = universe.ratings_df(w=0.8)
    EMP_df = universe.weighted_returns_portfolio(iter=False)
    vol_df = universe.volatility_weighted_returns_portfolio(iter=False)
    equal_df = universe.equal_weighted_returns_portfolio(iter=False)

    df_list = [EMP_df, vol_df, equal_df]

    return df_list, scores_df


def Iterative_Performance(corr, start_date, end_date, emerging_programs, other_programs):
    """
    Iteratively runs the main algorithm, treating each data point as validation data. 
    I.e., for each month's returns, give it a weight based on performance from previous months.  

    Note: this function currently causes errors. This was also what the original code in UI_EMP.py was doing.
    Ranjan has since decided to use the Static_Performance method for now.

    Parameters: 
        corr (int): The minimum correlation between each program in a cluster.
        start_date (string): The start date for each program's timeseries.
        end_date (string): The end date for each program's timeseries.

    Returns:
        list(pd.Dataframe): A list of dataframes. Each dataframe has every program's weighted timeseries.
        pd.Dataframe: A dataFrame of programs, performance measures, and scores.
    """
    start_date_input = pd.to_datetime('2022-01-01')
    end_date_input = pd.to_datetime('2024-04-01')

    # Generate date range based on user input
    date_range = pd.date_range(start=start_date_input, end=end_date_input, freq='MS')

    # Initialize dataframes and variables
    EMP_df = pd.DataFrame()
    vol_df = pd.DataFrame()
    equal_df = pd.DataFrame()
    scores_df = pd.DataFrame()
    start_date = '2003-01-01' 

    for i in range(len(date_range) - 1):
        end_date = date_range[i].strftime('%Y-%m-%d')
        test_date = date_range[i+1].strftime('%Y-%m-%d')

        universe = ManagerUniverse(corr)
        universe.populate_programs(emerging_programs, is_emerging=True, start_date=start_date, end_date=end_date, test_start_date=test_date, test_end_date=test_date)
        universe.populate_programs(other_programs, is_emerging=False, start_date=start_date, end_date=end_date)
        universe.perform_program_stats_calculations()
        universe.populate_clusters()

        scores_df = universe.ratings_df()
        emp_sample = universe.weighted_returns_portfolio(iter=True)
        vol_sample = universe.volatility_weighted_returns_portfolio(iter=True)
        equal_sample = universe.equal_weighted_returns_portfolio(iter=True)

        EMP_df = pd.concat([EMP_df, emp_sample])
        vol_df = pd.concat([vol_df, vol_sample])
        equal_df = pd.concat([equal_df, equal_sample])

    df_list = [EMP_df, vol_df, equal_df]
    return df_list, scores_df


if __name__ == '__main__':
    correlation_parameter = 0.3
    start_date = '2019-01-01'
    end_date = '2024-10-01'
    emerging_programs = 'data/core programs'
    other_programs = 'data/other programs'

    df_list, scores_df = Static_Performance(correlation_parameter, start_date, end_date, emerging_programs, other_programs)
    export_portfolio(df_list[0])
    plt, stats = Portfolio_Performance(df_list)
    plt.show()
    print("")
    print(stats)