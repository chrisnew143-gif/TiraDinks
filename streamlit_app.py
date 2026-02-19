import streamlit as st

st.set_page_config(page_title="Pickleball Manager", layout="centered")

st.title("🏠 Pickleball Manager")
st.write("Welcome to the Auto Stack Application!")

st.divider()

# Open Play Button
if st.button("🎾 Open Play Stacking", use_container_width=True):
    st.switch_page("pages/AutoStack.py")

st.divider()

# DUPR Match Button
if st.button("🏆 DUPR Match", use_container_width=True):
    st.switch_page("pages/DUPRMatch.py")
