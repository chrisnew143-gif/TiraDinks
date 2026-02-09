import streamlit as st
import random
from collections import deque
from itertools import combinations

# =========================================================
# CONFIG
# =========================================================

MAX_PER_COURT = 10

# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="Pickleball Auto Stack",
    page_icon="🎾",
    layout="wide"
)

# =========================================================
# HELPERS
# =========================================================

def skill_icon(cat):
    return {
        "BEGINNER": "🟢",
        "NOVICE": "🟡",
        "INTERMEDIATE": "🔴"
    }[cat]


def format_player(p):
    return f"{skill_icon(p[1])} {p[0]}"


def make_teams(players):
    random.shuffle(players)
    return [players[:2], players[2:]]


# =========================================================
# MATCHING
# =========================================================

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
# COURT LOGIC
# =========================================================

def start_match(court_id):
    four = pick_four_fifo_safe(st.session_state.queue)
    if four:
        st.session_state.courts[court_id] = make_teams(four)


def auto_fill():
    for c in st.session_state.courts:
        if st.session_state.courts[c] is None:
            start_match(c)


def finish_match(court_id, winner_idx):

    teams = st.session_state.courts[court_id]

    winners = teams[winner_idx]
    losers = teams[1 - winner_idx]

    # winners first for fairness rotation
    st.session_state.queue.extend(winners + losers)

    st.session_state.courts[court_id] = None

    auto_fill()


# =========================================================
# SESSION STATE
# =========================================================

if "queue" not in st.session_state:
    st.session_state.queue = deque()

if "courts" not in st.session_state:
    st.session_state.courts = {}

if "started" not in st.session_state:
    st.session_state.started = False

if "court_count" not in st.session_state:
    st.session_state.court_count = 2

if "action" not in st.session_state:
    st.session_state.action = None


# =========================================================
# HEADER
# =========================================================

st.title("🎾 Pickleball Auto Stack")
st.caption("First come • first play • fair rotation")


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙ Setup")

    st.session_state.court_count = st.selectbox(
        "Number of courts",
        [2,3,4,5,6,7]
    )

    max_players = st.session_state.court_count * MAX_PER_COURT

    st.divider()

    st.subheader("➕ Add Player")

    with st.form("add_player_form", clear_on_submit=True):

        name = st.text_input("Name")

        cat = st.radio(
            "Skill",
            ["Beginner", "Novice", "Intermediate"]
        )

        submitted = st.form_submit_button("Add to Queue")

        if submitted and name.strip():

            if len(st.session_state.queue) >= max_players:
                st.warning("Queue full")
            else:
                st.session_state.queue.append((name.strip(), cat.upper()))

    st.divider()

    if st.button("🚀 Start Games", use_container_width=True):
        st.session_state.started = True
        st.session_state.courts = {
            i: None for i in range(1, st.session_state.court_count + 1)
        }
        auto_fill()

    if st.button("🔄 Reset All", use_container_width=True):
        st.session_state.queue = deque()
        st.session_state.courts = {}
        st.session_state.started = False


# =========================================================
# WAITING LIST
# =========================================================

st.subheader("⏳ Waiting Queue")

waiting = [format_player(p) for p in st.session_state.queue]

if waiting:
    st.write(", ".join(waiting))
else:
    st.success("No players waiting 🎉")


if not st.session_state.started:
    st.info("Add players then press Start Games")
    st.stop()


# =========================================================
# COURTS
# =========================================================

st.divider()
st.subheader("🏟 Live Courts")

for court_id in st.session_state.courts:

    st.markdown(f"### Court {court_id}")

    teams = st.session_state.courts[court_id]

    if teams:

        teamA = " & ".join(format_player(p) for p in teams[0])
        teamB = " & ".join(format_player(p) for p in teams[1])

        st.write("Team A:", teamA)
        st.write("Team B:", teamB)

        c1, c2 = st.columns(2)

        if c1.button("🏆 A Wins", key=f"a{court_id}"):
            st.session_state.action = (court_id, 0)

        if c2.button("🏆 B Wins", key=f"b{court_id}"):
            st.session_state.action = (court_id, 1)

    else:
        st.info("Waiting for players...")


# =========================================================
# PROCESS ACTION (ONE TIME ONLY)
# =========================================================

if st.session_state.action:

    court_id, winner = st.session_state.action
    finish_match(court_id, winner)

    st.session_state.action = None
    st.rerun()
