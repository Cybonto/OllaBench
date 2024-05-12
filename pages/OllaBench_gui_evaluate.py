import streamlit as st
from OllaBench_gui_menu import menu_with_redirect, show_header

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
    st.title("Evaluate Models' Responses")
if not st.session_state.healthcheck_passed:
    st.warning("System health checking is not passed or not performed. Please run health check.")
    st.stop()
    
st.markdown(f"You are currently logged with the role of {st.session_state.role}.")