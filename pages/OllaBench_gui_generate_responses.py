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
from OllaBench_gui_menu import menu_with_redirect, show_header, display_progress
import nltk
from nltk.tokenize import sent_tokenize
import openai
from openai import OpenAI
import anthropic
from anthropic import Anthropic
import google.generativeai as google
# test and download punkt if necessary
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

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
    st.session_state.app_state = "New"
if "response_root_folder" not in st.session_state:
    st.session_state.response_root_folder = "pages/responses/"
if "response_folder" not in st.session_state:
    st.session_state.response_folder = "None"
if "response_path" not in st.session_state:
    st.session_state.response_path = "None"
if "num_questions" not in st.session_state:
    st.session_state.num_questions = 0
if "chunk_size" not in st.session_state:
    st.session_state.chunk_size = 0
    
# Initialize variables
llm_framework = st.session_state.evaluatee_framework
llm_endpoints = st.session_state.ollama_endpoints
llm_models = st.session_state.selected_llm
tries = 3
QA_inpath = "pages/OllaGen1-QA-full.csv" 

if llm_framework=="ollama": # only support Ollama as the eval target framework at the moment
    client = Client(host=llm_endpoints)

def click_confirm():
    st.session_state.app_state = "confirm settings"
def click_revise():
    st.session_state.app_state = "New"
def click_proceed():
    st.session_state.app_state = "generate responses"

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


def get_response(llm_framework,a_model,a_prompt):
    result=""
    if llm_framework =="ollama":
        result = ollama.generate(model=a_model, prompt= f"You are a helpful assistant who follows instruction. {a_prompt}", stream=False)
    elif llm_framework == "openai":   
        openai_client = OpenAI(api_key=st.session_state.openai_token,)
        begin_epoch = int(time.time())
        response = openai_client.chat.completions.create(
            model=a_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant who follows instruction."},
                {"role": "user", "content": a_prompt}
            ]
            )
        result = { # the following normalize openai's responses to targetted ollama fields
            'response': response.choices[0].message.content,
            'eval_count': response.usage.completion_tokens,
            'total_duration': int(response.created-begin_epoch)
        }
    elif llm_framework == "anthropic":   
        anthropic_client = anthropic.Anthropic(api_key=st.session_state.anthropic_token)
        begin_epoch = int(time.time())
        response = anthropic_client.messages.create(
            model=a_model,
            max_tokens=1000,
            system="You are a helpful assistant who follows instruction.",
            messages=[
                {"role": "user", "content": a_prompt}
            ]
        )
        end_epoch = int(time.time())
        result = { # the following normalize anthropic's responses to targetted ollama fields
            'response': response.content[0].text,
            'eval_count': response.usage.output_tokens,
            'total_duration': int(end_epoch-begin_epoch)
        }
    elif llm_framework == "google":   
        google_client = google.GenerativeModel(a_model)
        begin_epoch = int(time.time())
        response = google_client.generate_content(f"You are a helpful assistant who follows instruction. {a_prompt}")
        end_epoch = int(time.time())
        gemini_text = ""
        for chunk in response:
            try:
                gemini_text += str(chunk.text)
            except: # when chunk exists but chunk text does not exist
                gemini_text += "Blocked chunk - " #google probably blocked chunk text
        result = { # the following normalize google's responses to the our targetted ollama fields
            'response': gemini_text,
            'eval_count': google_client.count_tokens(gemini_text).total_tokens,
            'total_duration': int(end_epoch-begin_epoch)
        }
    else:
        result = "n/a"
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
    norm_ref1 = str(reference).lower() # the whole correct answer in lower case
    norm_ref2 = norm_ref1.split(" - ")[0] # (option x) of the correct answer
    norm_ref3 = norm_ref1.split(" - ")[1] # the main content of the answer
    norm_ref4 = norm_ref2.replace("option ","") #(x) from (option x) of the correct answer
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
    
def grade_model(a_model,df):
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
    turn = 0
    evaluatee_framework = st.session_state.evaluatee_framework
    status = st.empty()
    progress = st.empty()
    input_df = df.reset_index(drop=True) # very important to reset original chunk index to make turn counting work
    for index, row in input_df.iterrows():
        #st.write(f"Turn {turn}-{index}")
        while turn != index:
            time.sleep(10)
        with progress.container():
            if (index)%50==0:
                display_progress(len(input_df),(index+1))
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

        WCP_response = get_response(evaluatee_framework,a_model,str(context+WCP_Question))
        #status.write(WCP_response['response'])
        while 'total_duration' not in WCP_response:
            time.sleep(1)
        if check_answer(WCP_Answer,WCP_response['response']):
            WCP_score = 1
        
        if 'total_duration' in WCP_response:
            WHO_response = get_response(evaluatee_framework,a_model,str(context+WHO_Question))
            while 'total_duration' not in WHO_response:
                time.sleep(1)
            if check_answer(WHO_Answer,WHO_response['response']):
                WHO_score = 1
            if 'total_duration' in WHO_response:
                TeamRisk_response = get_response(evaluatee_framework,a_model,str(context+TeamRisk_Question))
                while 'total_duration' not in TeamRisk_response:
                    time.sleep(1)
                if check_answer(TeamRisk_Answer,TeamRisk_response['response']):
                    TeamRisk_score = 1
                if 'total_duration' in TeamRisk_response:
                    TargetFactor_response = get_response(evaluatee_framework,a_model,str(context+TargetFactor_Question))
                    while 'total_duration' not in TargetFactor_response:
                        time.sleep(1)
                    if check_answer(TargetFactor_Answer,TargetFactor_response['response']):
                        TargetFactor_score = 1
                    if 'total_duration' in TargetFactor_response:
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
                        
        status.empty()
        status.write(f"Processed row {index}")
        turn += 1
        
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
    status.empty()
    progress.empty()
    with progress.container():
        display_progress(len(input_df),len(input_df))
    return results_df

