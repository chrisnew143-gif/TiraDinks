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
        st.session_state.queue = []

    if "courts" not in st.session_state:
        st.session_state.courts = []

init()


# =====================================================
# CONFIG
# =====================================================
SKILLS = ["Beginner", "Novice", "Intermediate"]

ICON = {
    "Beginner": "🟢",
    "Novice": "🟡",
    "Intermediate": "🔴"
}

LEVEL = {
    "Beginner": 1,
    "Novice": 2,
    "Intermediate": 3
}


# =====================================================
# HELPERS
# =====================================================
def show(p):
    return f'{ICON[p["skill"]]} {p["name"]}'


def safe_group(players):
    skills = {p["skill"] for p in players}
    return not ("Beginner" in skills and "Intermediate" in skills)


# -----------------------------------------------------
# ⭐ Balanced teams (NO mutation)
# -----------------------------------------------------
def build_balanced(group):

    ordered = sorted(group, key=lambda x: LEVEL[x["skill"]], reverse=True)

    teamA = [ordered[0], ordered[3]]
    teamB = [ordered[1], ordered[2]]

    random.shuffle(teamA)
    random.shuffle(teamB)

    # IMPORTANT: return COPIES
    return list(teamA), list(teamB)


# -----------------------------------------------------
# Mix skills fairly
# -----------------------------------------------------
def mix_by_skill(players):

    buckets = {s: [] for s in SKILLS}

    for p in players:
        buckets[p["skill"]].append(p)

    for b in buckets.values():
        random.shuffle(b)

    mixed = []
    while any(buckets.values()):
        for s in SKILLS:
            if buckets[s]:
                mixed.append(buckets[s].pop())

    return mixed


# =====================================================
# START GAMES (build courts once only)
# =====================================================
def start_games():

    players = mix_by_skill(st.session_state.queue.copy())

    new_courts = []
    remaining = players.copy()

    while len(remaining) >= 4:

        group = remaining[:4]

        if not safe_group(group):
            random.shuffle(remaining)
            continue

        teamA, teamB = build_balanced(group)

        new_courts.append({
            "A": teamA.copy(),
            "B": teamB.copy()
        })

        remaining = remaining[4:]

    st.session_state.courts = new_courts
    st.session_state.queue = remaining


# =====================================================
# ⭐ FIXED FINISH MATCH (NO SHARED LISTS)
# =====================================================
def finish_match(idx, winner):

    court = st.session_state.courts[idx]

    winners = list(court[winner])   # COPY
    losers = list(court["A" if winner == "B" else "B"])

    # winners first then losers
    st.session_state.queue.extend(winners + losers)

    # build NEW court object (not mutate old one)
    if len(st.session_state.queue) >= 4:

        group = [st.session_state.queue.pop(0) for _ in range(4)]

        teamA, teamB = build_balanced(group)

        st.session_state.courts[idx] = {
            "A": teamA.copy(),
            "B": teamB.copy()
        }

    else:
        st.session_state.courts[idx] = {
            "A": [],
            "B": []
        }


def go_home():
    st.session_state.page = "home"


# =====================================================
# HOME
# =====================================================
if st.session_state.page == "home":

    st.title("🎾 Pickleball Stack App")

    c1, c2 = st.columns(2)

    if c1.button("🏟 Organizer", use_container_width=True):
        st.session_state.page = "organizer"

    if c2.button("👤 Player", use_container_width=True):
        st.session_state.page = "player"


# =====================================================
# PLAYER
# =====================================================
elif st.session_state.page == "player":

    st.button("⬅ Back Home", on_click=go_home)

    st.title("Join Queue")

    name = st.text_input("Name")
    skill = st.selectbox("Skill", SKILLS)

    if st.button("Join") and name:
        st.session_state.queue.append({"name": name, "skill": skill})


# =====================================================
# ORGANIZER
# =====================================================
elif st.session_state.page == "organizer":

    st.button("⬅ Back Home", on_click=go_home)

    st.title("🏟 Pickleball Auto Stack")

    # ---------------- sidebar
    with st.sidebar:

        name = st.text_input("Name")
        skill = st.selectbox("Skill", SKILLS, key="s")

        if st.button("Add") and name:
            st.session_state.queue.append({"name": name, "skill": skill})

        st.divider()

        if st.button("Start Games"):
            start_games()

    # ---------------- queue
    st.subheader("⏳ Waiting Queue")

    if st.session_state.queue:
        st.write(", ".join(show(p) for p in st.session_state.queue))
    else:
        st.success("No players waiting 🎉")

    st.divider()

    # ---------------- courts
    st.subheader("🏟 Live Courts")

    if not st.session_state.courts:
        st.info("Press Start Games")

    for i, court in enumerate(st.session_state.courts):

        with st.container(border=True):

            st.markdown(f"### Court {i+1}")

            c1, c2, c3 = st.columns([3, 3, 2])

            with c1:
                st.write("**Team A**")
                for p in court["A"]:
                    st.write(show(p))

            with c2:
                st.write("**Team B**")
                for p in court["B"]:
                    st.write(show(p))

            with c3:
                if st.button("Winner A", key=f"A{i}"):
                    finish_match(i, "A")

                if st.button("Winner B", key=f"B{i}"):
                    finish_match(i, "B")
