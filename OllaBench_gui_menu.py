import streamlit as st
import time

def show_header():
    col1, col2 = st.columns([0.1,0.2])
    with col1:
        st.write(" ")
    with col2:
        st.image('logo.png', width=120)
    return None
    
def logout():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.switch_page("OllaBench1_gui.py")
    return None

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
        st.sidebar.page_link("pages/privacy.py", label="Privacy Policy")
        st.sidebar.page_link("pages/tos.py", label="Terms of Service")
        if st.sidebar.button("Logout"):
            logout()
        


def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("pages/OllaBench_gui_about.py", label=":blush: Understanding OllaBench")
    st.sidebar.page_link("pages/privacy.py", label="Privacy Policy")
    st.sidebar.page_link("pages/tos.py", label="Terms of Service")
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

def display_progress(n,current):
    # Calculate the number of squares
    num_squares = (n + 49) // 50

    # Initialize progress list with False (grey) indicating incomplete
    progress = [False] * num_squares

    # Streamlit application
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
    for i in range(current // 50 + 1):
        if i > 0:
            progress[i-1] = True
        update_progress()