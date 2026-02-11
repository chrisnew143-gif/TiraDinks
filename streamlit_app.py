import streamlit as st
import random
from collections import deque
import pandas as pd
from itertools import combinations

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Pickleball Auto Stack",
    page_icon="🎾",
    layout="wide"
)

# ======================================================
# STYLE (compact courts)
# ======================================================
st.markdown("""
<style>
a[href*="github.com/streamlit"]{display:none!important;}

.court-card{
    padding:12px;
    border-radius:12px;
    background:#f4f6fa;
    margin-bottom:8px;
}

.waiting-box{
    background:#fff3cd;
    padding:10px;
    border-radius:10px;
    font-size:16px;
}
</style>
""", unsafe_allow_html=True)

st.title("🎾 Pickleball Auto Stack")
st.caption("First come • first play • fair rotation")

# ======================================================
# HELPERS
# ======================================================
def icon(skill):
    return {
        "BEGINNER": "🟢",
        "NOVICE": "🟡",
        "INTERMEDIATE": "🔴"
    }[skill]


def fmt(p):
    return f"{icon(p[1])} {p[0]}"


# ======================================================
# SAFETY RULE
# Beginner + Intermediate NEVER together
# ======================================================
def safe_group(players):
    skills = {p[1] for p in players}
    return not ("BEGINNER" in skills and "INTERMEDIATE" in skills)


def make_teams(players):
    random.shuffle(players)
    return [players[:2], players[2:]]


# ======================================================
# SESSION INIT
# ======================================================
def init():
    ss = st.session_state
    ss.setdefault("queue", deque())
    ss.setdefault("courts", {})
    ss.setdefault("scores", {})
    ss.setdefault("history", [])
    ss.setdefault("started", False)
    ss.setdefault("court_count", 2)

init()


# ======================================================
# MATCH ENGINE
# FIFO + SAFE PICK
# ======================================================
def take_four_safe():
    q = list(st.session_state.queue)

    if len(q) < 4:
        return None

    # first valid combo wins (FIFO priority)
    for combo in combinations(range(len(q)), 4):
        group = [q[i] for i in combo]

        if safe_group(group):
            for i in sorted(combo, reverse=True):
                del q[i]

            st.session_state.queue = deque(q)
            return group

    return None


def start_match(cid):
    players = take_four_safe()
    if not players:
        return

    st.session_state.courts[cid] = make_teams(players)
    st.session_state.scores[cid] = [0, 0]


def finish_match(cid):
    teams = st.session_state.courts[cid]
    scoreA, scoreB = st.session_state.scores[cid]

    players = teams[0] + teams[1]

    # save history
    st.session_state.history.append({
        "Court": cid,
        "Team A": " & ".join(p[0] for p in teams[0]),
        "Team B": " & ".join(p[0] for p in teams[1]),
        "Score A": scoreA,
        "Score B": scoreB
    })

    # fair rotation (shuffle then back to queue)
    random.shuffle(players)
    st.session_state.queue.extend(players)

    st.session_state.courts[cid] = None
    st.session_state.scores[cid] = [0, 0]


def auto_fill():
    if not st.session_state.started:
        return

    for cid in st.session_state.courts:
        if st.session_state.courts[cid] is None:
            start_match(cid)


# ======================================================
# CSV
# ======================================================
def create_csv():
    if not st.session_state.history:
        return b""
    df = pd.DataFrame(st.session_state.history)
    return df.to_csv(index=False).encode()


# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:

    st.header("⚙ Setup")

    st.session_state.court_count = st.selectbox("Courts", [2, 3, 4, 5, 6])

    # -----------------------
    # ADD PLAYER (FRONT)
    # -----------------------
    with st.form("add", clear_on_submit=True):
        name = st.text_input("Name")
        skill = st.radio("Skill", ["Beginner", "Novice", "Intermediate"])

        if st.form_submit_button("Add Player") and name:
            st.session_state.queue.appendleft((name, skill.upper()))

    # -----------------------
    # DELETE PLAYER
    # -----------------------
    if st.session_state.queue:
        st.subheader("❌ Remove Player")

        names = [p[0] for p in st.session_state.queue]
        pick = st.selectbox("Select player", names)

        if st.button("Remove"):
            st.session_state.queue = deque(
                [p for p in st.session_state.queue if p[0] != pick]
            )
            st.rerun()

    st.divider()

    # -----------------------
    # CONTROLS
    # -----------------------
    if st.button("🚀 Start Games"):
        st.session_state.started = True
        st.session_state.courts = {
            i: None for i in range(1, st.session_state.court_count + 1)
        }
        st.rerun()

    if st.button("🔄 Reset"):
        st.session_state.clear()
        st.rerun()

    st.download_button(
        "📥 Download Results (CSV)",
        data=create_csv(),
        file_name="pickleball_results.csv",
        mime="text/csv"
    )


# ======================================================
# AUTO FILL FIRST
# ======================================================
auto_fill()


# ======================================================
# WAITING QUEUE
# ======================================================
st.subheader("⏳ Waiting Queue")

if st.session_state.queue:
    st.markdown(
        f'<div class="waiting-box">{", ".join(fmt(p) for p in st.session_state.queue)}</div>',
        unsafe_allow_html=True
    )
else:
    st.success("No players waiting 🎉")

if not st.session_state.started:
    st.stop()


# ======================================================
# COURTS (COMPACT VERSION ⭐)
# ======================================================
st.divider()
st.subheader("🏟 Live Courts")

for cid in st.session_state.courts:

    st.markdown('<div class="court-card">', unsafe_allow_html=True)
    st.markdown(f"**Court {cid}**")

    teams = st.session_state.courts[cid]

    if not teams:
        st.caption("Waiting for safe players...")
        st.markdown('</div>', unsafe_allow_html=True)
        continue

    teamA = " & ".join(fmt(p) for p in teams[0])
    teamB = " & ".join(fmt(p) for p in teams[1])

    # ⭐ ONE ROW LAYOUT (less scroll)
    c1, c2, c3, c4 = st.columns([6, 1, 1, 2])

    c1.write(f"{teamA}  vs  {teamB}")

    a = c2.number_input("", 0, key=f"A{cid}")
    b = c3.number_input("", 0, key=f"B{cid}")

    if c4.button("Submit", key=f"S{cid}"):
        st.session_state.scores[cid] = [a, b]
        finish_match(cid)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
