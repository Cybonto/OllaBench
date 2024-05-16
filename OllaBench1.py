#!/usr/bin/env python
# coding: utf-8

# OllaBench1 v.0.2
# IMPORTS

## Import Python Libraries
import os
import doctest
import datetime
from datetime import datetime
import time
import random
import contextlib

import itertools
import copy
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import csv
import json

import ollama
import nltk
from nltk.tokenize import sent_tokenize


params_path="params.json"
params={}
# Read the parameters from the JSON file
try:
    with open(params_path, 'r') as file:
        params = json.load(file)   
except FileNotFoundError:
    print(f"The file {params_path} was not found.")
except json.JSONDecodeError:
    print(f"Error decoding JSON from the file {params_path}.")
# Initialize variables
llm_framework = params["llm_framework"]
llm_endpoints = params["llm_endpoints"]
llm_models = params["llm_models"]
llm_leaderboard = params["llm_leaderboard"]
tries = params["bench_tries"]
QA_inpath = params["QA_inpath"] 

if llm_framework=="ollama": # only support Ollama as the eval target framework at the moment
    from ollama import Client
    client = Client(host=llm_endpoints)

'''
if llm_framework=="openai":
    from openai import OpenAI
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
if llm_framework=="llama_index":
    from llama_index.llms import LocalTensorRTLLM
    def completion_to_prompt(completion: str) -> str:
        """
        Given a completion, return the prompt using llama2 format.
        """
        return f"<s> [INST] {completion} [/INST] "
    llm = LocalTensorRTLLM(
    model_path="./model",
    engine_name="llama_float16_tp1_rank0.engine",
    tokenizer_dir="meta-llama/Llama-2-13b-chat",
    completion_to_prompt=completion_to_prompt)
'''

# Prepare the list of targetted LLM models
llm_list = [d[next(iter(d))] for d in ollama.list()['models']] #get model names from the list of dict returned by Ollama
if llm_models=="all":
    llm_models=llm_list
else:
    llm_names_bak=llm_models.copy()
    llm_models[:] = [item for item in llm_models if item in llm_list] #remove model names that are not installed
    print("The following model(s) does not exist in Ollama: "+str([item for item in llm_names_bak if item not in llm_models]))


# FUNCTIONS

def write_df_to_csv(df, csv_file):
    # If the CSV file already exists, append to it, otherwise create a new file
    mode = 'a' if os.path.exists(csv_file) else 'w'

    # Write the DataFrame to CSV
    df.to_csv(csv_file, mode=mode, index=False)
    
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

def get_response(llm_framework,a_model,a_prompt):
    if llm_framework =="ollama":
        result = ollama.generate(model=a_model, prompt= a_prompt, stream=False)
        while "eval_duration" not in result:
            time.sleep(1)
    return result

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
        #print(context)
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
            print(".", end =" ", flush=True)
        
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
    print(" ")
    return results_df

def df_2_chunks (a_df,chunk_size):
    """
    Function description.
    
    Parameters:
    param : param description
    
    Returns:
    value : value description
    """
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
        
def function_template ():
    """
    Function description.
    
    Parameters:
    param : param description
    
    Returns:
    value : value description
    """
    try:
        return
        # function code here
    except Exception as e:
        return f"An error occurred: {str(e)}"
    

## MAIN

# Load QA datasets
QA_df = pd.read_csv(QA_inpath,header=0)
# Split to chunks
chunk_size = 500
QA_df_chunks = df_2_chunks(QA_df,chunk_size)
greenlight = True
greenlight2 = True

# Get Results
for a_model in llm_models:
    while not greenlight:
        time.sleep(10)
    greenlight=False # turn off greenlight here, pay attn to when it will be turned on again!
    test_passed = test_model(tries,a_model)
    if test_passed:
        for index,QA_df_chunk in enumerate(QA_df_chunks):
            while not greenlight2:
                time.sleep(60)
            greenlight2=False # turn off greenlight2 here, pay attn to when it will be turned on again!
            print(f"Load chunk {index}")
            QA_outpath = a_model.replace(":","-")+"_chunk"+str(index)+"_"+datetime.now().strftime("%Y-%m-%d_%H-%M")+"_QA_Results.csv"
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
    else:
        print(f"There are issues with loading {a_model}. Skip the grading of this model.")
        print(" ")

