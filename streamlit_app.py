import streamlit as st
import random
from collections import deque


# =========================================================
# PAGE CONFIG (MUST BE FIRST)
# =========================================================
st.set_page_config(
    page_title="TiraDinks Pickleball Auto Stack",
    page_icon="🎾",
    layout="wide"
)


# =========================================================
# 🔒 HIDE STREAMLIT CLOUD UI
# =========================================================
st.markdown("""
<style>
#MainMenu {visibility:hidden;}
header {visibility:hidden;}
footer {visibility:hidden;}
[data-testid="stToolbar"]{display:none;}
[data-testid="stDecoration"]{display:none;}
[data-testid="stStatusWidget"]{display:none;}

.court-card{
    padding:15px;
    border-radius:14px;
    background:#f3f6fa;
}
.waiting-box{
    background:#fff3cd;
    padding:12px;
    border-radius:10px;
    font-size:18px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# CONFIG
# =========================================================
COURT_LIMITS = {2:16,3:26,4:36,5:46,6:56,7:66}


# =========================================================
# HELPERS
# =========================================================
def icon(skill):
    return {"BEGINNER":"🟢","NOVICE":"🟡","INTERMEDIATE":"🔴"}[skill]


def fmt(p):
    return f"{icon(p[1])} {p[0]}"


# ---------------------------------------------------------
# SKILL RULE
# Beginner + Intermediate NOT allowed
# ---------------------------------------------------------
def safe_group(players):
    skills = {p[1] for p in players}
    return not ("BEGINNER" in skills and "INTERMEDIATE" in skills)


# ---------------------------------------------------------
# Balanced mixing inside group
# ---------------------------------------------------------
def make_teams(group):
    random.shuffle(group)  # mix categories
    return [group[:2].copy(), group[2:].copy()]


# =========================================================
# FIFO MATCHING (FAST + SIMPLE)
# =========================================================
def pick_four(queue):

    if len(queue) < 4:
        return None

    temp = list(queue)

    for i in range(len(temp) - 3):

        group = temp[i:i+4]

        if safe_group(group):
            for p in group:
                queue.remove(p)
            return group

    return None


# =========================================================
# COURT LOGIC
# =========================================================
def start_match(court_id):

    group = pick_four(st.session_state.queue)

    if group:
        st.session_state.courts[court_id] = make_teams(group)


def finish_match(court_id, winner_idx):

    teams = st.session_state.courts[court_id]

    if not teams:
        return

    winners = teams[winner_idx]
    losers  = teams[1-winner_idx]

    # winners first, losers next
    st.session_state.queue.extend(winners + losers)

    # only refill THIS court (no global changes)
    st.session_state.courts[court_id] = None
    start_match(court_id)


def auto_fill():

    if not st.session_state.started:
        return

    for cid in st.session_state.courts:
        if st.session_state.courts[cid] is None:
            start_match(cid)


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


# =========================================================
# HEADER
# =========================================================
st.title("🎾 TiraDinks Pickleball Auto Stack")
st.caption("First come • first play • fair skill matching")


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.header("⚙ Setup")

    st.session_state.court_count = st.selectbox(
        "Number of courts",
        list(COURT_LIMITS.keys())
    )

    st.write(f"Max players: **{COURT_LIMITS[st.session_state.court_count]}**")

    st.divider()

    with st.form("add", clear_on_submit=True):

        name = st.text_input("Name")
        skill = st.radio("Skill", ["Beginner","Novice","Intermediate"])

        if st.form_submit_button("Add Player") and name.strip():
            st.session_state.queue.append((name.strip(), skill.upper()))

    st.divider()

    if st.button("🚀 Start Games"):
        st.session_state.started = True
        st.session_state.courts = {
            i:None for i in range(1, st.session_state.court_count+1)
        }

    if st.button("🔄 Reset"):
        st.session_state.queue = deque()
        st.session_state.courts = {}
        st.session_state.started = False


# =========================================================
# MAIN LOGIC
# =========================================================
auto_fill()


# =========================================================
# WAITING QUEUE
# =========================================================
st.subheader("⏳ Waiting Queue")

waiting = [fmt(p) for p in st.session_state.queue]

if waiting:
    st.markdown(
        '<div class="waiting-box">'+", ".join(waiting)+'</div>',
        unsafe_allow_html=True
    )
else:
    st.success("No players waiting 🎉")


if not st.session_state.started:
    st.stop()


# =========================================================
# COURTS GRID
# =========================================================
st.divider()
st.subheader("🏟 Live Courts")

per_row = 3
ids = list(st.session_state.courts.keys())

for r in range(0, len(ids), per_row):

    cols = st.columns(per_row)

    for idx, cid in enumerate(ids[r:r+per_row]):

        with cols[idx]:

            st.markdown('<div class="court-card">', unsafe_allow_html=True)
            st.markdown(f"### Court {cid}")

            teams = st.session_state.courts[cid]

            if teams:
                st.write("**Team A**  \n" + " & ".join(fmt(p) for p in teams[0]))
                st.write("**Team B**  \n" + " & ".join(fmt(p) for p in teams[1]))

                c1, c2 = st.columns(2)

                if c1.button("🏆 A Wins", key=f"a{cid}"):
                    finish_match(cid, 0)

                if c2.button("🏆 B Wins", key=f"b{cid}"):
                    finish_match(cid, 1)
            else:
                st.info("Waiting for players...")

            st.markdown('</div>', unsafe_allow_html=True)
