#!/usr/bin/env python3
"""
Enhanced OllaBench1 with OpenAI and Anthropic Support - Targeted Model Version

This is a modified version of OllaBench1.py that supports:
- Ollama (original)
- OpenAI API
- Anthropic Claude API
- Targeted model evaluation via CLI

Usage:
    python OllaBench1_enhanced_targeted.py [--params PARAMS_FILE] [--model MODEL_NAME]
    
Parameter Files:
- Contains API keys and framework configuration
- Default: params.json
- Can specify custom parameter file with --params argument

Model Targeting:
- Use --model to evaluate only a specific model
- Overrides the model list in parameter file
- Useful for testing individual models

API Keys can be provided via:
1. Parameter file (recommended for parallel execution)
2. Environment variables (fallback)
"""

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
import sys
import argparse

import nltk
from nltk.tokenize import sent_tokenize

# Download NLTK data if needed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Also download punkt_tab for newer NLTK versions
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    print("Downloading punkt_tab for sentence tokenization...")
    nltk.download('punkt_tab')

# Parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Enhanced OllaBench1 with OpenAI and Anthropic Support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python OllaBench1_enhanced_targeted.py
    python OllaBench1_enhanced_targeted.py --params params_openai.json
    python OllaBench1_enhanced_targeted.py --params params_anthropic.json
    python OllaBench1_enhanced_targeted.py --params params_openai.json --model gpt-5
    python OllaBench1_enhanced_targeted.py --params params_anthropic.json --model claude-opus-4-1-20250805
    python OllaBench1_enhanced_targeted.py --params params_openai.json --model o1 --max-rows 100
        """
    )
    parser.add_argument(
        '--params', 
        default='params.json',
        help='Path to parameter file (default: params.json)'
    )
    parser.add_argument(
        '--output-dir',
        default=None,
        help='Output directory for chunk result files (overrides parameter file setting)'
    )
    parser.add_argument(
        '--max-rows',
        type=int,
        default=None,
        help='Maximum number of rows to read from dataset (overrides parameter file setting)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='Target specific model for evaluation (overrides parameter file model list)'
    )
    return parser.parse_args()

# Read parameters
args = parse_arguments()
params_path = args.params

try:
    with open(params_path, 'r') as file:
        params = json.load(file)   
    print(f"Loaded parameters from: {params_path}")
except FileNotFoundError:
    print(f"The file {params_path} was not found.")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error decoding JSON from the file {params_path}.")
    sys.exit(1)

# Initialize variables
llm_framework = params["llm_framework"]
llm_endpoints = params.get("llm_endpoints", "http://localhost:11434/")
llm_models = params["llm_models"]
llm_leaderboard = params["llm_leaderboard"]
tries = params["bench_tries"]
QA_inpath = params["QA_inpath"]

# Determine output directory (command-line overrides parameter file)
output_dir = args.output_dir or params.get("output_directory", ".")
if output_dir != ".":
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")

# Determine max rows (command-line overrides parameter file)
max_rows = args.max_rows or params.get("max_rows", None)
if max_rows:
    print(f"Dataset row limit: {max_rows}")

# Handle targeted model (command-line overrides parameter file)
if args.model:
    llm_models = [args.model]
    print(f"Targeting specific model: {args.model}")

print(f"Configured framework: {llm_framework}")
print(f"Target models: {llm_models}")

# Initialize clients based on framework
client = None

if llm_framework == "ollama":
    import ollama
    from ollama import Client
    client = Client(host=llm_endpoints)
    
    # Get available models
    try:
        llm_list = [d[next(iter(d))] for d in ollama.list()['models']]
        if llm_models == "all":
            llm_models = llm_list
        else:
            llm_names_bak = llm_models.copy()
            llm_models[:] = [item for item in llm_models if item in llm_list]
            missing_models = [item for item in llm_names_bak if item not in llm_models]
            if missing_models:
                print(f"The following model(s) do not exist in Ollama: {missing_models}")
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        sys.exit(1)

elif llm_framework == "openai":
    from openai import OpenAI
    # Try to get API key from params file first, then environment variable
    api_key = params.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OpenAI API key not found")
        print("Please provide it in the parameter file with 'openai_api_key' field")
        print("Or set OPENAI_API_KEY environment variable")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    print(f"OpenAI client initialized with key: ...{api_key[-10:]}")
    
    # For OpenAI, we use the model names as provided in the config
    # Common models: gpt-4, gpt-4-turbo-preview, gpt-3.5-turbo, o1-preview, o1-mini
    if llm_models == "all":
        llm_models = ["gpt-3.5-turbo", "gpt-4", "o1-preview", "o1-mini"]  # Default models
        
elif llm_framework == "anthropic":
    import anthropic
    # Try to get API key from params file first, then environment variable
    api_key = params.get("anthropic_api_key") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Anthropic API key not found")
        print("Please provide it in the parameter file with 'anthropic_api_key' field")
        print("Or set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)
        
    client = anthropic.Anthropic(api_key=api_key)
    print(f"Anthropic client initialized with key: ...{api_key[-10:]}")
    
    # For Anthropic, use Claude model names
    if llm_models == "all":
        llm_models = ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229"]  # Default models

else:
    print(f"Unsupported framework: {llm_framework}")
    print("Supported frameworks: ollama, openai, anthropic")
    sys.exit(1)

# Functions
def write_df_to_csv(df, csv_file):
    """Write DataFrame to CSV file"""
    mode = 'a' if os.path.exists(csv_file) else 'w'
    df.to_csv(csv_file, mode=mode, index=False)

def get_response(llm_framework, a_model, a_prompt):
    """
    Get response from different LLM frameworks
    Returns normalized response format similar to Ollama
    """
    if llm_framework == "ollama":
        result = ollama.generate(model=a_model, prompt=a_prompt, stream=False)
        while "eval_duration" not in result:
            time.sleep(1)
        return result
    
    elif llm_framework == "openai":
        begin_epoch = int(time.time())
        try:
            # Configure parameters based on model type
            if a_model.startswith(("o1", "o3", "o4")):
                # Reasoning models (o1, o3, o4 series) - use max_completion_tokens, no system message, no temperature
                response = client.chat.completions.create(
                    model=a_model,
                    messages=[
                        {"role": "user", "content": a_prompt}
                    ],
                    max_completion_tokens=4096,  # Higher limit for reasoning models (reasoning + response tokens)
                    timeout=60  # 60 second timeout for reasoning models
                )
            elif a_model.startswith("gpt-5"):
                # GPT-5 series - use max_completion_tokens, no custom temperature (only default 1.0 supported)
                response = client.chat.completions.create(
                    model=a_model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant who follows instructions."},
                        {"role": "user", "content": a_prompt}
                    ],
                    max_completion_tokens=4096,  # Higher limit for GPT-5 models (may also use reasoning tokens)
                    timeout=30  # 30 second timeout for GPT-5 models
                    # Note: GPT-5 only supports default temperature (1.0)
                )
            else:
                # Older models (gpt-4, gpt-3.5-turbo) - use max_tokens
                response = client.chat.completions.create(
                    model=a_model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant who follows instructions."},
                        {"role": "user", "content": a_prompt}
                    ],
                    temperature=0,  # Deterministic responses for evaluation
                    max_tokens=4096,
                    timeout=30  # 30 second timeout for older models
                )
            end_epoch = int(time.time())
            
            # Normalize to Ollama format
            # Handle reasoning models that may have reasoning_tokens in usage
            completion_tokens = response.usage.completion_tokens
            if hasattr(response.usage, 'completion_tokens_details') and response.usage.completion_tokens_details:
                # For reasoning models, include reasoning tokens if available
                reasoning_tokens = getattr(response.usage.completion_tokens_details, 'reasoning_tokens', 0)
                completion_tokens += reasoning_tokens
            
            # Get response content, handle potential None values and content filtering
            response_choice = response.choices[0]
            response_content = response_choice.message.content
            
            # Check for content filtering, refusals, or empty responses
            if response_content is None or response_content.strip() == "":
                if hasattr(response_choice.message, 'refusal') and response_choice.message.refusal:
                    response_content = f"[Content refused: {response_choice.message.refusal}]"
                elif response_choice.finish_reason == "content_filter":
                    response_content = "[Content filtered by OpenAI policy]"
                elif response_choice.finish_reason == "length":
                    response_content = "[Response truncated due to length limit]"
                elif response_content is None:
                    response_content = "[No response content]"
                else:
                    response_content = "[Empty response from API]"
            
            result = {
                'response': response_content,
                'eval_count': completion_tokens,
                'total_duration': int((end_epoch - begin_epoch) * 1000000000),  # Convert to nanoseconds
                'eval_duration': int((end_epoch - begin_epoch) * 1000000000)
            }
            return result
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise
    
    elif llm_framework == "anthropic":
        begin_epoch = int(time.time())
        try:
            response = client.messages.create(
                model=a_model,
                max_tokens=4096,  # Standardized token limit for comprehensive responses
                temperature=0,  # Deterministic responses for evaluation
                system="You are a helpful assistant who follows instructions.",
                messages=[
                    {"role": "user", "content": a_prompt}
                ]
            )
            end_epoch = int(time.time())
            
            # Normalize to Ollama format
            result = {
                'response': response.content[0].text,
                'eval_count': response.usage.output_tokens,
                'total_duration': int((end_epoch - begin_epoch) * 1000000000),  # Convert to nanoseconds
                'eval_duration': int((end_epoch - begin_epoch) * 1000000000)
            }
            return result
        except Exception as e:
            print(f"Anthropic API error: {e}")
            raise
    
    else:
        raise ValueError(f"Unsupported framework: {llm_framework}")

def test_model(tries, a_model):
    """Test if a model is accessible and working"""
    print(f"Testing model: {a_model}")
    if "demo" in a_model:
        return True
    
    while tries > 0:
        try:
            response = get_response(llm_framework, a_model, 'just say yes')
            if response and 'response' in response:
                print(f"✓ Model {a_model} is working")
                return True
        except Exception as e:
            print(f"✗ Test failed for {a_model}: {e}")
            tries -= 1
            if tries > 0:
                print(f"Retrying... ({tries} attempts remaining)")
                time.sleep(2)
    
    print(f"✗ Model {a_model} failed all tests")
    return False

def check_answer(reference, answer):
    """
    Check if the correct answer (reference) is within the first two sentences of a model's answer.
    """
    norm_ref1 = str(reference).lower()
    norm_ref2 = norm_ref1.split(" - ")[0]
    try:
        norm_ref3 = norm_ref1.split(" - ")[1]
    except IndexError:
        norm_ref3 = ""
    norm_ref4 = norm_ref2.replace("option ", "")
    ans_keys = (norm_ref1, norm_ref2, norm_ref3, norm_ref4)
    norm_answer = str(answer).lower()

    # Tokenize answer into sentences
    sentences = sent_tokenize(norm_answer)
    
    # Combine the first two sentences
    first_two_sentences = ' '.join(sentences[:2])

    # Check if any answer key is in the first two sentences
    return any(ans_key in first_two_sentences for ans_key in ans_keys if ans_key)

def grade_model(a_model, input_df):
    """Grade an LLM model's responses"""
    results = []
    print(f"Grading {a_model} on {len(input_df)} questions...")
    
    # Test model first
    if not test_model(tries, a_model):
        print(f"Skipping {a_model} due to test failure")
        return pd.DataFrame()
    
    turn = 0
    for index, row in input_df.iterrows():
        try:
            score = 0
            context = f"""
                Here are the intelligence about {row["P1_name"]} with comments from trusted experts and/or {row["P1_name"]}'s recorded statement(s).
                {row["P1_profile"]}
                Here are the intelligence about {row["P2_name"]} with comments from trusted experts and/or {row["P2_name"]}'s recorded statement(s).
                {row["P2_profile"]}
                """

            # Initialize question responses
            questions = {
                'WCP': {'Question': row["WCP_Question"], 'Answer': row["WCP_Answer"], 'score': 0, 'response': None, 'duration': 0, 'eval_count': 0},
                'WHO': {'Question': row["WHO_Question"], 'Answer': row["WHO_Answer"], 'score': 0, 'response': None, 'duration': 0, 'eval_count': 0},
                'TeamRisk': {'Question': row["TeamRisk_Question"], 'Answer': row["TeamRisk_Answer"], 'score': 0, 'response': None, 'duration': 0, 'eval_count': 0},
                'TargetFactor': {'Question': row["TargetFactor_Question"], 'Answer': row["TargetFactor_Answer"], 'score': 0, 'response': None, 'duration': 0, 'eval_count': 0}
            }

            # Process each question type
            for q_type in questions:
                q_data = questions[q_type]
                full_prompt = str(context + q_data['Question'])
                
                try:
                    response = get_response(llm_framework, a_model, full_prompt)
                    
                    if response and 'response' in response:
                        # Additional debugging for empty responses
                        response_text = response['response']
                        if response_text is None or response_text == "":
                            print(f"Warning: Empty response for {q_type} question in case {row['ID']}")
                            response_text = "[Empty response from API]"
                        
                        q_data['response'] = response_text
                        q_data['duration'] = response.get('total_duration', 0)
                        q_data['eval_count'] = response.get('eval_count', 0)
                        
                        # Check answer only if we have a valid response
                        if response_text and response_text not in ["[No response content]", "[Empty response from API]"]:
                            if check_answer(q_data['Answer'], response_text):
                                q_data['score'] = 1
                                score += 1
                    else:
                        print(f"Warning: Invalid response structure for {q_type} question in case {row['ID']}")
                        q_data['response'] = "[Invalid response structure]"
                    
                    # Small delay to respect API rate limits
                    if llm_framework in ["openai", "anthropic"]:
                        time.sleep(0.1)
                        
                except Exception as e:
                    print(f"Error processing question {q_type} for case {row['ID']}: {e}")
                    q_data['response'] = f"ERROR: {str(e)}"

            # Compile results
            results.append([
                row['ID'], a_model, str(context),
                questions['WCP']['Question'], questions['WCP']['Answer'],
                questions['WCP']['duration'], questions['WCP']['eval_count'], 
                str(questions['WCP']['response']), questions['WCP']['score'],
                questions['WHO']['Question'], questions['WHO']['Answer'],
                questions['WHO']['duration'], questions['WHO']['eval_count'], 
                str(questions['WHO']['response']), questions['WHO']['score'],
                questions['TeamRisk']['Question'], questions['TeamRisk']['Answer'],
                questions['TeamRisk']['duration'], questions['TeamRisk']['eval_count'], 
                str(questions['TeamRisk']['response']), questions['TeamRisk']['score'],
                questions['TargetFactor']['Question'], questions['TargetFactor']['Answer'],
                questions['TargetFactor']['duration'], questions['TargetFactor']['eval_count'], 
                str(questions['TargetFactor']['response']), questions['TargetFactor']['score'],
                score
            ])
            
            turn += 1
            if turn % 50 == 0:
                print(f"Processed {turn}/{len(input_df)} questions")

        except Exception as e:
            print(f"Error processing row {index}: {e}")

    # Create results DataFrame
    columns = [
        'ID', 'Model', 'Context', 
        'WCP_Question', 'WCP_Correct_Answer', 'WCP_TotalDuration', 'WCP_EvalCounts', 'WCP_Response', 'WCP_score',
        'WHO_Question', 'WHO_Correct_Answer', 'WHO_TotalDuration', 'WHO_EvalCounts', 'WHO_Response', 'WHO_score',
        'TeamRisk_Question', 'TeamRisk_Correct_Answer', 'TeamRisk_TotalDuration', 'TeamRisk_EvalCounts', 'TeamRisk_Response', 'TeamRisk_score',
        'TargetFactor_Question', 'TargetFactor_Correct_Answer', 'TargetFactor_TotalDuration', 'TargetFactor_EvalCounts', 'TargetFactor_Response', 'TargetFactor_score',
        'Total score'
    ]
    
    results_df = pd.DataFrame(results, columns=columns)
    print(f"Completed grading {a_model}: {len(results_df)} results")
    return results_df

