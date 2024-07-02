import os
import time
import random
import re
import hashlib
import json
from datetime import datetime
import csv
import streamlit as st
import ollama
from ollama import Client
import openai
from openai import OpenAI
import anthropic
from anthropic import Anthropic
import google.generativeai as google
from OllaBench_gui_menu import menu_with_redirect, show_header

st.set_page_config(
    page_title="Health Check",
    initial_sidebar_state="expanded"
)

if "ollama_endpoints" not in st.session_state:
    st.session_state.ollama_endpoints = "None"
if "evaluator_llm_list" not in st.session_state:
    st.session_state.evaluator_llm_list = "None"
if "evaluatee_llm_list" not in st.session_state:
    st.session_state.evaluatee_llm_list = "None"
if "use_default_dataset" not in st.session_state:
    st.session_state.use_default_dataset = "Yes"
if "evaluator_framework" not in st.session_state:
    st.session_state.evaluator_framework = "None"
if "evaluatee_framework" not in st.session_state:
    st.session_state.evaluatee_framework = "None"
if "openai_token" not in st.session_state:
    st.session_state.openai_token = "None"
if "anthropic_token" not in st.session_state:
    st.session_state.anthropic_token = "None"
if "google_token" not in st.session_state:
    st.session_state.google_token = "None"

# Functions

def read_data_from_csv(csv_file_path):
    """Read data from a CSV file with headers."""
    data = []
    try:
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)  # Each row is a dictionary
    except FileNotFoundError:
        st.write(f"The file {csv_file_path} was not found.")
    except Exception as e:
        st.write(f"An error occurred: {e}")
    return data

