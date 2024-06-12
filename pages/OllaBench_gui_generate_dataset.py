import os
import sys
import subprocess
import time
import datetime
import re
import streamlit as st
import csv
import pandas as pd
import shutil
import networkx as nx
import ollama
from ollama import Client
import openai
from openai import OpenAI
import anthropic
from anthropic import Anthropic
import google.generativeai as google
from OllaBench_gui_menu import menu_with_redirect, show_header

st.set_page_config(
    page_title="Generate Dataset",
    initial_sidebar_state="expanded"
)

st.session_state.ollama_endpoints = st.session_state.get('ollama_endpoints')
show_header()
menu_with_redirect()
if not st.session_state.healthcheck_passed:
    st.warning("System health checking is not passed or not performed. Please run health check.")
    st.stop()

if st.session_state.evaluator_framework == "ollama":
    client = Client(host=st.session_state.ollama_endpoints)
elif st.session_state.evaluator_framework == "openai":
    client = OpenAI(api_key=st.session_state.openai_token)
elif st.session_state.evaluator_framework == "anthropic":
    client = anthropic.Anthropic(api_key=st.session_state.anthropic_token)
elif st.session_state.evaluator_framework == "google":
    google.configure(api_key=st.session_state.google_token) # note that we didn't initialize the google client here

if "QA_core_outpath" not in st.session_state:
    st.session_state.QA_core_outpath = "OllaGen1-QA-core.csv"
if "selected_llm" not in st.session_state:    
    st.session_state.selected_llm = "None"
if "QA_full_outpath" not in st.session_state:
    st.session_state.QA_full_outpath = "OllaGen1-QA-full.csv"
if "evaluator_llm_list" not in st.session_state:
    st.session_state.evaluator_llm_list = []

node_path= "pages/Cybonto-Gen1- Nodes.csv"
edge_path= "pages/Cybonto-Gen1- Edges.csv"
llm_framework= "ollama"
construct_list = [
    'Affect',
    'Attitude',
    'Belief',
    'Benefits',
    'Commitment',
    'Control',
    'Costs',
    'Goal',
    'Group norms',
    'Intent',
    'Knowledge',
    'Moral',
    'Motivation',
    'Norms',
    'Response Efficacy',
    'Self-efficacy',
    'Social',
    'Subjective norms',
    'Threat severity',
    'Vulnerability'
]

flag_list = ["com, noncom"]

output_folder = "./templates"
os.makedirs(output_folder, exist_ok=True)

# Import prompt seeds
promptseed_df = pd.read_csv('pages/Cybonto-Gen1-PromptSeeds.csv')

def graph_load (nodes, edges):
    """
    Load a graph from a csv list of nodes and edges. Requires networkx.
    
    Parameters:
    nodes : csv file of nodes with header of "Nodes"
    
    Returns:
    the_graph : a networkx graph object
    """
    the_graph = nx.Graph()
    try:
        # sanitize and check paths
            # to be developed
        
        # load nodes
        node_list = pd.read_csv(nodes)
        # load edges
        edge_list = pd.read_csv(edges)

        # Create graph
        for i, row in edge_list.iterrows(): # Add edges and edge attributes
            the_graph.add_edge(row[0], row[1], attr_dict=row.iloc[2:].to_dict())
    except Exception as e:
        print("Error happens: "+e)
        # log errors as needed
    return the_graph

def get_ollama_response(a_model,a_prompt):
    result = ollama.generate(model=a_model, prompt= f"You are a helpful assistant who follows instruction. {a_prompt}", stream=False)
    while "eval_duration" not in result:
        time.sleep(1)
    return result

def get_openai_response(a_prompt, multiplier):
    responses = []
    model = "gpt-4o"
    if os.environ.get("OPENAI_API_KEY") or st.session_state.openai_token != "None":    
        openai_client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
    for _ in range(multiplier):
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant who follows instruction."},
                {"role": "user", "content": a_prompt}
            ]
            )
        responses.append(response.choices[0].message.content)
    return responses

def select_llm() -> None:
    llm_list=st.session_state.evaluator_llm_list
    evaluating_model = "None"
    container = st.empty()
    container.empty()
    with container.container():
        # Ask for which model to be evaluated
        evaluating_model = st.multiselect(
            "Please select ONE model to be the evaluator model",
            llm_list,
            default=None
        )
        if evaluating_model:
            st.write(f"You selected {evaluating_model}")
            st.write("Please make sure the selected model can generate text (not images/videos/sounds).")
            st.write("Once you are ready, please click Continue")
            if st.button("Continue"):
                container.empty()
                st.session_state.selected_llm = evaluating_model
    return None



