#!/usr/bin/env python
# coding: utf-8

# In[28]:


import os
import datetime
import time
import csv
import pandas as pd
import shutil

llm_framework="ollama"

from ollama import Client
llm_endpoints = os.environ.get("OLLAMA_ENDPOINT") # specify endpoint url:port here if you don't have OLLAMA_ENDPOINT set
ollama_client = Client(host=llm_endpoints)
    
from openai import OpenAI
openai_client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

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


# In[26]:


def get_response(a_model,a_prompt):
    result = ollama.generate(model=a_model, prompt= a_prompt, stream=False)
    while "eval_duration" not in result:
        time.sleep(1)
    return result

def get_openai_response(a_prompt, multiplier):
    responses = []
    model = "gpt-4o"
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


# In[153]:


def combine_and_remove_duplicates(input_folder, output_file):
    # List all CSV files in the input folder
    csv_files = [file for file in os.listdir(input_folder) if file.endswith('.csv')]
    
    # Read all CSV files into separate DataFrames
    dfs = [pd.read_csv(os.path.join(input_folder, file)) for file in csv_files]
    
    # Concatenate all DataFrames
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Remove duplicates from the combined DataFrame
    combined_df.drop_duplicates(inplace=True)
    
    # Write the combined DataFrame to a new CSV file
    combined_df.to_csv(output_file, index=False)
    print(f"Combined CSV with duplicates removed saved to '{output_file}'")

def remove_non_charmap_characters(s):
    """Remove characters from the string s that cannot be encoded using the charmap codec."""
    return s.encode('charmap', 'ignore').decode('charmap')

def remove_items_without_period(input_file, output_file):
    with open(input_file, 'r', newline='') as infile:
        with open(output_file, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            for row in reader:
                # Check if the last item in the row ends with a period
                if row[-1].strip().endswith('.'):
                    writer.writerow(row)


# In[5]:


# Import prompt seeds
promptseed_df = pd.read_csv('Cybonto-Gen1-PromptSeeds.csv')


# In[ ]:


rate_per_minute = 500 #number of request per minute, must be divisible by 2
# rate per minute is first dependent on your text generation endpoint constraint
# rate per minute should be much smaller than batch size and be divisible by batch size
batch_size = 3000 #number of one-sentence example for each construct-flag pair
batch_num = int(batch_size/rate_per_minute)

for flag in flag_list:
    for construct in construct_list:
        responses = []
        # Filter the DataFrame based on the current construct and flag
        filtered_rows = promptseed_df[(promptseed_df['Constructs'] == construct) & (promptseed_df['Flag'] == flag)]
        
        # Extract the 'Prompt' column values and extend the extracted_prompts list
        extracted_prompts = filtered_rows['Prompt'].tolist()
        for prompt in extracted_prompts:
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