def file_hash_sha256(file_path):
    """Compute SHA-256 hash of the specified file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return f"Error: {e}"

def load_previous_results(json_file_path):
    """Load previous hash results from a JSON file."""
    try:
        with open(json_file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # Return an empty list if no previous file exists
    except Exception as e:
        return f"Error loading previous results: {e}"

def check_files_integrity(data, json_file_path='file_hashes.json'):
    """Check the integrity of multiple files using data from CSV, record with file path, category, admin reviewed, date-time, and hash, and update JSON."""
    current_results = load_previous_results(json_file_path)
    new_results = []

    for entry in data:
        file_path = entry['file path']
        category = entry['category']
        admin_reviewed = entry['admin reviewed']
        current_hash = file_hash_sha256(file_path)
        if not current_results or not any(result['hash'] == current_hash and result['file_path'] == file_path for result in current_results):
        # check if current hash is in all previous hash of the same file, will improve this criteria in later version
            hash_info = {
                "file_path": file_path,
                "category": category,
                "admin_reviewed": admin_reviewed,
                "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "hash": current_hash
            }
            new_results.append(hash_info)

    # If no previous results, save new results; otherwise update only if there are new or changed files
    if not current_results or new_results:
        current_results = new_results if not current_results else current_results + new_results
        with open(json_file_path, 'w') as json_file:
            json.dump(current_results, json_file, indent=4)

    return new_results

def load_and_filter_results(json_file_path, reviewed_status='0'):
    """Load results from a JSON file and filter based on 'admin reviewed' status."""
    filtered_results = []
    try:
        with open(json_file_path, 'r') as file:
            results = json.load(file)
            # Filter results where 'admin reviewed' equals the specified reviewed_status
            filtered_results = [result for result in results if result.get('admin_reviewed') == reviewed_status]
    except FileNotFoundError:
        st.write(f"The file {json_file_path} was not found.")
    except json.JSONDecodeError:
        st.write("Error decoding JSON from the file.")
    except Exception as e:
        st.write(f"An error occurred: {e}")
    return filtered_results

def is_valid_url(url: str) -> bool:
    # Regular expression to validate URL
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https:// or ftp:// or ftps://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return re.match(regex, url) is not None

def get_ollama_response(llm_framework,a_model,a_prompt):
    if llm_framework =="ollama":
        result = ollama.generate(model=a_model, prompt= a_prompt, stream=False)
        while "eval_duration" not in result:
            time.sleep(1)
    return result

def test_ollama_model(tries,a_model):
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
                response = get_ollama_response("ollama",a_model,'just say yes')
                return True
            except Exception as e:
                tries-=1
                response = str(e) #"error" wil be in response
        if "error" in response:
            print(f"The model {a_model} is bad.")
    return False 

def set_llm_endpoint (framework) -> list:
    container = st.empty()
    container.empty()
    llm_list="None"
    random_integer = random.randint(1, 100)
    with container.container():
        if framework == "ollama":
            if st.session_state.ollama_endpoints in ["None","http://<url>:<port number>"]:
                st.session_state.ollama_endpoints = st.text_input(
                    "Ollama endpoint:",
                    "http://<url>:<port number>",
                )

            if is_valid_url(st.session_state.ollama_endpoints) or (st.session_state.ollama_endpoints == "demo") :
                #client = Client(host=st.session_state.ollama_endpoints)
                # Get model list for evaluation
                if st.session_state.ollama_endpoints == "demo":
                    llm_list = ["Arctic demo", "demo:7b-q4_0", "demo:7b-q8_0"]
                else:
                    try:
                        llm_list = [d[next(iter(d))] for d in ollama.list()['models']] #get model names from the list of dict returned by Ollama
                    except:
                        st.error('Cannot connect to the Ollama endpoint. Try another one?', icon="🚨")
        elif framework == "openai":
            if st.session_state.openai_token == "None":
                st.session_state.openai_token = st.text_input(
                    "OpenAI Project Key:",
                    value="None", type="password"
                )
            if st.session_state.openai_token != "None":
                client = OpenAI(api_key=st.session_state.openai_token)
                try:
                    models = client.models.list()
                    llm_list = [model.id for model in models.data]
                except:
                    st.error('Cannot get model list from OpenAI', icon="🚨")
        elif framework == "anthropic":
            if st.session_state.anthropic_token == "None":
                st.session_state.anthropic_token = st.text_input(
                    "Anthropic API Key:",
                    value="None", type="password"
                )
            if st.session_state.anthropic_token != "None":
                try:
                    anthropic_client = anthropic.Anthropic(api_key=st.session_state.anthropic_token)
                    message = anthropic_client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=1000,
                        temperature=0.3,
                        system="Respond only in Yoda-speak.",
                        messages=[
                            {"role": "user", "content": "How are you today?"}
                        ]
                    )
                    llm_list = ["claude-3-opus-20240229","claude-3-sonnet-20240229","claude-3-haiku-20240307"]
                except:
                    st.error('Cannot communicate with Anthropic', icon="🚨")
        elif framework == "google":
            model_names = []
            if st.session_state.google_token == "None":
                st.session_state.google_token = st.text_input(
                    "Google Project Key:",
                    value="None", type="password"
                )
            if st.session_state.google_token != "None":
                google.configure(api_key=st.session_state.google_token)
                try:
                    for m in google.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            model=m.name
                            model = model.split("/")[1]
                            model_names.append(model)
                except:
                    st.error('Cannot get model list from Google', icon="🚨")
                llm_list = model_names
    
    return llm_list

def check_llm_model (a_list) -> bool:
    for model in a_list:
        if "demo" in model or model in ("openai","anthropic","google"):
            check_passed=True
        else:
            check_passed = test_ollama_model(3,model)
        if not check_passed:
            return False
    return True

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)
            st.write('Demo username is "user" and password is "userpassword"')

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state.username in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state.password,
            st.secrets.passwords[st.session_state.username],
        ):
            st.session_state.password_correct = True
            # get authenticated user role to session state
            if st.session_state.username in st.secrets["roles"]:
                st.session_state.role = st.secrets.roles[st.session_state.username]
            del st.session_state.password  # Don't store the username or password.
            #del st.session_state["username"]
        else:
            st.session_state.password_correct = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state and st.session_state.password_correct == False:
        st.error("😕 Unknown user or incorrect password")
    return False

# Main Streamlit app starts here
show_header()
if not check_password():
    st.stop()
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
    st.title("System Health Checking")
    st.markdown(f"You are currently logged with the role of {st.session_state.role}.")
    csv_file_path = "admin/file_list.csv"
    check_results_path = "admin/health_checks.csv"
    data = read_data_from_csv(csv_file_path)
    results = check_files_integrity(data, check_results_path)
    nonreviewed_changes=load_and_filter_results(check_results_path, reviewed_status='0')
    if len(results)==0 and len(nonreviewed_changes)==0: # if there is no unexpected change in files
        st.success('System files retain integrity', icon="✅")

        # Check EVALUATOR
        st.session_state.use_default_dataset = st.radio(
            "Do you want to use default benchmark dataset instead of creating a new one?",
            ["Yes. To save time.","No. I want my own benchmark dataset."],
        )
        evaluator_llm_list = "None"
        if st.session_state.use_default_dataset == "No. I want my own benchmark dataset.":
            st.session_state.evaluator_framework = st.radio(
                "Please select an **evaluator** framework.",
                ["ollama","openai","anthropic","google"],
                index=None
            )
            if st.session_state.evaluator_framework in ["ollama","openai","anthropic","google"]:
                evaluator_llm_list = set_llm_endpoint (st.session_state.evaluator_framework)
        if evaluator_llm_list != "None":
            st.session_state.evaluator_llm_list = evaluator_llm_list
            with st.expander("Evaluator endpoint is healthy with access to the following models (click to expand)"):
                for model_name in st.session_state.evaluator_llm_list:
                    st.markdown(f"- {model_name}")
        else:
            st.session_state.healthcheck_passed = False
        
        # Check EVALUATEE
        evaluatee_llm_list = "None"
        st.session_state.evaluatee_framework = st.radio(
            "Please select an **evaluatee** framework.",
            ["ollama","openai","anthropic","google"],
            index=None
        )
        if evaluator_llm_list != "None" or "Yes" in st.session_state.use_default_dataset:
            if st.session_state.evaluatee_framework in ["ollama","openai","anthropic","google"]:
                evaluatee_llm_list = set_llm_endpoint (st.session_state.evaluatee_framework)
        if evaluatee_llm_list != "None":
            st.session_state.evaluatee_llm_list = evaluatee_llm_list
            with st.expander("Evaluatee endpoint is healthy with access to the following models (click to expand)"):
                for model_name in st.session_state.evaluatee_llm_list:
                    st.markdown(f"- {model_name}")
            st.session_state.healthcheck_passed = True
        else:
            st.session_state.healthcheck_passed = False
        
        if st.session_state.healthcheck_passed:
            st.success('All endpoints are healthy', icon="✅")
            next=False
            next = st.button("Generate Benchmark Dataset")
            if next:
                st.switch_page("pages/OllaBench_gui_generate_dataset.py")
    else:
        st.error(f'Systems are not healthy.', icon="🚨")
        if st.session_state.role == "admin":
            st.write("Detected new changes:")
            st.write(results)
            st.write("Detected non-reviewed changes:")
            st.write(nonreviewed_changes)
    