# Main Streamlit app starts here

# Verify the user's role
if st.session_state.role not in ["admin", "user"]:
    st.warning("You do not have permission to view this page.")
    st.stop()

col1, col2 = st.columns([0.05,0.9])
with col1:
    st.write(" ")
with col2:
    st.title("Generate Benchmarking Dataset")
if not st.session_state.healthcheck_passed:
    st.warning("System health checking is not passed or not performed. Please run health check.")
    st.stop()

if "Yes" in st.session_state.use_default_dataset:
    st.markdown("**You have decided to use the default benchmark dataset instead of generating a new one.** If you want to reverse this decision, please go back to Health Check.")
else:
    confirmed_setting = False
    container = st.empty()
    next = False

    if st.session_state.selected_llm == "None":
        select_llm()
    if st.session_state.selected_llm != "None":
        st.write(f"Evaluator: {st.session_state.selected_llm}")
        container.empty()
        with container.container():
            batch_size = st.slider(
                "Select the size of scenario setence describing a behavioral construct & compliance/noncompliant pair",
                1000,10000,3000,1000
            )
            rate_per_minute = st.slider(
                "Select the request's rate-per-minute",
                2,1000,10,10
            )
            st.write("Please double check and make sure the settings are within the evaluator's system constraint. Once you are done, please confirm.")
            confirmed_setting = st.button("Confirm settings")
        # rate per minute is first dependent on your text generation endpoint constraint
        # rate per minute should be much smaller than batch size and be divisible by batch size
        batch_num = int(batch_size/rate_per_minute)
        ollama_evaluator_model = st.session_state.selected_llm
        
        if confirmed_setting:
            container.empty()
            #pause = container.button("Pause")
            with st.spinner("Generating description of behavioral constructs' libraries, please wait..."):
                if "demo" in st.session_state.selected_llm:
                    st.write("Behavioral constructs' description libraries generated :heavy_check_mark: ")
                else:
                    # generating the benchmark dataset
                    for flag in flag_list:
                        for construct in construct_list:
                            responses = []
                            # Filter the DataFrame based on the current construct and flag
                            filtered_rows = promptseed_df[(promptseed_df['Constructs'] == construct) & (promptseed_df['Flag'] == flag)]
                            
                            # Extract the 'Prompt' column values and extend the extracted_prompts list
                            extracted_prompts = filtered_rows['Prompt'].tolist()
                            for prompt in extracted_prompts:
                                if llm_framework=="ollama":
                                    for _ in range (batch_size):
                                        response = get_ollama_response(ollama_evaluator_model,prompt)
                                        result = str(response['response'])
                                        responses.extend(result)
                                if llm_framework=="openai":
                                    for _ in range(batch_num): # loop through batches
                                        batch_result1 = get_openai_response(prompt,int(rate_per_minute/2))
                                        responses.extend(batch_result1)
                                        time.sleep(30)
                                        if len(batch_result1) > int(rate_per_minute/2)-3:
                                            batch_result2 = get_openai_response(prompt,int(rate_per_minute/2))
                                            responses.extend(batch_result2)
                                            time.sleep(30)
                            
                            file_name = f"Ollagen_{construct}_{flag}.csv"
                            output_path = os.path.join(output_folder, file_name)
                            with open(output_path, 'w') as file:
                                file.writelines([item + '\n' for item in responses])
                    st.write("Behavioral constructs' description libraries generated :heavy_check_mark: ")
            with st.spinner("Generating benchmark dataset, please wait..."):
                if "demo" in ollama_evaluator_model:
                    st.write("Benchmark dataset generated :heavy_check_mark: ")
                else:
                    run_result = subprocess.run([f"{sys.executable}", "pages/OllaGen1.py", st.session_state.ollama_endpoints],capture_output=True, text=True)
                    container.write("Results of generating QA datasets: ")
                    container.write(run_result.stdout)
                    container.write("Encountered errors (if any):")
                    container.write(run_result.stderr)
                    st.write("Benchmark dataset generated :heavy_check_mark: ")

st.write("When you are ready, please click the below button to proceed.")
next = st.button("Generate Responses")
if next:
    st.switch_page("pages/OllaBench_gui_generate_responses.py")

