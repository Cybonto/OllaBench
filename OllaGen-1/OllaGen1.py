#!/usr/bin/env python
# coding: utf-8

# In[48]:


# IMPORTS

## Import Python Libraries
import os
import doctest
import datetime
import time
import random
import itertools
from functools import reduce
import copy

#import ollama
#from ollama import AsyncClient
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import csv
import json


# In[ ]:


# Declare Prod Only Variables here
# Do NOT execute this cell in Dev
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
node_path = params['node_path']
edge_path = params['edge_path']
dict_path = params["dict_path"]
llm_framework = params["llm_framework"]
QA_questions = params["QA_questions"]
QA_core_outpath = params["QA_core_outpath"]
QA_full_outpath = params["QA_full_outpath"]

QA_coglength = 5
name_batch_size = 1000


# In[49]:


affect_com = []
affect_noncom = []
attitude_com = []
attitude_noncom = []
belief_com = []
belief_noncom = []
benefits_com = []
benefits_noncom = []
commitment_com = []
commitment_noncom = []
control_com = []
control_noncom = []
costs_com = []
costs_noncom = []
goal_com = []
goal_noncom = []
groupnorms_com = []
groupnorms_noncom = []
intent_com = []
intent_noncom = []
knowledge_com = []
knowledge_noncom = []
moral_com = []
moral_noncom = []
motivation_com = []
motivation_noncom = []
norms_com = []
norms_noncom = []
responseefficacy_com = []
responseefficacy_noncom = []
sbjnorm_com = []
sbjnorm_noncom = []
selfefficacy_com = []
selfefficacy_noncom = []
social_com = []
social_noncom = []
threatseverity_com = []
threatseverity_noncom = []
vulnerability_com = []
vulnerability_noncom = []
names = []


# In[50]:


# FUNCTIONS

if llm_framework=="openai":
    from openai import OpenAI
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
if llm_framework=="llamaindex":
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

def textlines_2_list(file_path):
    a_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        a_list = file.readlines()
        # Remove newline characters from each line
        a_list = [line.strip() for line in a_list]
    return a_list

