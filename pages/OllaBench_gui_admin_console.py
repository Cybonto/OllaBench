import streamlit as st
import json
from OllaBench_gui_menu import menu_with_redirect

# Retrieve the role from Session State to initialize the widget
st.session_state._role = st.session_state.role

menu_with_redirect()

# Verify the user's role
if st.session_state.role not in ["admin", "user"]:
    st.warning("You do not have permission to view this page.")
    st.stop()

# Load the JSON data from the file
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Save the JSON data to the file
def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

json_file_path = 'admin/health_checks.csv'

# Load file change logs for review
data = load_json(json_file_path)

st.title("Admin Console")
st.markdown(f"You are currently logged with the role of {st.session_state.role}.")

# Select entry to update
entry_index = st.selectbox("Select entry to update", range(len(data)), format_func=lambda x: data[x]['name'])

# Display the form for the selected entry
with st.form(key='json_form'):
    category = data[entry_index]['category']
    st.write(category)
    file_path = data[entry_index]['file_path']
    admin_reviewed = st.text_input("Admin reviewed", value=data[entry_index]['admin reviewed'])

    submit_button = st.form_submit_button(label='Update JSON')

# Update JSON data on form submission
if submit_button:
    data[entry_index]['category'] = category
    data[entry_index]['file path'] = file_path
    data[entry_index]['admin reviewed'] = admin_reviewed

    # Save the updated data to the file
    save_json(data, json_file_path)
    st.success("JSON file updated successfully!")

    # Display the updated data
    st.json(data)