import time
import re
import streamlit as st
import ollama
from ollama import Client
from OllaBench_gui_menu import menu_with_redirect, show_header

if "llm_endpoints" not in st.session_state:
    st.session_state.llm_endpoints = " "
if "selected_llm" not in st.session_state:
    st.session_state.selected_llm = "None"
if "app_state" not in st.session_state:
    st.session_state.apt_state = "load llm"

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

def display_progress(n):
    # Calculate the number of squares
    num_squares = (n + 49) // 50

    # Initialize progress list with False (grey) indicating incomplete
    progress = [False] * num_squares

    # Streamlit application
    st.subheader("Current progress")
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
        time.sleep(1)  # Simulate progress

def select_llm() -> None:
    llm_list=""
    selected_llm_list = ""
    container = st.empty()
    container.empty()
    with container.container():
        st.text_input(
            "Ollama endpoint:",
            "http://<url>:<port number>",
            key="llm_endpoints"
        )

        if is_valid_url(st.session_state.llm_endpoints) or (st.session_state.llm_endpoints == "mock test") :
            client = Client(host=st.session_state.llm_endpoints)
            # Get model list for evaluation
            if st.session_state.llm_endpoints == "mock test":
                llm_list = ["llama3:8b-text-q4_0", "wizardlm2:7b-q4_0", "qwen:7b-q4_0", "qwen:4b-chat-v1.5-q4_0", "openhermes:7b-mistral-v2.5-q4_0", "tinyllama:1.1b-chat-v0.6-q4_0", "falcon:7b-instruct-q4_0", "falcon:7b-text-q4_0", "stablelm2:12b-q4_0", "stablelm2:1.6b-q4_0", "falcon2:11b-q4_0", "bogus"]
            else:
                try:
                    llm_list = [d[next(iter(d))] for d in ollama.list()['models']] #get model names from the list of dict returned by Ollama
                except:
                    st.error('Cannot connect to the Ollama endpoint. Try again.', icon="🚨")
            # Ask for which model to be evaluated
            if len(llm_list)>0:
                selected_llm_list = st.multiselect(
                    "Please select which model to be evaluated",
                    llm_list
                )
                if st.checkbox("Select all models"):
                    selected_llm_list = llm_list
            if len(selected_llm_list)>0:
                st.write(f"You selected {selected_llm_list}")
                st.write("Once you are ready, please click Continue")
                if st.button("Continue"):
                    st.session_state.selected_llm = selected_llm_list
                    st.session_state.apt_state = "generate responses"
                    llm_list=""
                    selected_llm_list = ""
                    container.empty()
        else:
            st.write("The endpoint information is not a valid URL. Try again.")
    return None

def generate_responses() -> None:
    container = st.empty()
    temp = ""
    with container.container():
        st.write(f'You selected the following models:')
        for item in st.session_state.selected_llm:
            temp += f"`{item}`, "
        st.write(temp)

        n = 2000
        display_progress(n)
    
    return None

# Main Streamlit app starts here
show_header()
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
    st.title("Generate Models' Responses")
if not st.session_state.healthcheck_passed:
    st.warning("System health checking is not passed or not performed. Please run health check.")
    st.stop()

#st.markdown(f"You are currently logged with the role of {st.session_state.role}.")

if st.session_state.apt_state == "load llm":
    select_llm()
if st.session_state.apt_state == "generate responses":   
    generate_responses()
st.write("End of page")