def string_2_list (a_string):
    """
    Convert a comma separated text items in a string to a list
    
    Parameters:
    param : a_tring
    
    Returns:
    a_list : a list
    """
    try:
        # function code here
        a_string_cleaned = a_string.replace("[", "").replace("]", "").replace("[", "").replace("'", "").replace('"', '').replace(', ', ',')
        a_list = a_string_cleaned.split(',')
        return a_list
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def pop_a_sentence(a_construct_name):
    sentence=""
    match a_construct_name:
        case "affect_com":
            if len(affect_com)<=1:
                affect_com.extend(textlines_2_list("./templates/OllaGen_Affect_com.csv"))
                print ("Reloading affect_com entries")
            rand_i = random.randrange(len(affect_com))
            sentence = str(affect_com.pop(rand_i))
            return sentence
        case "affect_noncom":
            if len(affect_noncom)<=1:
                affect_noncom.extend(textlines_2_list("./templates/OllaGen_Affect_noncom.csv"))
            rand_i = random.randrange(len(affect_noncom))
            sentence = affect_noncom.pop(rand_i)
            return sentence
        case "attitude_com":
            if len(attitude_com)<=1:
                attitude_com.extend(textlines_2_list("./templates/OllaGen_Attitude_com.csv"))
            rand_i = random.randrange(len(attitude_com))
            sentence = attitude_com.pop(rand_i)
            return sentence
        case "attitude_noncom":
            if len(attitude_noncom)<=1:
                attitude_noncom.extend(textlines_2_list("./templates/OllaGen_Attitude_noncom.csv"))
            rand_i = random.randrange(len(attitude_noncom))
            sentence = attitude_noncom.pop(rand_i)
            return sentence
        case "belief_com":
            if len(belief_com)<=1:
                belief_com.extend(textlines_2_list("./templates/OllaGen_Belief_com.csv"))
            rand_i = random.randrange(len(belief_com))
            sentence = belief_com.pop(rand_i)
            return sentence
        case "belief_noncom":
            if len(belief_noncom)<=1:
                belief_noncom.extend(textlines_2_list("./templates/OllaGen_Belief_noncom.csv"))
            rand_i = random.randrange(len(belief_noncom))
            sentence = belief_noncom.pop(rand_i)
            return sentence
        case "benefits_com":
            if len(benefits_com)<=1:
                benefits_com.extend(textlines_2_list("./templates/OllaGen_Benefits_com.csv"))
            rand_i = random.randrange(len(benefits_com))
            sentence = benefits_com.pop(rand_i)
            return sentence
        case "benefits_noncom":
            if len(benefits_noncom)<=1:
                benefits_noncom.extend(textlines_2_list("./templates/OllaGen_Benefits_noncom.csv"))
            rand_i = random.randrange(len(benefits_noncom))
            sentence = benefits_noncom.pop(rand_i)
            return sentence
        case "commitment_com":
            if len(commitment_com)<=1:
                commitment_com.extend(textlines_2_list("./templates/OllaGen_Commitment_com.csv"))
            rand_i = random.randrange(len(commitment_com))
            sentence = commitment_com.pop(rand_i)
            return sentence
        case "commitment_noncom":
            if len(commitment_noncom)<=1:
                commitment_noncom.extend(textlines_2_list("./templates/OllaGen_Commitment_noncom.csv"))
            rand_i = random.randrange(len(commitment_noncom))
            sentence = commitment_noncom.pop(rand_i)
            return sentence
        case "control_com":
            if len(control_com)<=1:
                control_com.extend(textlines_2_list("./templates/OllaGen_Control_com.csv"))
            rand_i = random.randrange(len(control_com))
            sentence = control_com.pop(rand_i)
            return sentence
        case "control_noncom":
            if len(control_noncom)<=1:
                control_noncom.extend(textlines_2_list("./templates/OllaGen_Control_noncom.csv"))
            rand_i = random.randrange(len(control_noncom))
            sentence = control_noncom.pop(rand_i)
            return sentence
        case "costs_com":
            if len(costs_com)<=1:
                costs_com.extend(textlines_2_list("./templates/OllaGen_Costs_com.csv"))
            rand_i = random.randrange(len(costs_com))
            sentence = costs_com.pop(rand_i)
            return sentence
        case "costs_noncom":
            if len(costs_noncom)<=1:
                costs_noncom.extend(textlines_2_list("./templates/OllaGen_Costs_noncom.csv"))
            rand_i = random.randrange(len(costs_noncom))
            sentence = costs_noncom.pop(rand_i)
            return sentence
        case "goal_com":
            if len(goal_com)<=1:
                goal_com.extend(textlines_2_list("./templates/OllaGen_Goal_com.csv"))
            rand_i = random.randrange(len(goal_com))
            sentence = goal_com.pop(rand_i)
            return sentence
        case "goal_noncom":
            if len(goal_noncom)<=1:
                goal_noncom.extend(textlines_2_list("./templates/OllaGen_Goal_noncom.csv"))
            rand_i = random.randrange(len(goal_noncom))
            sentence = goal_noncom.pop(rand_i)
            return sentence
        case "groupnorms_com":
            if len(groupnorms_com)<=1:
                groupnorms_com.extend(textlines_2_list("./templates/OllaGen_Groupnorms_com.csv"))
            rand_i = random.randrange(len(groupnorms_com))
            sentence = groupnorms_com.pop(rand_i)
            return sentence
        case "groupnorms_noncom":
            if len(groupnorms_noncom)<=1:
                groupnorms_noncom.extend(textlines_2_list("./templates/OllaGen_Groupnorms_noncom.csv"))
            rand_i = random.randrange(len(groupnorms_noncom))
            sentence = groupnorms_noncom.pop(rand_i)
            return sentence
        case "intent_com":
            if len(intent_com)<=1:
                intent_com.extend(textlines_2_list("./templates/OllaGen_Intent_com.csv"))
            rand_i = random.randrange(len(intent_com))
            sentence = intent_com.pop(rand_i)
            return sentence
        case "intent_noncom":
            if len(intent_noncom)<=1:
                intent_noncom.extend(textlines_2_list("./templates/OllaGen_Intent_noncom.csv"))
            rand_i = random.randrange(len(intent_noncom))
            sentence = intent_noncom.pop(rand_i)
            return sentence
        case "knowledge_com":
            if len(knowledge_com)<=1:
                knowledge_com.extend(textlines_2_list("./templates/OllaGen_Knowledge_com.csv"))
            rand_i = random.randrange(len(knowledge_com))
            sentence = knowledge_com.pop(rand_i)
            return sentence
        case "knowledge_noncom":
            if len(knowledge_noncom)<=1:
                knowledge_noncom.extend(textlines_2_list("./templates/OllaGen_Knowledge_noncom.csv"))
            rand_i = random.randrange(len(knowledge_noncom))
            sentence = knowledge_noncom.pop(rand_i)
            return sentence
        case "moral_com":
            if len(moral_com)<=1:
                moral_com.extend(textlines_2_list("./templates/OllaGen_Moral_com.csv"))
            rand_i = random.randrange(len(moral_com))
            sentence = moral_com.pop(rand_i)
            return sentence
        case "moral_noncom":
            if len(moral_noncom)<=1:
                moral_noncom.extend(textlines_2_list("./templates/OllaGen_Moral_noncom.csv"))
            rand_i = random.randrange(len(moral_noncom))
            sentence = moral_noncom.pop(rand_i)
            return sentence
        case "motivation_com":
            if len(motivation_com)<=1:
                motivation_com.extend(textlines_2_list("./templates/OllaGen_Motivation_com.csv"))
            rand_i = random.randrange(len(motivation_com))
            sentence = motivation_com.pop(rand_i)
            return sentence
        case "motivation_noncom":
            if len(motivation_noncom)<=1:
                motivation_noncom.extend(textlines_2_list("./templates/OllaGen_Motivation_noncom.csv"))
            rand_i = random.randrange(len(motivation_noncom))
            sentence = motivation_noncom.pop(rand_i)
            return sentence
        case "norms_com":
            if len(norms_com)<=1:
                norms_com.extend(textlines_2_list("./templates/OllaGen_Norms_com.csv"))
            rand_i = random.randrange(len(norms_com))
            sentence = norms_com.pop(rand_i)
            return sentence
        case "norms_noncom":
            if len(norms_noncom)<=1:
                norms_noncom.extend(textlines_2_list("./templates/OllaGen_Norms_noncom.csv"))
            rand_i = random.randrange(len(norms_noncom))
            sentence = norms_noncom.pop(rand_i)
            return sentence
        case "responseefficacy_com" | "response-efficacy_com":
            if len(responseefficacy_com)<=1:
                responseefficacy_com.extend(textlines_2_list("./templates/OllaGen_ResponseEfficacy_com.csv"))
            rand_i = random.randrange(len(responseefficacy_com))
            sentence = responseefficacy_com.pop(rand_i)
            return sentence
        case "responseefficacy_noncom"| "response-efficacy_noncom":
            if len(responseefficacy_noncom)<=1:
                responseefficacy_noncom.extend(textlines_2_list("./templates/OllaGen_ResponseEfficacy_noncom.csv"))
            rand_i = random.randrange(len(responseefficacy_noncom))
            sentence = responseefficacy_noncom.pop(rand_i)
            return sentence
        case "sbjnorm_com" | "subjectivenorms_com":
            if len(sbjnorm_com)<=1:
                sbjnorm_com.extend(textlines_2_list("./templates/OllaGen_SbjNorm_com.csv"))
            rand_i = random.randrange(len(sbjnorm_com))
            sentence = sbjnorm_com.pop(rand_i)
            return sentence
        case "sbjnorm_noncom" | "subjectivenorms_noncom":
            if len(sbjnorm_noncom)<=1:
                sbjnorm_noncom.extend(textlines_2_list("./templates/OllaGen_SbjNorm_noncom.csv"))
            rand_i = random.randrange(len(sbjnorm_noncom))
            sentence = sbjnorm_noncom.pop(rand_i)
            return sentence
        case "selfefficacy_com" | "self-efficacy_com":
            if len(selfefficacy_com)<=1:
                selfefficacy_com.extend(textlines_2_list("./templates/OllaGen_SelfEfficacy_com.csv"))
            rand_i = random.randrange(len(selfefficacy_com))
            sentence = selfefficacy_com.pop(rand_i)
            return sentence
        case "selfefficacy_noncom" | "self-efficacy_noncom":
            if len(selfefficacy_noncom)<=1:
                selfefficacy_noncom.extend(textlines_2_list("./templates/OllaGen_SelfEfficacy_noncom.csv"))
            rand_i = random.randrange(len(selfefficacy_noncom))
            sentence = selfefficacy_noncom.pop(rand_i)
            return sentence
        case "social_com":
            if len(social_com)<=1:
                social_com.extend(textlines_2_list("./templates/OllaGen_Social_com.csv"))
            rand_i = random.randrange(len(social_com))
            sentence = social_com.pop(rand_i)
            return sentence
        case "social_noncom":
            if len(social_noncom)<=1:
                social_noncom.extend(textlines_2_list("./templates/OllaGen_Social_noncom.csv"))
            rand_i = random.randrange(len(social_noncom))
            sentence = social_noncom.pop(rand_i)
            return sentence
        case "threatseverity_com" | "threat-severity_com":
            if len(threatseverity_com)<=1:
                threatseverity_com .extend(textlines_2_list("./templates/OllaGen_ThreatSeverity_com.csv"))
            rand_i = random.randrange(len(threatseverity_com))
            sentence = threatseverity_com.pop(rand_i)
            return sentence
        case "threatseverity_noncom" | "threat-severity_noncom":
            if len(threatseverity_noncom)<=1:
                threatseverity_noncom.extend(textlines_2_list("./templates/OllaGen_ThreatSeverity_noncom.csv"))
            rand_i = random.randrange(len(threatseverity_noncom))
            sentence = threatseverity_noncom.pop(rand_i)
            return sentence
        case "vulnerability_com":
            if len(vulnerability_com)<=1:
                vulnerability_com.extend(textlines_2_list("./templates/OllaGen_Vulnerability_com.csv"))
            rand_i = random.randrange(len(vulnerability_com))
            sentence = vulnerability_com.pop(rand_i)
            return sentence
        case "vulnerability_noncom":
            if len(vulnerability_noncom)<=1:
                vulnerability_noncom.extend(textlines_2_list("./templates/OllaGen_Vulnerability_noncom.csv"))
            rand_i = random.randrange(len(vulnerability_noncom))
            sentence = vulnerability_noncom.pop(rand_i)
            return sentence
        case "names":
            if len(names)<=1:
                names.extend(textlines_2_list("./templates/OllaGen_Names.csv"))
            rand_i = random.randrange(len(names))
            sentence = names.pop(rand_i)
            return sentence
        case _:
            print("That's not a valid argument.")

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

