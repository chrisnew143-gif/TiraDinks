import streamlit as st
import random
from collections import deque
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Pickleball Auto Stack",
    page_icon="🎾",
    layout="wide"
)

# Hide Streamlit header + GitHub icon
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

.court-card {
    padding: 16px;
    border-radius: 14px;
    background: #f4f6fa;
    margin-bottom: 14px;
}

.waiting-box {
    background: #fff3cd;
    padding: 12px;
    border-radius: 10px;
    font-size: 17px;
}
</style>
""", unsafe_allow_html=True)

st.title("🎾 Pickleball Auto Stack")
st.caption("First come • first play • fair rotation")

# =========================================================
# CONSTANTS
# =========================================================
MAX_PER_COURT = 10


# =========================================================
# HELPERS
# =========================================================
def icon(skill):
    return {
        "BEGINNER": "🟢",
        "NOVICE": "🟡",
        "INTERMEDIATE": "🔴"
    }[skill]


def fmt(p):
    return f"{icon(p[1])} {p[0]}"


def make_teams(players):
    random.shuffle(players)
    return [players[:2], players[2:]]


# =========================================================
# SESSION STATE INIT
# =========================================================
def init():
    ss = st.session_state

    if "queue" not in ss:
        ss.queue = deque()

    if "courts" not in ss:
        ss.courts = {}

    if "locked" not in ss:
        ss.locked = {}

    if "scores" not in ss:
        ss.scores = {}

    if "history" not in ss:
        ss.history = []

    if "started" not in ss:
        ss.started = False

    if "court_count" not in ss:
        ss.court_count = 2


init()


# =========================================================
# MATCH ENGINE
# =========================================================
def get_four_players():
    if len(st.session_state.queue) < 4:
        return None

    four = [st.session_state.queue.popleft() for _ in range(4)]
    return four


def start_match(court_id):
    if st.session_state.locked[court_id]:
        return

    players = get_four_players()
    if not players:
        return

    st.session_state.courts[court_id] = make_teams(players)
    st.session_state.scores[court_id] = [0, 0]
    st.session_state.locked[court_id] = True


def finish_match(court_id):
    teams = st.session_state.courts[court_id]
    scoreA, scoreB = st.session_state.scores[court_id]

    players = teams[0] + teams[1]

    # save history
    st.session_state.history.append({
        "Court": court_id,
        "Team A": " & ".join(p[0] for p in teams[0]),
        "Team B": " & ".join(p[0] for p in teams[1]),
        "Score A": scoreA,
        "Score B": scoreB
    })

    # mix players
    random.shuffle(players)
    for p in players:
        st.session_state.queue.append(p)

    # reset court
    st.session_state.courts[court_id] = None
    st.session_state.locked[court_id] = False
    st.session_state.scores[court_id] = [0, 0]


def auto_fill():
    if not st.session_state.started:
        return

    for cid in st.session_state.courts:
        if st.session_state.courts[cid] is None:
            start_match(cid)


# =========================================================
# CSV DOWNLOAD (NO OPENPYXL NEEDED)
# =========================================================
def create_csv():
    if not st.session_state.history:
        return b""

    df = pd.DataFrame(st.session_state.history)
    return df.to_csv(index=False).encode("utf-8")


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.header("⚙ Setup")

    st.session_state.court_count = st.selectbox(
        "Courts",
        [2, 3, 4, 5, 6]
    )

    max_players = st.session_state.court_count * MAX_PER_COURT
    st.write(f"Max players: **{max_players}**")

    st.divider()

    # add player
    with st.form("add", clear_on_submit=True):
        name = st.text_input("Name")
        skill = st.radio("Skill", ["Beginner", "Novice", "Intermediate"])
        ok = st.form_submit_button("Add Player")

        if ok and name:
            st.session_state.queue.append((name, skill.upper()))

    st.divider()

    if st.button("🚀 Start Games", use_container_width=True):
        st.session_state.started = True
        st.session_state.courts = {i: None for i in range(1, st.session_state.court_count + 1)}
        st.session_state.locked = {i: False for i in range(1, st.session_state.court_count + 1)}
        st.session_state.scores = {i: [0, 0] for i in range(1, st.session_state.court_count + 1)}

    if st.button("🔄 Reset All", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.divider()

    # download results
    st.download_button(
        "📥 Download Results (CSV)",
        data=create_csv(),
        file_name="pickleball_results.csv",
        mime="text/csv",
        use_container_width=True
    )


# =========================================================
# WAITING QUEUE
# =========================================================
st.subheader("⏳ Waiting Queue")

if st.session_state.queue:
    names = ", ".join(fmt(p) for p in st.session_state.queue)
    st.markdown(f'<div class="waiting-box">{names}</div>', unsafe_allow_html=True)
else:
    st.success("No players waiting 🎉")


# =========================================================
# STOP IF NOT STARTED
# =========================================================
if not st.session_state.started:
    st.info("Add players then press **Start Games**")
    st.stop()


# =========================================================
# LIVE COURTS
# =========================================================
auto_fill()

st.divider()
st.subheader("🏟 Live Courts")

per_row = 3
ids = list(st.session_state.courts.keys())

for r in range(0, len(ids), per_row):
    cols = st.columns(per_row)

    for i, cid in enumerate(ids[r:r+per_row]):
        with cols[i]:
            st.markdown('<div class="court-card">', unsafe_allow_html=True)

            st.markdown(f"### Court {cid}")

            teams = st.session_state.courts[cid]

            if not teams:
                st.info("Waiting for players...")
                st.markdown('</div>', unsafe_allow_html=True)
                continue

            st.write("**Team A**  \n" + " & ".join(fmt(p) for p in teams[0]))
            st.write("**Team B**  \n" + " & ".join(fmt(p) for p in teams[1]))

            scoreA = st.number_input("Score A", 0, key=f"a{cid}")
            scoreB = st.number_input("Score B", 0, key=f"b{cid}")

            if st.button("Submit Score", key=f"s{cid}"):
                st.session_state.scores[cid] = [scoreA, scoreB]
                finish_match(cid)
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
