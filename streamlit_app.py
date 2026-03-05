import streamlit as st

st.set_page_config(page_title="Pickleball Manager", layout="centered")

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
# LOGIN FUNCTION
# =========================
def login():
    st.title("🔐 TiraDinks Login")

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

    st.title("🏠 TiraDinks Official")
    st.write(f"Welcome **{st.session_state.user}**!")

    st.sidebar.button("Logout", on_click=logout)

    # -------------------------
    # ORGANIZER MENU
    # -------------------------
    if st.session_state.role == "organizer":
        page = st.sidebar.selectbox(
            "Menu",
            [
                "Player Leaderboard",
                "Game Manager",
                "Schedule",
                "Settings"
            ]
        )

    # -------------------------
    # MEMBER MENU
    # -------------------------
    else:
        page = st.sidebar.selectbox(
            "Menu",
            ["Player Leaderboard"]
        )

    # =========================
    # PAGES
    # =========================
    if page == "Player Leaderboard":
        st.header("🏆 Player Leaderboard")
        st.write("Leaderboard content here")

    if page == "Game Manager":
        st.header("🎾 Game Manager")
        st.write("Organizer only content")

    if page == "Schedule":
        st.header("📅 Schedule")

    if page == "Settings":
        st.header("⚙️ Settings")


# =========================
# PAGE ROUTING
# =========================
if not st.session_state.logged_in:
    login()
else:
    main_app()