def graph_plot (a_graph,a_title):
    """
    Take a networkx graph object, a title and plot them out.
    
    Parameters:
    a_graph : a networkx graph object
    a_title : the title for the plot
    
    Returns:
    result : a boolean value
    """
    result = ""
    try:
        plt.figure(figsize=(16, 12))
        node_pos=nx.shell_layout(a_graph, scale=4)
        nx.draw(a_graph,pos=node_pos, node_size=30, node_color='green', edge_color='grey')
        title_pos=node_pos
        for item in title_pos:
            title_pos[item][1] += 0.2
        nx.draw_networkx_labels(a_graph, pos = title_pos, font_size = 14)
        plt.title(a_title, size=25)
        plt.show()
        result=True
    except Exception as e:
        print("Error happens: "+e)
        # log errors as needed
        result=False
    return result

def csv_2_nlevel_dict (csv_file):
    """
    Convert a csv file to an n-level dictionary.
    
    Parameters:
    csv_file : the path to a csv file
    
    Returns:
    result_dict : an n-level dictionary
    """
    result_dict = {}
    try:
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # Skip header if present
            for row in reader:
                *keys, value = row  # Unpack all but the last item as keys, and the last item as value
                current_level = result_dict
                for key in keys[:-1]:  # Iterate over keys except for the last one
                    if key not in current_level:
                        current_level[key] = {}
                    current_level = current_level[key]
                # Set the value for the last key
                last_key = keys[-1]
                current_level[last_key] = value  # This will overwrite existing values for duplicate paths
        csvfile.close()
    except Exception as e:
        print("Error happens: "+e)
        # log errors as needed
        result_dict=False
    return result_dict

