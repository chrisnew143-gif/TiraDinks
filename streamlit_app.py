import streamlit as st
import random

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Pickleball Manager",
    page_icon="🎾",
    layout="wide"
)

st.title("🎾 Pickleball Stack System")

# =====================================================
# SESSION STATE INIT
# =====================================================

def init_state():
    defaults = {
        "queue": [],
        "games_played": {},
        "courts": {"Court 1": []},
        "mode": "normal",  # normal | event
        "event_pool": []
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()

# =====================================================
# SMALL NUMBER STYLE (games played)
# =====================================================

def label(name):
    games = st.session_state.games_played.get(name, 0)
    return f"🔴 {games} {name}"


# =====================================================
# SIDEBAR – MODE
# =====================================================

st.sidebar.header("⚙️ Settings")

mode = st.sidebar.radio(
    "Mode",
    ["normal", "event"],
    index=0 if st.session_state.mode == "normal" else 1
)

st.session_state.mode = mode


# =====================================================
# NORMAL MODE – ADD PLAYERS
# =====================================================

if mode == "normal":

    st.sidebar.subheader("Add Players")

    names = st.sidebar.text_area(
        "Enter names (one per line)"
    )

    if st.sidebar.button("Add to Queue"):
        for n in names.split("\n"):
            n = n.strip()
            if n and n not in st.session_state.queue:
                st.session_state.queue.append(n)
                st.session_state.games_played.setdefault(n, 0)


# =====================================================
# EVENT MODE – FIXED 12 PLAYERS
# =====================================================

if mode == "event":

    st.sidebar.subheader("🎯 Court 1 Pool (12 players)")

    event_names = st.sidebar.text_area(
        "Enter EXACTLY 12 names",
        height=200
    )

    if st.sidebar.button("Load Pool"):
        players = [x.strip() for x in event_names.split("\n") if x.strip()]

        if len(players) != 12:
            st.sidebar.error("Must be exactly 12 players")
        else:
            st.session_state.event_pool = players.copy()
            st.session_state.queue = []
            st.session_state.courts["Court 1"] = []

            for p in players:
                st.session_state.games_played.setdefault(p, 0)

            st.sidebar.success("Pool loaded!")


# =====================================================
# MATCH GENERATOR
# =====================================================

def next_match_normal():
    if len(st.session_state.queue) < 4:
        return []

    match = st.session_state.queue[:4]
    st.session_state.queue = st.session_state.queue[4:] + match
    return match


def next_match_event():
    pool = st.session_state.event_pool
    if len(pool) < 4:
        return []

    match = pool[:4]
    st.session_state.event_pool = pool[4:] + match
    return match


def generate_match():
    if st.session_state.mode == "event":
        return next_match_event()
    else:
        return next_match_normal()


# =====================================================
# COURT UI
# =====================================================

col1, col2 = st.columns([2, 1])

with col1:

    st.subheader("🏟 Court 1")

    if not st.session_state.courts["Court 1"]:
        if st.button("Start Match"):
            st.session_state.courts["Court 1"] = generate_match()

    players = st.session_state.courts["Court 1"]

    if players:
        teamA = players[:2]
        teamB = players[2:]

        st.markdown("### Team A")
        for p in teamA:
            st.write(label(p))

        st.markdown("### Team B")
        for p in teamB:
            st.write(label(p))

        if st.button("Submit Score / Finish Game"):
            for p in players:
                st.session_state.games_played[p] += 1

            st.session_state.courts["Court 1"] = []


# =====================================================
# WAITING QUEUE + SWAP SYSTEM
# =====================================================

with col2:

    st.subheader("⏳ Waiting Queue")

    source = st.selectbox("From", ["Queue", "Court 1"])
    dest = st.selectbox("To", ["Court 1", "Queue"])

    def get_list(name):
        if name == "Queue":
            return st.session_state.queue
        else:
            return st.session_state.courts["Court 1"]

    src_list = get_list(source)
    dst_list = get_list(dest)

    if src_list:
        player = st.selectbox(
            "Select Player",
            src_list,
            key="swap_player"
        )

        if st.button("Swap / Move"):
            src_list.remove(player)
            dst_list.append(player)

    st.divider()

    # display waiting
    if mode == "event":
        display = st.session_state.event_pool
    else:
        display = st.session_state.queue

    for p in display:
        st.write(label(p))


# =====================================================
# EXTRA BUTTONS
# =====================================================

st.sidebar.divider()

if st.sidebar.button("Shuffle Queue"):
    random.shuffle(st.session_state.queue)

if st.sidebar.button("Reset Games"):
    for k in st.session_state.games_played:
        st.session_state.games_played[k] = 0
