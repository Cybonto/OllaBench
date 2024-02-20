#!/usr/bin/env python
# coding: utf-8

# IMPORTS

## Import Python Libraries
import os
import doctest
import datetime
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

## Import local modules
#- n/a

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
QA_TF_inpath = params["QA_TF_inpath"]
QA_WCP_inpath = params["QA_WCP_inpath"]
QA_WHO_inpath = params["QA_WHO_inpath"] 
QA_TF_outpath = params["QA_TF_outpath"]
QA_WCP_outpath = params["QA_WCP_outpath"]
QA_WHO_outpath = params["QA_WHO_outpath"] 

if llm_framework=="ollama": # only support Ollama as the eval target framework at the moment
    from ollama import Client
    client = Client(host=llm_endpoints)

# Prepare the list of targetted LLM models
llm_list = [d[next(iter(d))] for d in ollama.list()['models']] #get model names from the list of dict returned by Ollama
if llm_models=="all":
    llm_models=llm_list
else:
    llm_names_bak=llm_models.copy()
    llm_models[:] = [item for item in llm_models if item in llm_list] #remove model names that are not installed
    print("The following models were not pulled in Ollama: "+str([item for item in llm_names_bak if item not in llm_models]))

# FUNCTIONS

def load_csv_to_dataframe(file_path):
    try:
        # Load the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")

def write_df_to_csv(df, csv_file):
    # If the CSV file already exists, append to it, otherwise create a new file
    mode = 'a' if os.path.exists(csv_file) else 'w'

    # Write the DataFrame to CSV
    df.to_csv(csv_file, mode=mode, index=False)
    
def test_models(tries,llm_models):
    """
    A function to check for bad LLM models.
    
    Parameters:
    tries: the number of failed attempts before reporting
    llm_models: a list of targeted LLM models
    
    Returns:
    bad_models : a list of models that fail to load
    """
    bad_models=[]
    for a_model in llm_models:
        while tries>0:
            try:
                response = ollama.chat(model=a_model, messages=[{'role': 'user', 'content': 'Just say Yes'}])
                tries=0
            except Exception as e:
                tries-=1
                response = str(e) #"error" wil be in response
        if "error" in response:
            bad_models.append(a_model)
    if len(bad_models)>0:
        print("The following models are bad: "+str(bad_models))
    return bad_models

def check_answer (reference, answer):
    """
    Check if the correct answer (reference) is within the first two sentences of a model's answer.
    
    Parameters:
    reference : the reference answer
    answer : the model's answer
    
    Returns:
    True or False
    """
    # Tokenize string2 into sentences
    sentences = sent_tokenize(answer)

    # Combine the first two sentences into one string
    first_two_sentences = ' '.join(sentences[:2])

    # Check if string1 is in the combined first two sentences
    if reference in first_two_sentences:
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
    for index, row in input_df.iterrows():
        score=0
        notes='none'
        response = ollama.generate(model='llama2', prompt= str(row["Context"]+row["Question"]), stream=False)
        if check_answer(str(row['Answer']).lower(),str(response['response']).lower()):
            # give score if reference answer is within the first two sentences of model's answer
            score = 1
        elif str(row['Answer']).lower() in str(response['response']).lower():
            # if correct answer exist somewhere else, flag for human verification
            notes = "Needs verification"
        results.append([row['ID'], row['Context'], row['Question'], row['Answer'],
                        response['model'],response['total_duration'],response['eval_count'],
                        response['response'],score, notes
                        ])
    results_df = pd.DataFrame(results,columns=['ID', 'Context', 'Question', 'Reference Answer',
                                                    'Model','Total Duration','Eval Counts','Model Response',
                                                    'Score','Notes'
                                                    ])
    return results_df
    
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
QA_TF_df = load_csv_to_dataframe(QA_TF_inpath)
QA_WCP_df = load_csv_to_dataframe(QA_WCP_inpath)
QA_WHO_df = load_csv_to_dataframe(QA_WHO_inpath)

# Test load all targeted models first and remove models that failed to load
bad_models = test_models(tries,llm_models)
llm_models = [item for item in llm_models if item not in bad_models]

# Get Results
for a_model in llm_models:
    if len(QA_TF_df)>0:
        QA_TF_result_df = grade_model(a_model,QA_TF_df)
        write_df_to_csv(QA_TF_result_df,QA_TF_outpath)
    if len(QA_WCP_df)>0:
        QA_WCP_result_df = grade_model(a_model,QA_WCP_df)
        write_df_to_csv(QA_WCP_result_df,QA_WCP_outpath)
    if len(QA_WHO_df)>0:
        QA_WHO_result_df = grade_model(a_model,QA_WHO_df)
        write_df_to_csv(QA_WHO_result_df,QA_WHO_outpath)