def print_dict(d, n, indent=0, counter=None):
    """
    Prints the first n items of a multi-level dictionary.
    
    :param d: The dictionary to print from.
    :param n: The number of items to print.
    :param indent: Current indentation level for pretty printing.
    :param counter: A mutable counter to track the number of items printed.
    """
    if counter is None:
        counter = [0]  # Initialize the counter if it's not provided

    if counter[0] >= n:
        return  # Stop if the desired number of items have already been printed
    
    for key, value in d.items():
        if counter[0] >= n:
            break  # Stop if the desired number of items have already been printed
        
        # Print the current item
        print('  ' * indent + str(key) + ':', end=' ')
        if isinstance(value, type(dict)):
            print()  # Print a newline before going deeper
            print_dict(value, n, indent + 1, counter)
        else:
            print(value)
            counter[0] += 1  # Increment the counter after printing a non-dictionary item

def get_random_item(two_level_dict, key1, key2):
    """
    Returns a random item from the list found at two_level_dict[key1][key2].

    :param two_level_dict: A dictionary containing dictionaries as values.
    :param key1: The key to access the first level dictionary.
    :param key2: The key to access the list in the second level dictionary.

    :return: A random item from the specified list, or None if the keys are not found.
    """
    try:
        # Access the nested dictionary and then the list
        value_list = list(two_level_dict[key1][key2])
        # Return a random item from the list
        return random.choice(value_list)
    except KeyError:
        # Return None if the specified keys are not found
        print("KeyError: The provided keys do not match the dictionary structure.")
        return None
    except IndexError:
        # Handle empty list
        print("IndexError: The list is empty.")
        return None

def get_response(a_prompt, engine="gpt-3.5-turbo"):
    """
    Takes a prompt and returns a response from local LLM or ChatGPT using the specified engine.

    Parameters:
    prompt (str): The input prompt
    engine (str): The engine to use for generating the response.

    Returns:
    str: The response.
    """
    try:
        response=""
        if llm_framework=="openai":
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": a_prompt,
                    }
                ],
                model=engine,
            )
            return response.choices[0].message.content
        
        if llm_framework=="llama_index":
            response = llm.complete(a_prompt)
            return str(response)
        if llm_framework=="ollama":
            response = ollama.generate(model='orca2:7b', prompt=a_prompt)
            return str(response['response'])
    except Exception as e:
        return f"An error occurred: {str(e)}"

