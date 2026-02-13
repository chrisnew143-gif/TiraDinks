import streamlit as st
import random
from collections import deque
import pandas as pd
from itertools import combinations
import json
import os

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(page_title="Pickleball Auto Stack", page_icon="🎾", layout="wide")

st.title("🎾 Pickleball Auto Stack")
st.caption("First come • first play • fair rotation")

# ======================================================
# HELPERS
# ======================================================
def icon(skill):
    return {"BEGINNER":"🟢","NOVICE":"🟡","INTERMEDIATE":"🔴"}[skill]

def superscript_number(n):
    return str(n).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))

# UPDATED for preferred court
def fmt(p):
    name, skill, dupr, pref = p
    games = st.session_state.players.get(name, {}).get("games", 0)
    return f"{icon(skill)} {superscript_number(games)} {name}"

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
    ss.setdefault("locked", {})
    ss.setdefault("scores", {})
    ss.setdefault("history", [])
    ss.setdefault("started", False)
    ss.setdefault("court_count", 2)
    ss.setdefault("players", {})

init()

# ======================================================
# DELETE PLAYER
# ======================================================
def delete_player(name):
    st.session_state.queue = deque([p for p in st.session_state.queue if p[0] != name])

    for cid, teams in st.session_state.courts.items():
        if not teams:
            continue
        new_teams = []
        for team in teams:
            new_teams.append([p for p in team if p[0] != name])

        if len(new_teams[0]) < 2 or len(new_teams[1]) < 2:
            st.session_state.courts[cid] = None
            st.session_state.locked[cid] = False
        else:
            st.session_state.courts[cid] = new_teams

    st.session_state.players.pop(name, None)

# ======================================================
# NEW MATCH ENGINE WITH COURT PREFERENCE
# ======================================================
def take_four_for_court(cid):

    q = list(st.session_state.queue)

    preferred = [p for p in q if p[3] in (None, cid)]

    if len(preferred) < 4:
        return None

    for combo in combinations(range(len(preferred)), 4):
        group = [preferred[i] for i in combo]
        if safe_group(group):
            for g in group:
                q.remove(g)
            st.session_state.queue = deque(q)
            return group

    return None


def start_match(cid):
    if st.session_state.locked[cid]:
        return

    players = take_four_for_court(cid)
    if not players:
        return

    st.session_state.courts[cid] = make_teams(players)
    st.session_state.locked[cid] = True
    st.session_state.scores[cid] = [0, 0]


# ======================================================
# FINISH MATCH
# ======================================================
def finish_match(cid):
    teams = st.session_state.courts[cid]
    if not teams:
        return

    scoreA, scoreB = st.session_state.scores[cid]
    teamA, teamB = teams

    for p in teamA + teamB:
        st.session_state.players[p[0]]["games"] += 1

    players = teamA + teamB
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

# ======================================================
# PROFILE SAVE / LOAD / DELETE
# ======================================================
SAVE_DIR = "profiles"
os.makedirs(SAVE_DIR, exist_ok=True)

def save_profile(name):
    data = dict(st.session_state)
    data["queue"] = list(data["queue"])
    with open(os.path.join(SAVE_DIR, f"{name}.json"), "w") as f:
        json.dump(data, f)
    st.success("Profile saved!")

def load_profile(name):
    path = os.path.join(SAVE_DIR, f"{name}.json")
    with open(path, "r") as f:
        data = json.load(f)
    for k, v in data.items():
        st.session_state[k] = v
    st.session_state.queue = deque(data["queue"])
    st.success("Profile loaded!")

def delete_profile(name):
    os.remove(os.path.join(SAVE_DIR, f"{name}.json"))
    st.success("Profile deleted!")
    st.rerun()

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:

    st.header("⚙ Setup")

    st.session_state.court_count = st.selectbox(
        "Courts", [2,3,4,5,6],
        index=st.session_state.court_count-2
    )

    # ⭐ UPDATED ADD PLAYER FORM
    with st.form("add", clear_on_submit=True):
        name = st.text_input("Name")
        dupr = st.text_input("DUPR ID")
        skill = st.radio("Skill", ["Beginner","Novice","Intermediate"])

        pref = st.selectbox(
            "Preferred Court",
            ["Any"] + list(range(1, st.session_state.court_count+1))
        )

        if st.form_submit_button("Add Player") and name:
            pref_val = None if pref == "Any" else int(pref)
            st.session_state.queue.appendleft((name, skill.upper(), dupr, pref_val))
            st.session_state.players.setdefault(name, {"dupr": dupr, "games":0, "wins":0, "losses":0})

    # Delete player
    if st.session_state.players:
        st.divider()
        remove = st.selectbox("❌ Remove Player", list(st.session_state.players.keys()))
        if st.button("Delete"):
            delete_player(remove)
            st.rerun()

    st.divider()

    st.header("💾 Profiles")
    profile_name = st.text_input("Profile Name")

    if st.button("Save Profile"):
        save_profile(profile_name)

    profiles = [f[:-5] for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
    selected = st.selectbox("Select Profile", [""] + profiles)

    if st.button("Load Profile") and selected:
        load_profile(selected)
        st.rerun()

    if st.button("Delete Profile") and selected:
        delete_profile(selected)
