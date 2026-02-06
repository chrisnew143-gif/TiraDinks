import streamlit as st

# ================== SESSION STATE NAV ==================
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_home():
    st.session_state.page = "home"

def go_autostack():
    st.session_state.page = "autostack"

def go_player():
    st.session_state.page = "player"

# ================== HOMEPAGE ==================
if st.session_state.page == "home":
    st.set_page_config(page_title="Pickleball Manager", layout="centered")
    st.title("🎾 Pickleball Stack System")
    st.write("Welcome! Choose where you want to go:")

    col1, col2 = st.columns(2)
    if col1.button("🏟 AutoStack Organizer"):
        go_autostack()
    if col2.button("👤 Player Join"):
        go_player()

# ================== NAVIGATION TO PAGES ==================
elif st.session_state.page == "autostack":
    import pages.auto_stack_page as autostack
    autostack.show(go_home)

elif st.session_state.page == "player":
    import pages.player_join_page as player
    player.show(go_home)
