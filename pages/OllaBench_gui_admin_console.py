import streamlit as st
import json
from OllaBench_gui_menu import menu_with_redirect

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

# Filter entries with admin_reviewed = 0
unreviewed_entries = [entry for entry in data if entry['admin_reviewed'] == "0"]

# Display unreviewed entries
if unreviewed_entries:
    st.write("Unreviewed Entries:")
    for i, entry in enumerate(unreviewed_entries):
        st.json(entry)
        if st.button(f"Approve {i}", key=f"approve_{i}"):
            # Update the admin_reviewed value to 1
            entry['admin_reviewed'] = "1"
            st.success(f"Entry {i} approved!")

    # Save the updated data to the file
    save_json(data, json_file_path)
else:
    st.write("No unreviewed entries found.")