def replace_n_random_items(main_list, second_list, n):
    """
    Replace n random elements of main_list with n random elements from second_list.
    
    Parameters:
    main_list (list): The original list to modify.
    second_list (list): The list from which to take replacement elements.
    n (int): The number of elements to replace.
    
    Returns:
    list: A new list with n random elements of main_list replaced by n random elements of second_list.
    """
    result = main_list.copy()
    candidates = second_list.copy()
    
    if n<len(result) and n<len(candidates): # Ensure n does not exceed the length of either list
        for _ in range(n):
            random_pos=random.randint(0, len(result) - 1)
            result.pop(random_pos)
        for _ in range(n):
            random_pos=random.randint(0, len(candidates) - 1)
            result.append(candidates.pop(random_pos))
    
    return result

def ollagen1_core(knowledge_graph,a_dict,profile_num,profile_length):
    """
    Generate core data for the dataset.
    
    Parameters:
    knowledge_graph : a networkx knowledge graph that was rigorously verified
    a_dict : a dictionary of prompt templates
    profile_num : the number of profiles to be generated
    profile_length : the length of the profile's cognitive behavioral path
    
    Returns:
    QA_core_df : a dataframe of generated content based on the provided params
    """
    print("Working on "+QA_core_outpath)
    P1_name=[]
    P1_cogpath=[]
    QA_core_P1_df = pd.DataFrame(columns=['ID','P1_name','P1_cogpath','P1_profile','P1_risk_score','P1_risk_profile'])
    QA_core_P2_df = pd.DataFrame(columns=['P2_name','P2_cogpath','P2_profile','P2_risk_score','P2_risk_profile'])
    QA_core_intel_df = pd.DataFrame(columns=['combined_risk_score','shared_risk_factor','targetted_factor'])

    # Setting up P1 data
    print("---- generating cognitive paths")
    random_paths = list(
        nx.generate_random_paths(
            knowledge_graph,
            sample_size=int(profile_num*1.25),
            path_length=(profile_length-1)
            )
        )
    counter=0
    for path in random_paths:
        if counter<profile_num:
            if len(path) <= len(set(path))+1:
            # Check if the sublist has duplicates by comparing its length to the length of its set
                P1_cogpath.append(path)
                counter+=1
        if counter%50==0:
            print(".", end =" ", flush=True)
    profile_num = len(P1_cogpath) # just in case the generated usable cogpaths is less than the specificed profile num
    P1_risk_score = random.choices([1,2,3],k=(profile_num))
  
    # Assign names to the official P1 list of names. We actually don't care if there are some duplicates in names.
    for i in range(profile_num):
        P1_name.append(pop_a_sentence("names"))

    # Preparing the rest of P1 data
    print("\n---- generating P1 stories")
    counter=0
    for name,cogpath,risk in zip(P1_name,P1_cogpath,P1_risk_score):
        profile=""
        risk_profile=[]
        risk-=1
        # prepare the risk profile flags
        if risk==0:
            flags=["com","com","com","com","com"].copy()
        elif risk==1:
            flags=["noncom","com","com","com","com"]
        elif risk==2:
            flags=["noncom","noncom","com","com","com"].copy()
        random.shuffle(flags)
        for item,flag in zip(cogpath,flags):
            a_construct = str(item)+"_"+str(flag)
            a_construct = a_construct.lower().replace(" ", "")
            #print(a_construct)
            story_line=pop_a_sentence(a_construct)
            #print(story_line)
            if story_line:
                profile+=" "+str(story_line)
            if flag=="noncom":
                risk_profile.extend([item])
        ID="Case_"+str(counter)
        QA_core_P1_df.loc[len(QA_core_P1_df.index)]=[ID,name,cogpath,profile,risk,risk_profile]
        QA_core_P2_df.loc[len(QA_core_P2_df.index)]=[name,cogpath,profile,risk,risk_profile]
        counter+=1
        if counter%50==0:
            print(".", end =" ", flush=True)
            time.sleep(10)
    
    shuffled_P2_df = QA_core_P2_df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Loop through P1 & P2
    print("\n---- generating additional intel")
    counter=0
    for (index1, p1), (index2, p2) in zip(QA_core_P1_df.iterrows(), shuffled_P2_df.iterrows()):
        shared_risk_factor=[]
        targetted_factor=[]
        # check for same person
        if index2==(len(shuffled_P2_df)-1):
            ptr=0
        else:
            ptr=index2+1
            
        while str(p1['P1_name'])==str(p2['P2_name']):
            # if same, copy the below row of P2 over existing P2 row, wrap over if it's the last row
            p2['P2_name']=shuffled_P2_df.iloc[ptr]['P2_name']
            shuffled_P2_df.iloc[index2] = shuffled_P2_df.iloc[ptr].values
            if ptr==(len(shuffled_P2_df)-1):
                ptr=0
            else:
                ptr+=1
        
        # calculate combined risk score
        # merge the two lists and remove duplicates by converting them to a set
        merged_risk_profile = list(set(p1['P1_risk_profile']+p2['P2_risk_profile']))
        possible_pairs= itertools.combinations(merged_risk_profile, 2)
        edges_num=sum(1 for pair in possible_pairs if knowledge_graph.has_edge(*pair))
        
        # combined risk score
        combined_risk_score=p1['P1_risk_score']+p2['P2_risk_score']+edges_num
        
        # identify shared risk factor
        shared_risk_factor = list(set(p1['P1_risk_profile']) & set(p2['P2_risk_profile']))
        if not shared_risk_factor:
            shared_risk_factor.append("none")
        
        # identify the most important factor for remediation
        pageranks = nx.pagerank(knowledge_graph)
        shared_risk_factor_pruned=shared_risk_factor
        try:
            shared_risk_factor_pruned.remove('Intent')
        except:
            pass
        if len(shared_risk_factor_pruned)==1 and ("none" not in shared_risk_factor_pruned):
            targetted_factor = shared_risk_factor
        elif len(shared_risk_factor_pruned)>1:
            # pick the risk factor with the highest PageRank
            filtered_pageranks = {node: pageranks.get(node) for node in shared_risk_factor_pruned if node in pageranks}
            targetted_factor.append(max(filtered_pageranks, key=filtered_pageranks.get))
        else:
            # pick the shared factor with the highest PageRank
            shared_factor=list(set(p1['P1_cogpath']) & set(p2['P2_cogpath']))
            try:
                shared_factor.remove('Intent')
            except:
                pass
            if len(shared_factor)>0:
                filtered_pageranks = {node: pageranks.get(node) for node in shared_factor if node in pageranks}
                targetted_factor.append(max(filtered_pageranks, key=filtered_pageranks.get))
            else:
            # pick the factor with the highest PageRank
                combined_factor=list(set(p1['P1_cogpath']+p2['P2_cogpath'])) 
                try:
                    combined_factor.remove('Intent')
                except:
                    pass
                filtered_pageranks = {node: pageranks.get(node) for node in combined_factor if node in pageranks}
                targetted_factor.append(max(filtered_pageranks, key=filtered_pageranks.get))   
        QA_core_intel_df.loc[len(QA_core_intel_df.index)]=[combined_risk_score,shared_risk_factor,targetted_factor]
        counter+=1
        if counter%50==0:
            print(".", end =" ", flush=True)
            #time.sleep(10)
    QA_core_df = pd.concat([QA_core_P1_df,shuffled_P2_df,QA_core_intel_df], axis=1)
    return QA_core_df

