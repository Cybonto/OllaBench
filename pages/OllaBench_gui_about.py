import streamlit as st
from OllaBench_gui_menu import menu_with_redirect

# Retrieve the role from Session State to initialize the widget
st.session_state._role = st.session_state.role

menu_with_redirect()

# Verify the user's role
if st.session_state.role not in ["admin", "user"]:
    st.warning("You do not have permission to view this page.")
    st.stop()

st.title("This page is available to all admins")
st.markdown(f"You are currently logged with the role of {st.session_state.role}.")