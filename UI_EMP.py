"""
Displays the results of the main algorithm using Streamlit.

How to run:
1. Open terminal
2. Activate virtural environment (venv)
3. cd folder path (C:...\GitHub\emerging_managers_project)
4. run code: streamlit run UI_EMP.py
"""

import streamlit as st
import pandas as pd
import pandas as pd
import matplotlib.pyplot as plt

from main import Static_Performance, Portfolio_Performance
# from tqdm import tqdm 
# import seaborn as sns

# Streamlit interface
st.title('Portfolio Analysis Tool')

# User inputs for correlation and date range
correlation_parameter = st.sidebar.slider('Correlation Parameter', min_value=0.0, max_value=1.0, value=0.3, step=0.05)
start_date_input = st.sidebar.date_input('Start Date', value=pd.to_datetime('2022-01-01'))
end_date_input = st.sidebar.date_input('End Date', value=pd.to_datetime('2024-04-01'))

# Initialize arguments for the main algorithm
start_date = start_date_input.strftime('%Y-%m-%d')
end_date = end_date_input.strftime('%Y-%m-%d')
core_folder = 'Data'
other_folder = 'Old data'

# Get the weighted timeseries for each program from the main algorithm
df_list, scores_df = Static_Performance(correlation_parameter, start_date, end_date, core_folder, other_folder)
EMP_df, vol_df, equal_df = df_list

# Create a single hypothetical portfolio for each weighing method
plt, stats = Portfolio_Performance(df_list)

# Display the results
st.text(stats)
st.pyplot(plt)

st.subheader('EMP Portfolio Performance DataFrame')
st.dataframe(EMP_df)

st.subheader('Vol Weighted Portfolio Performance DataFrame')
st.dataframe(vol_df)

st.subheader('Equal Weighted Portfolio Performance DataFrame')
st.dataframe(equal_df)

st.subheader('Scores and Weights DataFrame')
st.dataframe(scores_df)