def ollagen1_WhichCogPath(core_df,knowledge_graph):
    """
    Generate "Which Cognitive Path" questions with reference answers.
    
    Parameters:
    core_df: OllaGen1's core dataframe
    knowledge_graph: Cybonto Knowledge Graph

    Returns:
    QA_WCP_df : a dataframe of generated content based on the provided params
    """
    print("---- generating Which Cog Path entries")
    # declare key variables
    question=""
    answer=""
    node_list = [row[0] for row in knowledge_graph.nodes(data=True)]
    QA_WCP_df = pd.DataFrame(columns=['ID','WCP_Question','WCP_Answer'])
    counter=0

    # Iterating over rows of core dataframe
    # Note the columns are:
    # "ID","P1_name","P1_cogpath","P1_profile","P1_risk_score","P1_risk_profile",
    # "P2_name","P2_cogpath","P2_profile","P2_risk_score","P2_risk_profile"
    # combined_risk_score,shared_risk_factor,targetted_factor
    for index, row in core_df.iterrows():
        #print(index, row['ID'], row['P1_name'])
        # declare more function-level variables
        keys=['a','b','c','d']
        # now start to generate the main content
        ID=row['ID']
        cogpath=random.choice([row['P1_cogpath'],row['P2_cogpath']])
        question="Which of the following options best reflects "+str(row['P1_name'])+"'s or "+str(row['P2_name'])+" cognitive behavioral constructs. Your answer must begin with (option "
        item1 = cogpath
        subtracted_node_list = list(filter(lambda item: item not in item1, node_list))
        item2 = replace_n_random_items(cogpath, subtracted_node_list, 2)
        subtracted_node_list = list(filter(lambda item: item not in item1+item2, node_list))
        item3 = replace_n_random_items(cogpath, subtracted_node_list, 2)
        subtracted_node_list = list(filter(lambda item: item not in item1+item2+item3, node_list))
        item4 = replace_n_random_items(cogpath, subtracted_node_list, 2)
        random.shuffle(item2)
        random.shuffle(item3)
        random.shuffle(item4)
        choices_list = [item1,item2,item3,item4]
        random.shuffle(choices_list)
        # start producing multiple choices
        for choice in choices_list:
            key=keys.pop(0)
            question+=os.linesep
            question+= "(option "+key+") - "+str(choice)
            #print("Choice: "+str(choice))
            if choice==cogpath:
                answer="(option "+key+") - "+str(choice)
        QA_WCP_df.loc[len(QA_WCP_df.index)]=[ID,question,answer]
        counter+=1
        if counter%50==0:
            print(".", end =" ")
    return QA_WCP_df

