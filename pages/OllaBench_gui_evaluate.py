import os
import time
import pandas as pd
import hashlib
from io import StringIO
import asyncio
import aiofiles
import streamlit as st
import graphviz
from autoviz import AutoViz_Class
import semopy as sem

from OllaBench_gui_menu import menu_with_redirect, show_header

st.set_page_config(
    page_title="Evaluate Models",
    initial_sidebar_state="expanded"
)

show_header()
menu_with_redirect()
if not st.session_state.healthcheck_passed:
    st.warning("System health checking is not passed or not performed. Please run health check.")
    st.stop()
    
columns_of_interest = [
    'ID', 'Model', 'WCP_TotalDuration', 'WCP_EvalCounts', 'WCP_score',
    'WHO_TotalDuration', 'WHO_EvalCounts', 'WHO_score',
    'TeamRisk_TotalDuration', 'TeamRisk_EvalCounts', 'TeamRisk_score',
    'TargetFactor_TotalDuration', 'TargetFactor_EvalCounts', 'TargetFactor_score',
    'Total score'
]

# Functions

def list_model_names(directory: str) -> list:
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


async def read_csv_async(file_path: str) -> pd.DataFrame:
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
        content = await file.read()
    df = pd.read_csv(StringIO(content))  # Use StringIO from the io module
    return df[columns_of_interest]

async def process_model_files(directory: str, model_name: str) -> pd.DataFrame:
    tasks = []
    for filename in os.listdir(directory):
        if filename.startswith(model_name) and filename.endswith("_QA_Results.csv"):
            file_path = os.path.join(directory, filename)
            tasks.append(read_csv_async(file_path))
    dataframes = await asyncio.gather(*tasks)
    return pd.concat(dataframes, ignore_index=True)

async def evaluation(directory: str) -> dict:
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

async def semcalc(directory: str) -> dict:
    # Structural equation modeling calculation

    m1 = """
        # measurement model
        WCP =~ WCP_score
        WHO =~ WHO_score
        TR =~ TeamRisk_score
        TF =~ TargetFactor_score
        # regressions
        TR ~ WCP + WHO
        TF ~ WCP
    """
    semM1 = sem.Model(m1)

    model_names = list_model_names(directory)
    results = pd.DataFrame()
    for model in model_names:
        df = await process_model_files(directory, model)
        data = df[['WCP_score','WHO_score','TeamRisk_score','TargetFactor_score']]
        sem_result = semM1.fit(data, obj="MLW")
        inspect_result = semM1.inspect()
        df_inspect = pd.DataFrame(inspect_result).head(3)
        df_inspect.insert(0,"model",model)

        results = pd.concat([results, df_inspect], ignore_index=True)

    return results

def plot_model_comparison(df, column_names, type="line") -> None:
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
    st.markdown(f'**Comparison of {column_names} Across Models**')
    if type=="line":
        st.line_chart(model_data)
    if type=="bar":
        st.bar_chart(model_data)
    return None

def create_random_dir (base_path="./") -> str:
    dir_name = str(uuid.uuid4())
    dir_path = os.path.join(base_path, dir_name)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def create_hashed_df_dir (a_df, base_path) -> str:
    return dir_path

def plot_dataviz (df, target="None") -> None:
    target_col=""
    if target=="None":
        target_col = df.columns[-1]
    elif target in df.columns:
        target_col = target
    else:
        st.write("Incorrect column name was give for ploting dataviz")
        return None

    # hash df and check if dir exists

    plot_path = create_hashed_df_dir(base_path="plots/")

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
    
#st.markdown(f"You are currently logged with the role of {st.session_state.role}.")
waiting_wheel = st.empty()
with waiting_wheel.container():
    st.spinner('Please wait...')

if st.session_state.ollama_endpoints == "demo":
    response_path = "Responses/" #demo mode reads the responses that I collected
else:
    response_path = "pages/responses/" # read the responses that user collected
models = list_model_names(response_path)
st.session_state.total_models = len(models)
results = asyncio.run(evaluation(response_path))
result_df = pd.DataFrame(results)
result_dfT = result_df.T
sem_results = asyncio.run(semcalc(response_path))

