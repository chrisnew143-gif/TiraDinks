import streamlit as st

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

/* hide default sidebar pages */
[data-testid="stSidebarNav"] {display:none;}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)


# =========================
# USERS (HARDCODED)
# =========================
users = {
    "tiradinks1": {"password": "123456", "role": "organizer"},
    "tiradinks2": {"password": "123456", "role": "member"}
}


# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user = None


# =========================
# LOGIN PAGE
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

            st.rerun()

        else:
            st.error("Invalid username or password")


# =========================
# LOGOUT
# =========================
def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user = None
    st.rerun()


# =========================
# MAIN APP
# =========================
def main_app():

    st.sidebar.title("🏓 TiraDinks Menu")
    st.sidebar.write(f"Logged in as **{st.session_state.user}**")

    if st.sidebar.button("Logout"):
        logout()

    # =========================
    # ORGANIZER MENU
    # =========================
    if st.session_state.role == "organizer":

        page = st.sidebar.selectbox(
            "Navigate",
            [
                "AutoStack",
                "DUPRmatch",
                "Player Profile",
                "Players Leader Board",
                "Schedules"
            ]
        )

        if page == "AutoStack":
            st.switch_page("pages/AutoStack.py")

        if page == "DUPRmatch":
            st.switch_page("pages/DUPRmatch.py")

        if page == "Player Profile":
            st.switch_page("pages/Player Profile.py")

        if page == "Players Leader Board":
            st.switch_page("pages/Players Leader Board.py")

        if page == "Schedules":
            st.switch_page("pages/Schedules.py")


    # =========================
    # MEMBER MENU
    # =========================
    else:

        st.sidebar.success("Players Leader Board")

        st.switch_page("pages/Players Leader Board.py")


# =========================
# PAGE ROUTING
# =========================
if not st.session_state.logged_in:
    login()
else:
    main_app()
