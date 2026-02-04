import streamlit as st
import random

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="TiraDinks Pickleball",
    page_icon="🎾",
    layout="wide"
)

# ======================================================
# SESSION STATE INIT
# ======================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "waiting_players" not in st.session_state:
    st.session_state.waiting_players = []

if "courts" not in st.session_state:
    st.session_state.courts = []


# ======================================================
# HELPERS
# ======================================================

def go_home():
    st.session_state.page = "home"


def go_organizer():
    st.session_state.page = "organizer"


def go_player():
    st.session_state.page = "player"


def add_player(name):
    name = name.strip().lower()

    if name and name not in st.session_state.waiting_players:
        st.session_state.waiting_players.append(name)


# 🔥 FIFO SAFE (fixes your bug)
def start_games():
    queue = st.session_state.waiting_players

    while len(queue) >= 4:
        players = [queue.pop(0) for _ in range(4)]
        random.shuffle(players)

        court = {
            "team_a": players[:2],
            "team_b": players[2:]
        }

        st.session_state.courts.append(court)


def winners_stay(court_index):
    court = st.session_state.courts[court_index]

    winners = court["team_a"]
    losers = court["team_b"]

    st.session_state.waiting_players.extend(losers)
    st.session_state.courts.pop(court_index)


def rotate_all():
    for court in st.session_state.courts:
        st.session_state.waiting_players.extend(
            court["team_a"] + court["team_b"]
        )

    st.session_state.courts = []


# ======================================================
# HOME PAGE
# ======================================================

def home_page():
    st.title("🎾 TiraDinks Pickleball")
    st.subheader("Choose your role")

    col1, col2 = st.columns(2)

    with col1:
        st.button(
            "🎾 Organizer",
            use_container_width=True,
            on_click=go_organizer
        )

    with col2:
        st.button(
            "🙋 Player",
            use_container_width=True,
            on_click=go_player
        )


# ======================================================
# PLAYER PAGE
# ======================================================

def player_page():
    st.title("🙋 Player Check-in")

    name = st.text_input("Enter your name")

    st.button("Join Queue", on_click=lambda: add_player(name))

    st.divider()

    st.subheader("⏳ Waiting Queue")

    if st.session_state.waiting_players:
        for p in st.session_state.waiting_players:
            st.write(f"🟢 {p}")
    else:
        st.success("No players waiting 🎉")

    st.divider()
    st.button("⬅ Back Home", on_click=go_home)


# ======================================================
# ORGANIZER PAGE
# ======================================================

def organizer_page():
    st.title("🎾 Pickleball Auto Stack")
    st.caption("First come, first play • Fair rotation")

    col1, col2 = st.columns(2)

    with col1:
        st.button("▶ Start Games", on_click=start_games)

    with col2:
        st.button("🔄 Rotate All", on_click=rotate_all)

    st.divider()

    # --------------------
    # WAITING QUEUE
    # --------------------
    st.subheader("⏳ Waiting Queue")

    if st.session_state.waiting_players:
        st.write(", ".join(f"🟢 {p}" for p in st.session_state.waiting_players))
    else:
        st.success("No players waiting 🎉")

    st.divider()

    # --------------------
    # COURTS
    # --------------------
    st.subheader("🏟 Live Courts")

    if not st.session_state.courts:
        st.info("No active games yet")
    else:
        for i, court in enumerate(st.session_state.courts):
            st.markdown(f"### Court {i+1}")

            colA, colB = st.columns(2)

            with colA:
                st.write("Team A")
                st.write(" & ".join(f"🟢 {p}" for p in court["team_a"]))

            with colB:
                st.write("Team B")
                st.write(" & ".join(f"🟢 {p}" for p in court["team_b"]))

            st.button(
                f"🏆 Team A Won (Court {i+1})",
                key=f"win_{i}",
                on_click=winners_stay,
                args=(i,)
            )

            st.divider()

    st.button("⬅ Back Home", on_click=go_home)


# ======================================================
# ROUTER
# ======================================================

if st.session_state.page == "home":
    home_page()

elif st.session_state.page == "organizer":
    organizer_page()

elif st.session_state.page == "player":
    player_page()
