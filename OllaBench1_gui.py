import hmac
import streamlit as st
from OllaBench_gui_menu import menu, show_header

st.set_page_config(
    page_title="OllaBench1 v.0.2",
    initial_sidebar_state="expanded"
)

# Initialize st.session_state
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
menu()

# If user is not logged in, show login form
if "role" not in st.session_state or st.session_state.role is None:
    st.markdown("## Please log in to access OllaBench features")
    if not check_password():
        st.stop()
col1, col2 = st.columns([0.1,0.2])
with col1:
    st.write(" ")
with col2:
    st.image('logo.png', width=180)
st.markdown('''
            <div align="center">
            <h4> OllaBench is a novel a benchmark platform and dataset generator to evaluate Large Language Models' ability to reason and make decisions based on cognitive behavioral insights in cybersecurity. </h4>

            [![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat)]()
            [![python](https://img.shields.io/badge/python-3.10-green)]()
            [![Static Badge](https://img.shields.io/badge/release-0.2-green?style=flat&color=green)]()
            [![license](https://img.shields.io/badge/license-Apache%202-blue)](./LICENSE)


            The grand challenge that most CEO's care about is maintaining the right level of cybersecurity at a minimum cost as companies are not able to reduce cybersecurity risks despite their increased cybersecurity investments [[1]](https://www.qbusiness.pl/uploads/Raporty/globalrisk2021.pdf). Fortunately, the problem can be explained via interdependent cybersecurity (IC) [[2]](https://www.nber.org/system/files/working_papers/w8871/w8871.pdf). Human factors account for half of the long-lasting challenges in IC as identified by Kianpour et al. [[3]](https://www.mdpi.com/2071-1050/13/24/13677), and Laszka et al. [[4]](http://real.mtak.hu/21924/1/Buttyan4.pdf). Unfortunately, human-centric research within the context of IC is under-explored while research on general IC has unrealistic assumptions about human factors. Fortunately, the dawn of Large Language Models (LLMs) promise a much efficient way to research and develop solutions to human-centric problems across domains. We also note that the Zero-trust principles require the evaluation, validation, and continuous monitoring of AI applications including LLMs.

            Therefore, OllaBench was born to help both researchers and application developers conveniently evaluate their LLM models within the context of cybersecurity compliance or non-compliance behaviors. The main goal is to help with identifying the right LLM in the early phase of developing an LLM-based application.</div>
            ''',unsafe_allow_html=True)
st.markdown("**Introduction Video (90s)**")
col1, col2 = st.columns([0.04,0.9])
with col1:
    st.write(" ")
with col2:
    st.video('https://youtu.be/o-uIvInsOMA')
st.markdown("**Demonstration of use (3mins)**")
col1, col2 = st.columns([0.04,0.9])
with col1:
    st.write(" ")
with col2:
    st.video('https://youtu.be/aOEGLCnLo1M')