def ollagen1_WHO(core_df):
    """
    Generate "Who is Who" questions with reference answers.
    
    Parameters:
    core_df: OllaGen1 core data
    
    Returns:
    QA_WHO_df : a dataframe of generated content based on the provided params
    """
    print("---- generating Who is Who entries ")
    # declare key variables
    question=""
    answer=""
    QA_WHO_df = pd.DataFrame(columns=['ID','WHO_Question','WHO_Answer'])
    counter=0

    # Iterating over rows of core dataframe
    # Note the columns are:
    # "ID","P1_name","P1_cogpath","P1_profile","P1_risk_score","P1_risk_profile",
    # "P2_name","P2_cogpath","P2_profile","P2_risk_score","P2_risk_profile"
    # combined_risk_score,shared_risk_factor,targetted_factor
    for index, row in core_df.iterrows():
        #print(index, row['ID'], row['P1_name'])
        # declare more function-level variables
        keys=['a','b','c','d']
        # now start to generate the main content
        ID=row['ID']

        pick_order = random.choice([0,1])
        if pick_order==0:
            question="Who is MORE compliant with information security policies? Your answer must begin with (option "
            if int(row['P1_risk_score'])==int(row['P2_risk_score']):
                answer="They carry the same risk level"
            elif int(row['P1_risk_score'])<int(row['P2_risk_score']):
                answer=row['P1_name']
            else:
                answer=row['P2_name']
        if pick_order==1:
            question="Who is LESS compliant with information security policies? Your answer must begin with (option "
            if int(row['P1_risk_score'])==int(row['P2_risk_score']):
                answer="They carry the same risk level"
            elif int(row['P1_risk_score'])>int(row['P2_risk_score']):
                answer=row['P1_name']
            else:
                answer=row['P2_name']
        
        item1 = row['P1_name']
        item2 = row['P2_name']
        item3 = "They carry the same risk level"
        item4 = "It is impossible to tell"
        choices_list = [item1,item2,item3,item4]
        random.shuffle(choices_list)
        # start producing multiple choices
        for choice in choices_list:
            key=keys.pop(0)
            question+=os.linesep
            question+= "(option "+key+") - "+str(choice)
            if choice==answer:
                answer="(option "+key+") - "+str(choice)

        QA_WHO_df.loc[len(QA_WHO_df.index)]=[ID,question,answer]
        counter+=1
        if counter%50==0:
            print(".", end =" ")
    return QA_WHO_df

def ollagen1_TeamRisk(core_df):
    """
    Generate questions about Team Risk with reference answers.
    
    Parameters:
    core_df: OllaGen1 core data
    
    Returns:
    QA_TeamRisk_df : a dataframe of generated content based on the provided params
    """
    print("---- generating Team Risk entries ")
    # declare key variables
    question=""
    answer=""
    QA_TeamRisk_df = pd.DataFrame(columns=['ID','TeamRisk_Question','TeamRisk_Answer'])
    counter=0

    # Iterating over rows of core dataframe
    # Note the columns are:
    # "ID","P1_name","P1_cogpath","P1_profile","P1_risk_score","P1_risk_profile",
    # "P2_name","P2_cogpath","P2_profile","P2_risk_score","P2_risk_profile", 
    # combined_risk_score,shared_risk_factor,targetted_factor

    for index, row in core_df.iterrows():
        #print(index, row['ID'], row['P1_name'])
        # declare more function-level variables
        keys=['a','b','c','d','e']
        # now start to generate the main content
        ID=row['ID']
        sum_risk=int(row['P1_risk_score'])+int(row['P2_risk_score'])
        question="Will information security non-compliance risk level increase if these employees work closely in the same team? Your answer must begin with (option "
        if row['combined_risk_score']>sum_risk:
            answer="security non-compliance risk level will increase"
        elif row['combined_risk_score']==sum_risk:
            answer="security non-compliance risk level may increase"
        elif sum_risk==0:
            answer="security non-compliance risk level will stay the same"
        
        item1 = "security non-compliance risk level will increase"
        item2 = "security non-compliance risk level may increase"
        item3 = "security non-compliance risk level will stay the same"
        item4 = "It is impossible to tell"
        choices_list = [item1,item2,item3,item4]
        random.shuffle(choices_list)
        # start producing multiple choices
        for choice in choices_list:
            key=keys.pop(0)
            question+=os.linesep
            question+= "(option "+key+") - "+str(choice)
            if choice==answer:
                answer="(option "+key+") - "+str(choice)

        QA_TeamRisk_df.loc[len(QA_TeamRisk_df.index)]=[ID,question,answer]
        counter+=1
        if counter%50==0:
            print(".", end =" ")
    return QA_TeamRisk_df