def df_2_chunks(a_df, chunk_size):
    """Split DataFrame into chunks"""
    try:
        num_chunks = len(a_df) // chunk_size + (1 if len(a_df) % chunk_size else 0)
        chunks = []
        for i in range(num_chunks):
            start_row = i * chunk_size
            end_row = start_row + chunk_size
            chunk = a_df[start_row:end_row]
            chunks.append(chunk)
        return chunks
    except Exception as e:
        print(f"Error creating chunks: {e}")
        return [a_df]  # Return original DataFrame as single chunk

# Main execution
def main():
    print(f"\\n=== OllaBench1 Enhanced - {llm_framework.upper()} Mode ===")
    print(f"Framework: {llm_framework}")
    print(f"Models to evaluate: {llm_models}")
    print(f"Dataset: {QA_inpath}")
    
    # Load QA dataset
    try:
        if max_rows:
            QA_df = pd.read_csv(QA_inpath, header=0, nrows=max_rows)
            print(f"Loaded dataset with {len(QA_df)} questions (limited to {max_rows} rows)")
        else:
            QA_df = pd.read_csv(QA_inpath, header=0)
            print(f"Loaded dataset with {len(QA_df)} questions")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)
    
    # Split to chunks
    chunk_size = 500
    QA_df_chunks = df_2_chunks(QA_df, chunk_size)
    print(f"Split into {len(QA_df_chunks)} chunks of size {chunk_size}")
    
    # Process each model
    for a_model in llm_models:
        print(f"\\n{'='*50}")
        print(f"Processing model: {a_model}")
        print(f"{'='*50}")
        
        model_start_time = time.time()
        
        # Process each chunk
        for chunk_index, QA_df_chunk in enumerate(QA_df_chunks):
            print(f"\\nProcessing chunk {chunk_index + 1}/{len(QA_df_chunks)}")
            
            # Generate output filename
            safe_model_name = a_model.replace(":", "-").replace("/", "-")
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            filename = f"{safe_model_name}_chunk{chunk_index}_{timestamp}_QA_Results.csv"
            QA_outpath = os.path.join(output_dir, filename)
            
            # Grade the chunk
            try:
                QA_result_df = grade_model(a_model, QA_df_chunk)
                
                if len(QA_result_df) > 0:
                    write_df_to_csv(QA_result_df, QA_outpath)
                    avg_score = QA_result_df['Total score'].mean()
                    print(f"✓ Chunk {chunk_index} completed. Average score: {avg_score:.2f}")
                    print(f"Results saved to: {QA_outpath}")
                else:
                    print(f"✗ No results generated for chunk {chunk_index}")
                    
            except Exception as e:
                print(f"✗ Error processing chunk {chunk_index}: {e}")
        
        model_end_time = time.time()
        model_duration = model_end_time - model_start_time
        print(f"\\nModel {a_model} completed in {model_duration/60:.1f} minutes")
    
    print(f"\\n{'='*60}")
    print("🎉 Evaluation campaign completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()