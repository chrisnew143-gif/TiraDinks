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

# Hide ONLY github icon
st.markdown("""
<style>
a[href*="github.com/streamlit"]{display:none!important;}

.court-card{
    padding:18px;
    border-radius:14px;
    background:#f4f6fa;
    margin-bottom:14px;
}

.waiting-box{
    background:#fff3cd;
    padding:12px;
    border-radius:10px;
    font-size:17px;
}
</style>
""", unsafe_allow_html=True)

st.title("🎾 Pickleball Auto Stack")
st.caption("First come • first play • fair rotation")

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


# =========================================================
# ⭐ SAFE MATCH RULES (THE IMPORTANT PART)
# =========================================================
def safe_pair(a, b):
    """
    Beginner ❌ Intermediate
    Everything else ✅
    """
    s = {a[1], b[1]}
    return not ("BEGINNER" in s and "INTERMEDIATE" in s)


def make_safe_teams(players):
    """
    Create teams WITHOUT beginner vs intermediate
    """
    random.shuffle(players)

    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            if safe_pair(players[i], players[j]):
                teamA = [players[i], players[j]]
                rest = [p for k, p in enumerate(players) if k not in (i, j)]

                if safe_pair(rest[0], rest[1]):
                    return [teamA, rest]

    # fallback (should rarely happen)
    return [players[:2], players[2:]]


# =========================================================
# SESSION INIT
# =========================================================
def init():
    ss = st.session_state
    ss.setdefault("queue", deque())
    ss.setdefault("courts", {})
    ss.setdefault("locked", {})
    ss.setdefault("scores", {})
    ss.setdefault("history", [])
    ss.setdefault("started", False)
    ss.setdefault("court_count", 2)


init()


# =========================================================
# MATCH ENGINE
# =========================================================
def take_four():
    if len(st.session_state.queue) < 4:
        return None
    return [st.session_state.queue.popleft() for _ in range(4)]


def start_match(cid):
    if st.session_state.locked[cid]:
        return

    players = take_four()
    if not players:
        return

    st.session_state.courts[cid] = make_safe_teams(players)
    st.session_state.locked[cid] = True
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

    random.shuffle(players)
    st.session_state.queue.extend(players)

    st.session_state.courts[cid] = None
    st.session_state.locked[cid] = False
    st.session_state.scores[cid] = [0, 0]


def auto_fill():
    if not st.session_state.started:
        return

    for cid in st.session_state.courts:
        if st.session_state.courts[cid] is None:
            start_match(cid)


# =========================================================
# CSV
# =========================================================
def create_csv():
    if not st.session_state.history:
        return b""
    df = pd.DataFrame(st.session_state.history)
    return df.to_csv(index=False).encode()


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.header("⚙ Setup")

    st.session_state.court_count = st.selectbox("Courts", [2,3,4,5,6])

    # =========================
    # ADD PLAYER (FRONT)
    # =========================
    with st.form("add", clear_on_submit=True):
        name = st.text_input("Name")
        skill = st.radio("Skill", ["Beginner","Novice","Intermediate"])
        ok = st.form_submit_button("Add Player")

        if ok and name:
            st.session_state.queue.appendleft((name, skill.upper()))  # ⭐ FRONT

    # =========================
    # DELETE PLAYER
    # =========================
    if st.session_state.queue:
        st.subheader("❌ Remove Player")

        options = [p[0] for p in st.session_state.queue]
        remove_name = st.selectbox("Select player", options)

        if st.button("Remove"):
            st.session_state.queue = deque(
                [p for p in st.session_state.queue if p[0] != remove_name]
            )
            st.rerun()

    st.divider()

    if st.button("🚀 Start Games"):
        st.session_state.started = True
        st.session_state.courts = {i:None for i in range(1, st.session_state.court_count+1)}
        st.session_state.locked = {i:False for i in range(1, st.session_state.court_count+1)}
        st.session_state.scores = {i:[0,0] for i in range(1, st.session_state.court_count+1)}
        st.rerun()

    if st.button("🔄 Reset"):
        st.session_state.clear()
        st.rerun()

    st.download_button(
        "📥 Download Results",
        data=create_csv(),
        file_name="pickleball_results.csv",
        mime="text/csv"
    )


# =========================================================
# FILL FIRST
# =========================================================
auto_fill()


# =========================================================
# WAITING
# =========================================================
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


# =========================================================
# COURTS
# =========================================================
st.divider()
st.subheader("🏟 Live Courts")

for cid in st.session_state.courts:

    st.markdown('<div class="court-card">', unsafe_allow_html=True)
    st.markdown(f"### Court {cid}")

    teams = st.session_state.courts[cid]

    if not teams:
        st.info("Waiting for players...")
        st.markdown('</div>', unsafe_allow_html=True)
        continue

    st.write("**Team A**  \n" + " & ".join(fmt(p) for p in teams[0]))
    st.write("**Team B**  \n" + " & ".join(fmt(p) for p in teams[1]))

    scoreA = st.number_input("Score A", 0, key=f"A{cid}")
    scoreB = st.number_input("Score B", 0, key=f"B{cid}")

    if st.button("Submit Score", key=f"S{cid}"):
        st.session_state.scores[cid] = [scoreA, scoreB]
        finish_match(cid)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