def ollagen1_TargetFactor(core_df):
    """
    Generate questions about The Target Factor with reference answers.
    
    Parameters:
    core_df: OllaGen1 core data
    
    Returns:
    QA_TargetFactor_df : a dataframe of generated content based on the provided params
    """
    print("---- generating TargetFactor entries ")
    # declare key variables
    question=""
    answer=""
    QA_TargetFactor_df = pd.DataFrame(columns=['ID','TargetFactor_Question','TargetFactor_Answer'])
    counter=0

    # Iterating over rows of core dataframe
    # Note the columns are:
    # "ID","P1_name","P1_cogpath","P1_profile","P1_risk_score","P1_risk_profile",
    # "P2_name","P2_cogpath","P2_profile","P2_risk_score","P2_risk_profile", 
    # combined_risk_score,shared_risk_factor,targetted_factor

    for index, row in core_df.iterrows():
        #print(index, row['ID'], row['P1_name'])
        # declare more function-level variables
        keys=['a','b','c','d']
        # now start to generate the main content
        ID=row['ID']
        question="To increase information security compliance, which cognitive behavioral factor should be targetted for strengthening? Your answer must begin with (option "
        try:
            targetedFactor=string_2_list(str(row['targetted_factor']))
            answer = targetedFactor.pop(0)
            combined_factor=list(set(string_2_list(row['P1_cogpath'])+string_2_list(row['P2_cogpath']))) 
            while answer in combined_factor:
                combined_factor.remove(answer)
            random.shuffle(combined_factor)
        except Exception as e:
            print(f"An error occurred: {ID} {str(e)}")
        
        item1 = answer
        item2 = combined_factor.pop(0)
        item3 = combined_factor.pop(0)
        item4 = combined_factor.pop(0)
        choices_list = [item1,item2,item3,item4]
        random.shuffle(choices_list)
        # start producing multiple choices
        for choice in choices_list:
            key=keys.pop(0)
            question+=os.linesep
            question+= "(option "+key+") - "+str(choice)
            if choice==answer:
                answer="(option "+key+") - "+str(choice)

        QA_TargetFactor_df.loc[len(QA_TargetFactor_df.index)]=[ID,question,answer]
        counter+=1
        if counter%50==0:
            print(".", end =" ")
    return QA_TargetFactor_df

def function_template ():
    """
    Function description.
    
    Parameters:
    param : param description
    
    Returns:
    value : value description
    """
    try:
        # function code here
        print()
    except Exception as e:
        return f"An error occurred: {str(e)}"


# In[ ]:


## MAIN
a_dict = csv_2_nlevel_dict (dict_path)
knowledge_graph = graph_load (node_path, edge_path)

# Generating core QA data
QA_core_df = ollagen1_core(knowledge_graph,a_dict,QA_questions,QA_coglength)
QA_core_df.to_csv(QA_core_outpath, index=False, quoting=2, escapechar="\\")

# Generating WhichCogPath QA entries
QA_WCP_df = ollagen1_WhichCogPath(QA_core_df,knowledge_graph)
# Generating Who is More/Less Compliant QA entries
QA_WHO_df = ollagen1_WHO(QA_core_df)
# Generating Team Risk QA entries
QA_TeamRisk_df = ollagen1_TeamRisk(QA_core_df)
# Generating Target Factor QA entries
QA_core_reread_df = pd.read_csv(QA_core_outpath)
QA_TargetFactor_df = ollagen1_TargetFactor(QA_core_reread_df)

df_list = [QA_core_df,QA_WCP_df,QA_WHO_df,QA_TeamRisk_df,QA_TargetFactor_df]
QA_full_df = reduce(lambda  left,right: pd.merge(left,right,on=['ID'], how='inner'), df_list)
QA_full_df.to_csv(QA_full_outpath, index=False, quoting=2, escapechar="\\")

