import os
import datetime
from datetime import datetime
import time
import pandas as pd
import csv
import re
import streamlit as st
import ollama
from ollama import Client
from OllaBench_gui_menu import menu_with_redirect, show_header
import nltk
from nltk.tokenize import sent_tokenize

st.set_page_config(
    page_title="Generate Responses",
    initial_sidebar_state="expanded"
)

show_header()
menu_with_redirect()
if not st.session_state.healthcheck_passed:
    st.warning("System health checking is not passed or not performed. Please run health check.")
    st.stop()
    
if "selected_llm" not in st.session_state:
    st.session_state.selected_llm = "None"
if "app_state" not in st.session_state:
    st.session_state.apt_state = "load llm"

# Initialize variables
llm_framework = "ollama"
llm_endpoints = st.session_state.llm_endpoints
llm_models = ""
tries = 3
QA_inpath = "pages/OllaGen1-QA-full.csv" 

if llm_framework=="ollama": # only support Ollama as the eval target framework at the moment
    client = Client(host=llm_endpoints)

def df_2_chunks (a_df,chunk_size):
    try:
        # Calculate the total number of chunks to be created
        num_chunks = len(a_df) // chunk_size + (1 if len(a_df) % chunk_size else 0)
        chunks=[]
        for i in range(num_chunks):
            # Slice the DataFrame to create a chunk
            start_row = i * chunk_size
            end_row = start_row + chunk_size
            chunk = a_df[start_row:end_row]
    
            # Append the chunk to the list of chunks
            chunks.append(chunk)
        return chunks
    except Exception as e:
        return f"An error occurred: {str(e)}"

def write_df_to_csv(df, csv_file):
    # If the CSV file already exists, append to it, otherwise create a new file
    mode = 'a' if os.path.exists(csv_file) else 'w'

    # Write the DataFrame to CSV
    df.to_csv(csv_file, mode=mode, index=False)

