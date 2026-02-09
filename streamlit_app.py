import streamlit as st
import random
import pandas as pd
from collections import deque
from itertools import combinations
from io import BytesIO

# =========================================================
# CONFIG
# =========================================================
MAX_PER_COURT = 10

# =========================================================
# PAGE SETUP
# =========================================================
st.set_page_config(
    page_title="Pickleball Auto Stack",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ Hide GitHub + menu + footer
st.markdown("""
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.court-card {
    padding: 15px;
    border-radius: 15px;
    background-color: #f3f6fa;
    margin-bottom: 10px;
}
.waiting-box {
    background-color: #fff3cd;
    padding: 12px;
    border-radius: 10px;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPERS
# =========================================================
def skill_icon(cat):
    return {"BEGINNER":"🟢","NOVICE":"🟡","INTERMEDIATE":"🔴"}[cat]

def format_player(p):
    return f"{skill_icon(p[1])} {p[0]}"

def make_teams(players):
    random.shuffle(players)
    return [players[:2], players[2:]]

def is_safe_combo(players):
    skills = {p[1] for p in players}
    return not ("BEGINNER" in skills and "INTERMEDIATE" in skills)

def pick_four_fifo_safe(queue):
    if len(queue) < 4:
        return None
    players = list(queue)
    for combo in combinations(players, 4):
        if is_safe_combo(combo):
            for p in combo:
                queue.remove(p)
            return list(combo)
    return None

# =========================================================
# SESSION STATE
# =========================================================
defaults = {
    "queue": deque(),
    "courts": {},
    "court_locked": {},
    "started": False,
    "court_count": 2,
    "match_log": []   # ⭐ NEW (store results)
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =========================================================
# LOGGING + EXPORT
# =========================================================
def log_match(court_id, teamA, teamB, scoreA, scoreB):
    st.session_state.match_log.append({
        "Court": court_id,
        "Team A": " & ".join(p[0] for p in teamA),
        "Team B": " & ".join(p[0] for p in teamB),
        "Score A": scoreA,
        "Score B": scoreB,
        "Winner": "A" if scoreA > scoreB else "B"
    })

def create_excel():
    df = pd.DataFrame(st.session_state.match_log)
    output = BytesIO()
    df.to_excel(output, index=False)
    return output.getvalue()

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.header("⚙ Setup")

    st.session_state.court_count = st.selectbox("Courts",[2,3,4,5,6,7])

    max_players = st.session_state.court_count * MAX_PER_COURT
    st.write(f"Max players: **{max_players}**")

    st.divider()

    # Add player
    with st.form("add_player", clear_on_submit=True):
        name = st.text_input("Player name")
        skill = st.radio("Skill",["Beginner","Novice","Intermediate"])
        if st.form_submit_button("Add"):
            st.session_state.queue.append((name, skill.upper()))

    st.divider()

    if st.button("🚀 Start Games", use_container_width=True):
        st.session_state.started = True
        st.session_state.courts = {i:None for i in range(1, st.session_state.court_count+1)}
        st.session_state.court_locked = {i:False for i in range(1, st.session_state.court_count+1)}

    if st.button("🔄 Reset All", use_container_width=True):
        for k in defaults:
            st.session_state[k] = defaults[k]

    st.divider()

    # ⭐ DOWNLOAD BUTTON
    if st.session_state.match_log:
        st.download_button(
            "⬇️ Download Results (.xlsx)",
            data=create_excel(),
            file_name="pickleball_scores.xlsx"
        )

# =========================================================
# COURT LOGIC
# =========================================================
def start_match(court_id):
    if st.session_state.court_locked[court_id]:
        return
    four = pick_four_fifo_safe(st.session_state.queue)
    if four:
        st.session_state.courts[court_id] = make_teams(four)
        st.session_state.court_locked[court_id] = True

def submit_score(court_id, scoreA, scoreB):
    teams = st.session_state.courts[court_id]
    if not teams:
        return

    teamA, teamB = teams

    # ⭐ log match
    log_match(court_id, teamA, teamB, scoreA, scoreB)

    # remix back to queue
    players = teamA + teamB
    random.shuffle(players)
    st.session_state.queue.extend(players)

    # unlock court
    st.session_state.courts[court_id] = None
    st.session_state.court_locked[court_id] = False

# =========================================================
# AUTO FILL
# =========================================================
if st.session_state.started:
    for c in st.session_state.courts:
        if st.session_state.courts[c] is None:
            start_match(c)

# =========================================================
# UI
# =========================================================
st.title("🎾 Pickleball Auto Stack")
st.caption("First come • first play • fair rotation")

# waiting queue
st.subheader("⏳ Waiting Queue")
if st.session_state.queue:
    st.markdown('<div class="waiting-box">' +
        ", ".join(format_player(p) for p in st.session_state.queue) +
        '</div>', unsafe_allow_html=True)
else:
    st.success("No players waiting 🎉")

if not st.session_state.started:
    st.stop()

st.divider()
st.subheader("🏟 Live Courts")

for court_id in st.session_state.courts:

    st.markdown('<div class="court-card">', unsafe_allow_html=True)
    st.markdown(f"### Court {court_id}")

    teams = st.session_state.courts[court_id]

    if teams:
        teamA, teamB = teams

        st.write("**Team A**", " & ".join(format_player(p) for p in teamA))
        st.write("**Team B**", " & ".join(format_player(p) for p in teamB))

        col1, col2, col3 = st.columns([1,1,1])

        scoreA = col1.number_input("A",0,key=f"A{court_id}")
        scoreB = col2.number_input("B",0,key=f"B{court_id}")

        if col3.button("Submit", key=f"S{court_id}"):
            submit_score(court_id, scoreA, scoreB)

    else:
        st.info("Waiting for players...")

    st.markdown('</div>', unsafe_allow_html=True)