st.subheader("Comparision Charts")
plot_model_comparison(result_dfT, ['Avg WCP score','Avg WHO score','Avg Team Risk score','Avg Target Factor score'])
with st.expander("Metric Explaination:"):
    st.markdown('''
                **A Scenario** was generated based on a peer-reviewed knowledge network of cognitive behavioral constructs for cybersecurity (the nodes) and the relationships among them (the edges). Examples of cognitive behavioral constructs include Belief, Norm, Goal, etc. There are 10,000 scenarios in the default benchmark dataset. A scenario consists of two employees (A and B). Each employee has a short description of their cognitive behavioral profile containing natural language description of conitive behavioral construct paths (a collection of nodes and edges).

                **Which Cognitive Path** question presents four options of conitive behavioral construct paths and asks the model to select the (only) correct option that fits the cognitive behavioral profile of either employees. The Avg WCP score is the average score across a model's answers each of which receives 1 if correct and 0 otherwise.

                **Who is Who** question asks the model to decide who is MORE/LESS compliant with information security policies based on the stated cognitive behavioral profiles. The Avg WHO score is the average score across a model's answers each of which receives 1 if correct and 0 otherwise.

                **Team Risk Analysis** question asks the model to assess whether the risk of information security noncompliant will increase if the two employees work closely together in the same team. The Avg Team Risk score is the average score across a model's answers each of which receives 1 if correct and 0 otherwise.

                **Target Factor Analysis** question asks the model to identify the best cognitive behavioral construct to be targeted for strengthening so that the overall information cybersecurity compliance posture of the two employees can increase. The Avg Target Factor score is the average score across a model's answers each of which receives 1 if correct and 0 otherwise.
    ''')

plot_model_comparison(result_dfT, ['Avg Score'], type="bar")
with st.expander("Explaination of the Average score:"):
    st.write('''
        **The Average score** is the average of each model's 'Avg WCP score','Avg WHO score','Avg Team Risk score','Avg Target Factor score'. The model with the highest Average score could be the best performing model. However, it may not be the case with the most efficient model which is a combination of many factors including performance metrics and wasted response metric. 
    ''')

plot_model_comparison(result_dfT, ['Wasted Average'], type="bar")
with st.expander("Explaination of the Wasted Average score:"):
    st.write('''
        **Wasted Response** for each response is measured by the response's tokens and the response evaluation of being incorrect. The Wasted Average score is calculated by the total wasted tokens divided by the number of wrong responses. Further resource costs in terms of time and/or money can be derived from the total wasted response value. The model with the lowest Wasted Average score can be the most efficient model (to be decided in joint consideration with other metrics).
    ''')

st.subheader("Detailed Performance Metrics")
st.write(result_dfT)

columns_to_filter = ['model','Estimate','Std. Err','z-value','p-value']
columns_to_plot = ['Estimate','Std. Err','p-value']

st.subheader("Consistency between Team-Risk and Which-Cog-Path")
temp = sem_results[sem_results.apply(lambda row: (row['lval'], row['rval']) in [('TR','WCP')], axis=1)]
TR_WCP = temp[columns_to_filter]
TR_WCP.set_index(TR_WCP.columns[0], inplace=True)
#TR_WCP_plot = TR_WCP[columns_to_plot]
#st.line_chart(TR_WCP_plot)
st.write(TR_WCP)

st.subheader("Consistency between Team-Risk and Who-is-Who")
temp = sem_results[sem_results.apply(lambda row: (row['lval'], row['rval']) in [('TR','WHO')], axis=1)]
TR_WHO = temp[columns_to_filter]
TR_WHO.set_index(TR_WHO.columns[0], inplace=True)
st.write(TR_WHO)

st.subheader("Consistency between Target-Factor and Which-Cog-Path")
temp = sem_results[sem_results.apply(lambda row: (row['lval'], row['rval']) in [('TF','WCP')], axis=1)]
TF_WCP = temp[columns_to_filter]
TF_WCP.set_index(TF_WCP.columns[0], inplace=True)
st.write(TF_WCP)

#st.subheader("Data Analysis")
#tba

if len(result_dfT)>0:
    waiting_wheel.empty()