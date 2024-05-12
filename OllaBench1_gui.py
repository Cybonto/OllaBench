import hmac
import streamlit as st
from OllaBench_gui_menu import menu, show_header

# Initialize st.session_state.role to None
if "role" not in st.session_state:
    st.session_state.role = None
if "password" not in st.session_state:
    st.session_state.password = None
if "username" not in st.session_state:
    st.session_state.username = None
if "healthcheck_passed" not in st.session_state:
    st.session_state.healthcheck_passed = False

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

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
            #del st.session_state["username"] # Persist username value for later use
        else:
            st.session_state.password_correct = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


# Main Streamlit app starts here
show_header()
if not check_password():
    st.stop()
menu()

st.write("Brief introduction and stated important requirements")
st.write(st.session_state.role)