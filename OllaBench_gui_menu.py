import streamlit as st

def show_header():
    col1, col2 = st.columns([0.1,0.2])
    with col1:
        st.write(" ")
    with col2:
        st.image('logo.png', width=120)
    return None
    
def logout():
    st.session_state.password_correct = False
    st.session_state.password = None
    st.session_state.password = None
    st.session_state.role = None
    st.session_state.llm_endpoints = " "
    st.session_state.healthcheck_passed = False
    st.session_state.selected_llm = "None"
    st.session_state.llm_list = "None"
    st.switch_page("OllaBench1_gui.py")
    return 

def authenticated_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("OllaBench1_gui.py", label="Home")
    if st.session_state.role in ["admin", "user"]:
        st.sidebar.page_link("pages/OllaBench_gui_about.py", label=":blush: Understanding OllaBench")
        st.sidebar.page_link("pages/OllaBench_gui_health_check.py", label=":mag: Health Check")
        st.sidebar.page_link("pages/OllaBench_gui_generate_dataset.py", label=":arrows_counterclockwise: Generate Dataset")
        st.sidebar.page_link("pages/OllaBench_gui_generate_responses.py", label=":inbox_tray: Generate Responses")
        st.sidebar.page_link("pages/OllaBench_gui_evaluate.py", label=":bar_chart: Evaluate Models")
        st.sidebar.page_link(
            "pages/OllaBench_gui_admin_console.py",
            label=":pick: Admin Console",
            disabled=st.session_state.role != "admin",
        )
        if st.sidebar.button("Logout"):
            logout()
        


def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("OllaBench1_gui.py", label="Log in")


def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu
    if "role" not in st.session_state or st.session_state.role is None:
        unauthenticated_menu()
        return
    authenticated_menu()


def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    if "role" not in st.session_state or st.session_state.role is None:
        st.switch_page("OllaBench1_gui.py")
    if "role" not in st.session_state or st.session_state.role is None:
        st.switch_page("OllaBench1_gui.py")
    menu()