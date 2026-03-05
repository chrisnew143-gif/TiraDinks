import streamlit as st

st.set_page_config(page_title="TiraDinks", layout="centered")

# =========================
# BACKGROUND IMAGE
# =========================
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
background-image: url("TDphoto.jpg");
background-size: cover;
background-position: center;
background-repeat: no-repeat;
background-attachment: fixed;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)


# =========================
# HARDCODED USERS
# =========================
users = {
    "tiradinks1": {"password": "123456", "role": "organizer"},
    "tiradinks2": {"password": "123456", "role": "member"},
}


# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "user" not in st.session_state:
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
            st.session_state.role = users[username]["role"]
            st.session_state.user = username

            st.success("Login successful")
            st.rerun()

        else:
            st.error("Invalid username or password")


# =========================
# MAIN PAGE AFTER LOGIN
# =========================
def home():

    st.sidebar.title("🏓 TiraDinks")
    st.sidebar.write(f"Logged in as **{st.session_state.user}**")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.user = None
        st.rerun()

    st.title("🏓 Welcome to TiraDinks")
    st.write("Use the sidebar to navigate the application.")


# =========================
# ROUTING
# =========================
if not st.session_state.logged_in:
    login()
else:
    home()
