import streamlit as st
import pandas as pd
from tqdm import tqdm 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import normalize
import os

from ManagerUniverse import ManagerUniverse
import DataParser
import Entities

"""
How to run:
1. Open terminal
2. Activate virtural environment (venv)
3. cd folder path (C:...\GitHub\emerging_managers_project)
4. run code: streamlit run UI_EMP.py:
"""

def Portfolio_Performance(df_list):
    weight_order = ["EMP Weights", "Vol Weights", "Equal Weights"]
    plt.figure(figsize=(25, 10))
    for i, df in enumerate(df_list):
        monthly_returns_manager_sum = df.sum(axis=1)
        portfolio_monthly_performance, metric_dic = ManagerUniverse.calculate_metrics(monthly_returns_manager_sum)    
        plt.plot(portfolio_monthly_performance.values.flatten())
        plt.xticks(range(len(portfolio_monthly_performance.index)), portfolio_monthly_performance.index.astype(str), rotation=45)
        plt.title("Cumulative Sum")
        st.write(weight_order[i] + ": " + str(metric_dic))
    plt.legend(weight_order)
    
    st.pyplot(plt)


# Streamlit interface
st.title('Portfolio Analysis Tool')

# User inputs for date range
correlation_parameter = st.sidebar.slider('Correlation Parameter', min_value=0.0, max_value=1.0, value=0.3, step=0.05)

start_date_input = st.sidebar.date_input('Start Date', value=pd.to_datetime('2022-01-01'))
end_date_input = st.sidebar.date_input('End Date', value=pd.to_datetime('2023-06-01'))

# Generate date range based on user input
date_range = pd.date_range(start=start_date_input, end=end_date_input, freq='MS')

# Initialize dataframes
EMP_df = pd.DataFrame()
vol_df = pd.DataFrame()
equal_df = pd.DataFrame()
scores_and_weight_df = pd.DataFrame()

# Process periods
for i in range(len(date_range) - 1):
    returns_folder = 'sub_manager_returns'
    start_date = "2003-01-01"
    end_date = date_range[i].strftime('%Y-%m-%d')
    
    test_start_date = date_range[i + 1].strftime('%Y-%m-%d')
    test_end_date = test_start_date
    
    # Display processing period
    # st.write(f"Processing period: Start date = {start_date}, End date = {end_date}, Test start date = {test_start_date}, Test end date = {test_end_date}")
    
    universe = ManagerUniverse(correlation_parameter)
    universe.populate_managers(returns_folder, start_date=start_date, end_date=end_date, test_start_date=test_start_date, test_end_date=test_end_date)
    universe.perform_manager_stats_calculations()
    universe.populate_clusters()
    
    ratings_df = universe.ratings_df()
    df_rp_weight = universe.weighted_returns_portfolio()
    df_vol_weight = universe.volatility_weighted_returns_portfolio()
    df_eq_weight = universe.equal_weighted_returns_portfolio()
        
    EMP_df = pd.concat([EMP_df, df_rp_weight])
    vol_df = pd.concat([vol_df, df_vol_weight])
    equal_df = pd.concat([equal_df, df_eq_weight])
    
    scores_and_weight_df = pd.concat([scores_and_weight_df, ratings_df])

# Display 
df_list = [EMP_df, vol_df, equal_df]

Portfolio_Performance(df_list)

st.subheader('EMP Portfolio Performance DataFrame')
st.dataframe(EMP_df)

st.subheader('Vol Weighted Portfolio Performance DataFrame')
st.dataframe(vol_df)

st.subheader('Equal Weighted Portfolio Performance DataFrame')
st.dataframe(equal_df)

st.subheader('Scores and Weights DataFrame')
st.dataframe(scores_and_weight_df)