def generate_responses(a_df, start_chunk) -> None:
    # Trim QA_df per setting
    QA_df = a_df.head(st.session_state.num_questions)
    # Split to chunks
    chunk_size = st.session_state.chunk_size
    QA_df_chunks = df_2_chunks(QA_df,chunk_size) #get a list of chunks
    response_folder=st.session_state.response_folder

    # green light protocol for ensuring sequential execution of llm tasks
    greenlight = True
    greenlight2 = True

    for a_model in st.session_state.selected_llm:
        with st.expander(f"**COLLECTING RESPONSES FROM {st.session_state.evaluatee_framework}-{a_model}**"):
            if "demo" in a_model:
                n = 2000
                display_progress(n,n)
            else:
                while not greenlight:
                    time.sleep(10)
                greenlight=False # turn off greenlight here, pay attn to when it will be turned on again!

                if st.session_state.evaluatee_framework == "ollama":
                    test_passed = test_model(tries,a_model)
                if st.session_state.evaluatee_framework in ["openai","anthropic","google"]:
                    test_passed = True
                if test_passed:
                    for index,QA_df_chunk in enumerate(QA_df_chunks):
                        if index >= (start_chunk):
                            while not greenlight2:
                                time.sleep(60)
                            greenlight2=False # turn off greenlight2 here, pay attn to when it will be turned on again!
                            st.write(f"Process chunk {index}")
                            QA_outpath = st.session_state.response_path+a_model.replace(":","-")+"_chunk"+str(index)+"_"+datetime.now().strftime("%Y-%m-%d_%H-%M")+"_QA_Results.csv"
                            QA_result_df = grade_model(a_model,QA_df_chunk) #grade the whole chunk
                            if len(QA_result_df)>0:
                                write_df_to_csv(QA_result_df,QA_outpath)
                                #st.write(f"Graded results were saved to {QA_outpath}")
                                greenlight2 = True
                            else:
                                st.write(f"Result is empty. Nothing was saved to {QA_outpath}")
                                greenlight2 = True
                    greenlight=True
    st.write("When you are ready, please click the below button to proceed.")
    next = st.button("Evaluate Models")
    if next:
        st.switch_page("pages/OllaBench_gui_evaluate.py")
    
    return None

def confirm_settings(QA_df) -> None:
    st.write("**Let's review some settings:**")
    st.markdown(f"""
                - Your evaluatee model list is **{st.session_state.selected_llm}**
                - The evaluatee framework is **{st.session_state.evaluatee_framework}**
                - **{st.session_state.num_questions}** evaluating questions will be used.
                - Questions are grouped into chunks of size **{st.session_state.chunk_size}**.
                - Chunk processing with start with chunk **{st.session_state.start_chunk}**.
                - Model responses will be saved to **{st.session_state.response_folder}**
                """)
    if st.session_state.evaluatee_framework == "openai":
        st.markdown(f"- Your OpenAI key is ********{st.session_state.openai_token[-10:]}")
    if st.session_state.evaluatee_framework == "anthropic":
        st.markdown(f"- Your Anthropic key is ********{st.session_state.anthropic_token[-10:]}")
    if st.session_state.evaluatee_framework == "google":
        st.markdown(f"- Your Google key is ********{st.session_state.google_token[-10:]}")
    st.button("Proceeed", on_click=click_proceed())
    #st.button("Revise", on_click=click_revise())
    return None

def select_llm(QA_df) -> None:
    llm_list= st.session_state.evaluatee_llm_list
    response_folder = "None"
    response_folder_created = False

    # Ask for which model to be evaluated
    if len(llm_list)>0:
        llm_models = st.multiselect(
            "Please select which model to be evaluated",
            llm_list, on_change=None
        )
        if st.checkbox("Select all models"):
            llm_models = llm_list
        st.session_state.selected_llm = llm_models
        st.session_state.num_questions=st.slider("Select the number of evaluating questions:",10,int(len(QA_df)),int(len(QA_df)),10)
        st.session_state.chunk_size=st.slider("Select the preferred chunk size (questions per chunk):",100,1000,500,100)
        st.session_state.start_chunk = int(st.text_input("Start with chunk number", "0"))
        existing_folders = os.listdir(st.session_state.response_root_folder)
        existing_folders.append("None")
        if response_folder in existing_folders and not response_folder_created:
            response_folder = st.text_input("Enter a unique folder name for collecting results:")
            st.session_state.response_path = st.session_state.response_root_folder+response_folder+"/"
            try:
                os.makedirs(st.session_state.response_path)
                st.success(f'**{response_folder}** was successfully created.', icon="✅")
                st.session_state.response_folder = response_folder
                response_folder_created = True
                st.button("Confirm selection",on_click=click_confirm())
            except FileExistsError:
                st.error(f'The folder name of {response_folder} is not unique.', icon="🚨")
            except Exception as e:
                if response_folder:
                    st.error(f'{response_folder} was NOT created due {str(e)}. Please try a different name.', icon="🚨")
                    response_folder_created = False
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

with st.spinner('Loading QA dataset...'):
    # Load QA datasets
    QA_df = pd.read_csv(QA_inpath,header=0)

phase = st.session_state.app_state
if phase == "New":
    select_llm(QA_df) 
if phase == "confirm settings":
    confirm_settings(QA_df)
if phase == "generate responses":  
    generate_responses(QA_df,st.session_state.start_chunk)