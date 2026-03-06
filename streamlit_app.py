import streamlit as st
import importlib

st.set_page_config(page_title="Pickleball Manager", layout="centered")

# =========================
# BACKGROUND IMAGE
# =========================
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
background-image: url("TDphoto.jpg");
background-size: cover;
background-position: center;
background-repeat: no-repeat;
background-attachment: fixed;
}

[data-testid="stSidebarNav"] {
display: none;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# =========================
# USERS (HARDCODED)
# =========================
users = {
    "tdorg1": {"password": "123456", "role": "organizer"},
    "tdmem2": {"password": "123456", "role": "member"}
}

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user = None

# =========================
# LOGIN FUNCTION
# =========================
def login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("TDphoto.jpg", width=300)

    st.title("🏠 TiraDinks Official")
    st.write("Welcome to the TiraDinks Club!")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Sign In"):
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.role = users[username]["role"]
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# =========================
# LOGOUT FUNCTION
# =========================
def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user = None
    st.rerun()

# =========================
# MAIN APPLICATION
# =========================
def main_app():
    st.sidebar.title("🏓 TiraDinks Menu")
    st.sidebar.write(f"Logged in as **{st.session_state.user}**")
    st.sidebar.button("Logout", on_click=logout)

    # =========================
    # PAGES MAPPING
    # =========================
    pages = {
        "AutoStack": "pages.AutoStack",
        "DUPRmatch": "pages.DUPRmatch",
        "Player Profile": "pages.Player_Profile",
        "Players Leader Board": "pages.Players_Leader_Board",
        "Schedules": "pages.Schedules"
    }

    # =========================
    # ROLE BASED MENU
    # =========================
    if st.session_state.role == "organizer":
        page_choice = st.sidebar.selectbox("Navigate", list(pages.keys()))
    else:  # members only see Players Leader Board
        page_choice = "Players Leader Board"
        st.sidebar.success("Players Leader Board")

    # =========================
    # DYNAMIC PAGE IMPORT
    # =========================
    try:
        page_module = importlib.import_module(pages[page_choice])
        if hasattr(page_module, "app"):
            page_module.app()  # call the app() function inside the page file
        else:
            st.error(f"{page_choice}.py does not have an `app()` function.")
    except ModuleNotFoundError:
        st.error(f"Module for {page_choice} not found. Check file names in pages/ folder.")

# =========================
# PAGE ROUTING
# =========================
if not st.session_state.logged_in:
    login()
else:
    main_app()
