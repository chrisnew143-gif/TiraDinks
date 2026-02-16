import streamlit as st

st.set_page_config(page_title="Pickleball Manager", layout="centered")

# -------------------------
# Router
# -------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

def go(page):
    st.session_state.page = page
    st.rerun()


# =========================
# HOME
# =========================
if st.session_state.page == "home":

    st.title("🎾 Pickleball Stack System")

    col1, col2, col3 = st.columns(3)

    if col1.button("🏟 Organizer (AutoStack)", use_container_width=True):
        go("autostack")

    if col2.button("👤 Player Join", use_container_width=True):
        go("player")

    if col3.button("🏢 Clubs", use_container_width=True):
        go("registerclub")


# =========================
# AUTOSTACK
# =========================
elif st.session_state.page == "autostack":

    if st.button("⬅ Back to Home"):
        go("home")

    import AutoStack   # your module


# =========================
# PLAYER
# =========================
elif st.session_state.page == "player":

    if st.button("⬅ Back to Home"):
        go("home")

    import PlayerJoin   # your module


# =========================
# REGISTER CLUB (placeholder)
# =========================
elif st.session_state.page == "registerclub":

    if st.button("⬅ Back to Home"):
        go("home")

    st.markdown("## 🚧 Under Construction 🚧")
    st.info("Club registration feature coming soon!")
