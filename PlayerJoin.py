import streamlit as st

st.title("👤 Player Join")
st.markdown("## 🚧 Under Construction 🚧")
st.info("Player join feature coming soon!")

# ✅ Back button
if st.button("⬅ Back to Home"):
    st.session_state.page = "home"
    st.rerun()
