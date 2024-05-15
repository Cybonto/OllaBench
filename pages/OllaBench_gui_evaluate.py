import os
import time
import pandas as pd
from io import StringIO
import asyncio
import aiofiles
import streamlit as st
from autoviz import AutoViz_Class

from OllaBench_gui_menu import menu_with_redirect, show_header

columns_of_interest = [
    'ID', 'Model', 'WCP_TotalDuration', 'WCP_EvalCounts', 'WCP_score',
    'WHO_TotalDuration', 'WHO_EvalCounts', 'WHO_score',
    'TeamRisk_TotalDuration', 'TeamRisk_EvalCounts', 'TeamRisk_score',
    'TargetFactor_TotalDuration', 'TargetFactor_EvalCounts', 'TargetFactor_score',
    'Total score'
]

# Functions
def list_model_names(directory):
    model_names = set()  # Using a set to avoid duplicate model names
    files = os.listdir(directory)
    # count total files for progress tracking
    st.session_state.total_files = sum(1 for file in files if os.path.isfile(os.path.join(directory, file)))
    for filename in files:
        if filename.endswith("_QA_Results.csv"):
            parts = filename.split('_')
            if len(parts) >= 6:  # Check if filename splits correctly
                model_name = parts[0]
                model_names.add(model_name)
    results = list(model_names)
    results.sort()
    return results

async def read_csv_async(file_path):
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
        content = await file.read()
    df = pd.read_csv(StringIO(content))  # Use StringIO from the io module
    return df[columns_of_interest]

async def process_model_files(directory, model_name):
    tasks = []
    for filename in os.listdir(directory):
        if filename.startswith(model_name) and filename.endswith("_QA_Results.csv"):
            file_path = os.path.join(directory, filename)
            tasks.append(read_csv_async(file_path))
    dataframes = await asyncio.gather(*tasks)
    return pd.concat(dataframes, ignore_index=True)

async def evaluation(directory):
    model_names = list_model_names(directory)
    results = {}
    for model in model_names:
        df = await process_model_files(directory, model)
        wasted_wcp_counts = df.loc[df['WCP_score'] == 0, 'WCP_EvalCounts'].sum()
        wasted_who_counts = df.loc[df['WHO_score'] == 0, 'WHO_EvalCounts'].sum()
        wasted_team_risk_counts = df.loc[df['TeamRisk_score'] == 0, 'TeamRisk_EvalCounts'].sum()
        wasted_target_factor_counts = df.loc[df['TargetFactor_score'] == 0, 'TargetFactor_EvalCounts'].sum()

        n = len(df)  # Length of the DataFrame for each model

        results[model] = {
            'Avg WCP Duration': df['WCP_TotalDuration'].mean(),
            'Avg WCP Counts': df['WCP_EvalCounts'].mean(),
            'Avg WCP score': df['WCP_score'].mean(),
            'Avg WHO Duration': df['WHO_TotalDuration'].mean(),
            'Avg WHO Counts': df['WHO_EvalCounts'].mean(),
            'Avg WHO score': df['WHO_score'].mean(),
            'Avg Team Risk Duration': df['TeamRisk_TotalDuration'].mean(),
            'Avg Team Risk Counts': df['TeamRisk_EvalCounts'].mean(),
            'Avg Team Risk score': df['TeamRisk_score'].mean(),
            'Avg Target Factor Duration': df['TargetFactor_TotalDuration'].mean(),
            'Avg Target Factor Counts': df['TargetFactor_EvalCounts'].mean(),
            'Avg Target Factor score': df['TargetFactor_score'].mean(),
            'Avg Score': df['Total score'].mean()/4,
            'Wasted WCP Counts': wasted_wcp_counts,
            'Wasted WHO Counts': wasted_who_counts,
            'Wasted Team Risk Counts': wasted_team_risk_counts,
            'Wasted Target Factor Counts': wasted_target_factor_counts,
            'Wasted Average': (wasted_wcp_counts + wasted_who_counts +
                               wasted_team_risk_counts + wasted_target_factor_counts) / (n * 4) if n > 0 else 0
        }

    return results

def plot_model_comparison(df, column_names, type="line"):
    """
    Plots a comparison of all models based on a specified column.

    Args:
    df (DataFrame): A DataFrame containing model data with models as columns.
    column_name (str): The name of the column to compare.

    Raises:
    ValueError: If the column_name is not in the DataFrame.
    """
    # Check for column existence
    missing_columns = [col for col in column_names if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Columns '{', '.join(missing_columns)}' not found in DataFrame.")

    # Extract the relevant data
    model_data = df[column_names]
    st.write(f'Comparison of {column_names} Across Models')
    if type=="line":
        st.line_chart(model_data)
    if type=="bar":
        st.bar_chart(model_data)

def create_random_dir (base_path="./"):
    dir_name = str(uuid.uuid4())
    dir_path = os.path.join(base_path, dir_name)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def plot_dataviz (df, target="None"):
    target_col=""
    if target=="None":
        target_col = df.columns[-1]
    elif target in df.columns:
        target_col = target
    else:
        st.write("Incorrect column name was give for ploting dataviz")
        return None

    plot_path = create_random_dir(base_path="plots/")
    AV = AutoViz_Class()
    AV.AutoViz(
        filename='',
        dfte=df,
        depVar=target_col,
        verbose=2, #save to disk plots
        chart_format='jpg',
        save_plot_dir=plot_path
    )
    image_path = os.path.join(plot_path,target_col)
    plot_files = os.listdir(image_path)
    for file in plot_files:
        st.image(os.path.join(image_path,file))

    return None

# Main Streamlit app starts here
show_header()
menu_with_redirect()

# Verify the user's role
if st.session_state.role not in ["admin", "user"]:
    st.warning("You do not have permission to view this page.")
    st.stop()

col1, col2, col3 = st.columns([0.1,0.8,0.1])
with col1:
    st.write(" ")
with col3:
    st.write(" ")
with col2:
    st.title("Evaluate Models' Responses")
if not st.session_state.healthcheck_passed:
    st.warning("System health checking is not passed or not performed. Please run health check.")
    st.stop()
    
#st.markdown(f"You are currently logged with the role of {st.session_state.role}.")
waiting_wheel = st.empty()
with waiting_wheel.container():
    st.spinner('Please wait...')

response_path = "Responses/"
models = list_model_names(response_path)
st.session_state.total_models = len(models)
results = asyncio.run(evaluation(response_path))
result_df = pd.DataFrame(results)
result_dfT = result_df.T

st.subheader("Performance Metrics")
st.write(result_dfT)

st.subheader("Consistency Metrics")
#tba

st.subheader("Comparision Charts")
plot_model_comparison(result_dfT, ['Avg WCP score','Avg WHO score','Avg Team Risk score','Avg Target Factor score'])
#plot_model_comparison(result_dfT, 'Avg WHO score')
#plot_model_comparison(result_dfT, 'Avg Team Risk score')
#plot_model_comparison(result_dfT, 'Avg Target Factor score')
plot_model_comparison(result_dfT, ['Avg Score'], type="bar")
plot_model_comparison(result_dfT, ['Wasted Average'], type="bar")

st.subheader("Data Analysis")
#tba

if len(result_dfT)>0:
    waiting_wheel.empty()