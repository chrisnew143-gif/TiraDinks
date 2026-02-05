import streamlit as st
import random

st.set_page_config(page_title="Pickleball Auto Stack", layout="wide")

# =====================================================
# INIT STATE
# =====================================================
def init():
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if "queue" not in st.session_state:
        st.session_state.queue = []  # [{name, skill}]

    if "courts" not in st.session_state:
        st.session_state.courts = []

init()


# =====================================================
# SKILL RULES
# =====================================================

SKILLS = ["Beginner", "Novice", "Intermediate"]

ICON = {
    "Beginner": "🟢",
    "Novice": "🔵",
    "Intermediate": "🔴"
}


def display_player(p):
    return f'{ICON[p["skill"]]} {p["name"]}'


# -----------------------------------------------------
# RULE:
# Beginner + Intermediate NOT allowed
# -----------------------------------------------------
def safe_group(players):
    skills = {p["skill"] for p in players}
    if "Beginner" in skills and "Intermediate" in skills:
        return False
    return True


# -----------------------------------------------------
# MIX PLAYERS BY SKILL
# -----------------------------------------------------
def mix_by_skill(players):

    groups = {s: [] for s in SKILLS}

    for p in players:
        groups[p["skill"]].append(p)

    for g in groups.values():
        random.shuffle(g)

    mixed = []

    # round robin
    while any(groups.values()):
        for s in SKILLS:
            if groups[s]:
                mixed.append(groups[s].pop())

    return mixed


# -----------------------------------------------------
# CREATE COURTS SAFELY
# -----------------------------------------------------
def start_games():

    players = mix_by_skill(st.session_state.queue.copy())

    courts = []
    remaining = players.copy()

    while len(remaining) >= 4:

        found = False

        # try few small shuffles only
        for _ in range(10):
            group = remaining[:4]

            if safe_group(group):
                teamA = [group[0], group[1]]
                teamB = [group[2], group[3]]

                courts.append({"A": teamA, "B": teamB})

                remaining = remaining[4:]
                found = True
                break
            else:
                random.shuffle(remaining)

        if not found:
            break

    st.session_state.courts = courts
    st.session_state.queue = remaining


# -----------------------------------------------------
# FINISH MATCH
# Winner stays, losers rotate to queue
# -----------------------------------------------------
def finish_match(court_index, winner):

    court = st.session_state.courts[court_index]

    winners = court[winner]
    losers = court["A" if winner == "B" else "B"]

    # winners stay first in queue
    st.session_state.queue.extend(winners + losers)

    # refill court
    if len(st.session_state.queue) >= 4:
        new_group = []

        for _ in range(4):
            new_group.append(st.session_state.queue.pop(0))

        court["A"] = new_group[:2]
        court["B"] = new_group[2:]

    st.session_state.courts[court_index] = court


def go_home():
    st.session_state.page = "home"


# =====================================================
# HOME PAGE
# =====================================================
if st.session_state.page == "home":

    st.title("🎾 Pickleball Stack App")

    c1, c2 = st.columns(2)

    if c1.button("🏟 Organizer", use_container_width=True):
        st.session_state.page = "organizer"

    if c2.button("👤 Player", use_container_width=True):
        st.session_state.page = "player"


# =====================================================
# PLAYER PAGE
# =====================================================
elif st.session_state.page == "player":

    st.button("⬅ Back Home", on_click=go_home)

    st.title("👤 Join Queue")

    name = st.text_input("Your name")

    skill = st.selectbox("Skill", SKILLS)

    if st.button("Join"):
        if name:
            st.session_state.queue.append({
                "name": name,
                "skill": skill
            })
            st.success("Added to queue!")


# =====================================================
# ORGANIZER PAGE
# =====================================================
elif st.session_state.page == "organizer":

    st.button("⬅ Back Home", on_click=go_home)

    st.title("🏟 Pickleball Auto Stack")

    # -----------------
    # SIDEBAR
    # -----------------
    with st.sidebar:

        st.subheader("Add Player")

        name = st.text_input("Name")
        skill = st.selectbox("Skill", SKILLS, key="side")

        if st.button("Add"):
            if name:
                st.session_state.queue.append({
                    "name": name,
                    "skill": skill
                })

        st.divider()

        if st.button("Start Games"):
            start_games()

    # -----------------
    # QUEUE
    # -----------------
    st.subheader("⏳ Waiting Queue")

    if st.session_state.queue:
        st.write(", ".join(display_player(p) for p in st.session_state.queue))
    else:
        st.success("No players waiting 🎉")

    st.divider()

    # -----------------
    # COURTS
    # -----------------
    st.subheader("🏟 Live Courts")

    if not st.session_state.courts:
        st.info("Press Start Games")
    else:
        for i, court in enumerate(st.session_state.courts):

            with st.container(border=True):

                st.markdown(f"### Court {i+1}")

                c1, c2, c3 = st.columns([3, 3, 2])

                with c1:
                    st.write("**Team A**")
                    for p in court["A"]:
                        st.write(display_player(p))

                with c2:
                    st.write("**Team B**")
                    for p in court["B"]:
                        st.write(display_player(p))

                with c3:
                    if st.button("Winner A", key=f"A{i}"):
                        finish_match(i, "A")

                    if st.button("Winner B", key=f"B{i}"):
                        finish_match(i, "B")
