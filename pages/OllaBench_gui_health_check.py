import os
import hashlib
import json
from datetime import datetime
import csv
import streamlit as st
from OllaBench_gui_menu import menu_with_redirect, show_header


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

# Retrieve the role from Session State to initialize the widget
st.session_state._role = st.session_state.role

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
    st.title("System Health Checking")
    st.markdown(f"You are currently logged with the role of {st.session_state.role}.")
    csv_file_path = "admin/file_list.csv"
    check_results_path = "admin/health_checks.csv"
    data = read_data_from_csv(csv_file_path)
    results = check_files_integrity(data, json_file_path=check_results_path)
    nonreviewed_changes=load_and_filter_results(check_results_path, reviewed_status='0')
    if len(results)==0 and len(nonreviewed_changes)==0: #will add more health check criteria in later versions
        st.session_state.healthcheck_passed = True
        st.write(":heavy_check_mark: Systems are healthy.")
    else:
        st.write(":octagonal_sign: Systems are not healthy.")
        if st.session_state.role == "admin":
            st.write("Detected new changes:")
            st.write(results)
            st.write("Detected non-reviewed changes:")
            st.write(nonreviewed_changes)