def display_progress(n):
    # Calculate the number of squares
    num_squares = (n + 49) // 50

    # Initialize progress list with False (grey) indicating incomplete
    progress = [False] * num_squares

    # Streamlit application
    #st.subheader("Current progress")
    progress_placeholder = st.empty()

    # Function to update progress display
    def update_progress():
        with progress_placeholder.container():
            cols = st.columns(40)  # Create 40 columns for a single row

            for i in range(num_squares):
                col_index = i % 40  # Determine the column index
                color = "green" if progress[i] else "Gainsboro"
                cols[col_index].write(
                    f"<div style='width:10px; height:10px; background-color:{color}; display:inline-block; margin:2px;'></div>",
                    unsafe_allow_html=True
                )

    # Main loop to update progress
    for i in range(n // 50 + 1):
        if i > 0:
            progress[i-1] = True
        update_progress()
        time.sleep(0.2)  # Simulate progress

def get_response(llm_framework,a_model,a_prompt):
    if llm_framework =="ollama":
        result = ollama.generate(model=a_model, prompt= a_prompt, stream=False)
        while "eval_duration" not in result:
            time.sleep(1)
    return result

def test_model(tries,a_model):
    """
    A function to check for bad LLM models.
    
    Parameters:
    tries: the number of failed attempts before reporting
    llm_models: a list of targeted LLM models
    
    Returns:
    True if the model is good
    """
    print(f"Test loading of {a_model}")
    if "demo" in a_model:
        return True
    else:
        while tries>0:
            try:
                response = get_response(llm_framework,a_model,'just say yes')
                return True
            except Exception as e:
                tries-=1
                response = str(e) #"error" wil be in response
        if "error" in response:
            print(f"The model {a_model} is bad.")
    return False 

def check_answer (reference, answer):
    """
    Check if the correct answer (reference) is within the first two sentences of a model's answer.
    Parameters:
    reference : the reference answer
    answer : the model's answer
    Returns:
    True or False
    """
    norm_ref1 = str(reference).lower()
    norm_ref2 = norm_ref1.split(" - ")[0]
    norm_ref3 = norm_ref1.split(" - ")[1]
    norm_ref4 = norm_ref2.replace("option ","")
    ans_keys = (norm_ref1, norm_ref2, norm_ref3, norm_ref4)
    norm_answer = str(answer).lower()

    # Tokenize string2 into sentences
    sentences = sent_tokenize(norm_answer)

    # Combine the first two sentences into one string
    first_two_sentences = ' '.join(sentences[:2])

    # Check if string1 is in the combined first two sentences
    if any(ans_key in first_two_sentences for ans_key in ans_keys):
        return True
    else:
        return False
    
def grade_model(a_model,input_df):
    """
    A function to grade an LLM model's responses
    
    Parameters:
    a_model : the target LLM model
    input_df : input dataframe that is consistent with OllaGen1 output format
    
    Returns:
    Results_df : a result df with input_df columns and additional columns of
    'Model','Total Duration','Eval Counts','Model Response','Score','Notes'
    """
    results=[]

    print(f"Grading {a_model}")
    # load the model in Ollama
    get_response("ollama",a_model,'just say yes')

    turn = 0
    for index, row in input_df.iterrows():
        while turn != index:
            time.sleep(10)

        score=0
        context = f"""
            Here are the intelligence about {row["P1_name"]} with comments from trusted experts and/or {row["P1_name"]}'s recorded statement(s).
            {row["P1_profile"]}
            Here are the intelligence about {row["P2_name"]} with comments from trusted experts and/or {row["P2_name"]}'s recorded statement(s).
            {row["P2_profile"]}

            """
        WCP_Question = row["WCP_Question"]
        WCP_Answer = row["WCP_Answer"]
        WCP_score = 0
        WHO_Question = row["WHO_Question"]
        WHO_Answer = row["WHO_Answer"]
        WHO_score = 0
        TeamRisk_Question = row["TeamRisk_Question"]
        TeamRisk_Answer = row["TeamRisk_Answer"]
        TeamRisk_score = 0
        TargetFactor_Question = row["TargetFactor_Question"]
        TargetFactor_Answer = row["TargetFactor_Answer"]
        TargetFactor_score = 0

        WCP_response = get_response("ollama",a_model,str(context+WCP_Question))
        while "eval_duration" not in WCP_response:
            time.sleep(1)
        if check_answer(WCP_Answer,WCP_response['response']):
            WCP_score = 1
        
        if "eval_duration" in WCP_response:
            WHO_response = get_response("ollama",a_model,str(context+WHO_Question))
            while "eval_duration" not in WHO_response:
                time.sleep(1)
            if check_answer(WHO_Answer,WHO_response['response']):
                WHO_score = 1
            if "eval_duration" in WHO_response:
                TeamRisk_response = get_response("ollama",a_model,str(context+TeamRisk_Question))
                while "eval_duration" not in TeamRisk_response:
                    time.sleep(1)
                if check_answer(TeamRisk_Answer,TeamRisk_response['response']):
                    TeamRisk_score = 1
                if "eval_duration" in TeamRisk_response:
                    TargetFactor_response = get_response("ollama",a_model,str(context+TargetFactor_Question))
                    while "eval_duration" not in TargetFactor_response:
                        time.sleep(1)
                    if check_answer(TargetFactor_Answer,TargetFactor_response['response']):
                        TargetFactor_score = 1
                    if "eval_duration" in TargetFactor_response:
                        score = WCP_score+WHO_score+TeamRisk_score+TargetFactor_score

                        results.append([row['ID'], a_model, str(context), WCP_Question, WCP_Answer,
                                        WCP_response['total_duration'],WCP_response['eval_count'], str(WCP_response['response']),WCP_score,
                                        WHO_Question, WHO_Answer,
                                        WHO_response['total_duration'],WHO_response['eval_count'], str(WHO_response['response']),WHO_score,
                                        TeamRisk_Question, TeamRisk_Answer,
                                        TeamRisk_response['total_duration'],TeamRisk_response['eval_count'], str(TeamRisk_response['response']),TeamRisk_score,
                                        TargetFactor_Question, TargetFactor_Answer,
                                        TargetFactor_response['total_duration'],TargetFactor_response['eval_count'], str(TargetFactor_response['response']),TargetFactor_score,
                                        score
                                        ])
                        turn += 1
        if index%50==0:
            st.write(".", end =" ")
        
    results_df = pd.DataFrame(results,columns=['ID', 'Model', 'Context', 'WCP_Question', 'WCP_Correct_Answer',
                                                    'WCP_TotalDuration','WCP_EvalCounts','WCP_Response','WCP_score',
                                                    'WHO_Question', 'WHO_Correct_Answer',
                                                    'WHO_TotalDuration','WHO_EvalCounts','WHO_Response','WHO_score',
                                                    'TeamRisk_Question', 'TeamRisk_Correct_Answer',
                                                    'TeamRisk_TotalDuration','TeamRisk_EvalCounts','TeamRisk_Response','TeamRisk_score',
                                                    'TargetFactor_Question', 'TargetFactor_Correct_Answer',
                                                    'TargetFactor_TotalDuration','TargetFactor_EvalCounts','TargetFactor_Response','TargetFactor_score',
                                                    'Total score'
                                                    ])
    st.write(" ")
    return results_df

def generate_responses() -> None:
    container = st.empty()
    temp = ""
    with st.spinner('Loading QA dataset...'):
        # Load QA datasets
        QA_df = pd.read_csv(QA_inpath,header=0)
    # Split to chunks
    chunk_size = 500
    QA_df_chunks = df_2_chunks(QA_df,chunk_size)
    response_folder="pages/responses"
    os.makedirs(response_folder, exist_ok=True)
    greenlight = True
    greenlight2 = True
    with container.container():
        for a_model in st.session_state.selected_llm:
            with st.expander(f"Collecting responses from {a_model}"):
                if "demo" in a_model:
                    n = 2000
                    display_progress(n)
                else:
                    while not greenlight:
                        time.sleep(10)
                    greenlight=False # turn off greenlight here, pay attn to when it will be turned on again!
                    test_passed = test_model(tries,a_model)
                    if test_passed:
                        for index,QA_df_chunk in enumerate(QA_df_chunks):
                            while not greenlight2:
                                time.sleep(60)
                            greenlight2=False # turn off greenlight2 here, pay attn to when it will be turned on again!
                            st.write(f"Load chunk {index}")
                            QA_outpath = response_folder+a_model.replace(":","-")+"_chunk"+str(index)+"_"+datetime.now().strftime("%Y-%m-%d_%H-%M")+"_QA_Results.csv"
                            if len(QA_df)>0:
                                QA_result_df = grade_model(a_model,QA_df_chunk)
                                if len(QA_result_df)>0:
                                    write_df_to_csv(QA_result_df,QA_outpath)
                                    print(f"Graded results were saved to {QA_outpath}")
                                    greenlight2 = True
                                else:
                                    print(f"Result is empty. Nothing was saved to {QA_outpath}")
                                    greenlight2 = True
                            else:
                                print("Input dataframe is empty. Program exiting.")
                                greenlight2 = True
                        greenlight=True
        st.write("Please continue to :bar_chart: Evaluate Models")
    
    return None

def select_llm() -> None:
    container = st.empty()
    llm_list=""
    selected_llm_list = ""
    if st.session_state.llm_endpoints != "demo":
        try:
            llm_list = [d[next(iter(d))] for d in ollama.list()['models']] #get model names from the list of dict returned by Ollama
        except:
            st.error('Cannot connect to the Ollama endpoint. Please run health check again.', icon="🚨")
    if st.session_state.llm_endpoints == "demo":
        llm_list = ["demo-llama3", "demo-wizardlm2", "demo-qwen", "demo-openhermes", "demo-tinyllama"]

    # Ask for which model to be evaluated
    if len(llm_list)>0:
        with container.container():
            llm_models = st.multiselect(
                "Please select which model to be evaluated",
                llm_list, on_change=None
            )
            if st.checkbox("Select all models"):
                llm_models = llm_list
            if st.button("Confirm selection"):
                st.session_state.selected_llm = llm_models
                st.session_state.apt_state = "generate responses"
                container.empty()
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
    st.title("Generate Models' Responses")

main_container=st.empty()
with main_container.container():
    st.markdown(f"You are using the endpoint of: {st.session_state.llm_endpoints}.")
    #if st.session_state.apt_state == "load llm":
    select_llm()
    if st.session_state.apt_state == "generate responses":   
        generate_responses()