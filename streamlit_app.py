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

st.markdown("""
<style>
footer {visibility:hidden;}
a[href*="github.com/streamlit"]{display:none!important;}

.court-card{
    padding:14px;
    border-radius:12px;
    background:#f4f6fa;
    margin-bottom:12px;
}
.waiting-box{
    background:#fff3cd;
    padding:10px;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🎾 Pickleball Auto Stack")
st.caption("First come • first play • fair rotation • court preference supported")

# ======================================================
# HELPERS
# ======================================================
def icon(skill):
    return {"BEGINNER":"🟢","NOVICE":"🟡","INTERMEDIATE":"🔴"}[skill]


def superscript_number(n):
    sup_map = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    return str(n).translate(sup_map)


# UPDATED (shows court preference)
def fmt(p):
    name, skill, dupr, pref = p
    games = st.session_state.players.get(name, {}).get("games", 0)
    pref_txt = f" (C{pref})" if pref != 0 else ""
    return f"{icon(skill)} {superscript_number(games)} {name}{pref_txt}"


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
# MATCH ENGINE
# ======================================================

# NEW — preference aware
def take_four_safe_for_court(cid):
    q = list(st.session_state.queue)
    if len(q) < 4:
        return None

    preferred = [p for p in q if p[3] == cid or p[3] == 0]

    source = preferred if len(preferred) >= 4 else q

    for combo in combinations(range(len(source)), 4):
        group = [source[i] for i in combo]
        if safe_group(group):
            for player in group:
                q.remove(player)
            st.session_state.queue = deque(q)
            return group
    return None


def start_match(cid):
    if st.session_state.locked[cid]:
        return

    players = take_four_safe_for_court(cid)
    if not players:
        return

    st.session_state.courts[cid] = make_teams(players)
    st.session_state.locked[cid] = True
    st.session_state.scores[cid] = [0, 0]


def finish_match(cid):
    teams = st.session_state.courts[cid]
    if not teams:
        return

    scoreA, scoreB = st.session_state.scores[cid]
    teamA, teamB = teams

    if scoreA > scoreB:
        winner = "Team A"
        winners, losers = teamA, teamB
    elif scoreB > scoreA:
        winner = "Team B"
        winners, losers = teamB, teamA
    else:
        winner = "DRAW"
        winners = losers = []

    for p in teamA + teamB:
        st.session_state.players[p[0]]["games"] += 1
    for p in winners:
        st.session_state.players[p[0]]["wins"] += 1
    for p in losers:
        st.session_state.players[p[0]]["losses"] += 1

    st.session_state.history.append({
        "Court": cid,
        "Team A": " & ".join(p[0] for p in teamA),
        "Team B": " & ".join(p[0] for p in teamB),
        "Score A": scoreA,
        "Score B": scoreB,
        "Winner": winner
    })

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
# CSV EXPORTS
# ======================================================
def matches_csv():
    if not st.session_state.history:
        return b""
    return pd.DataFrame(st.session_state.history).to_csv(index=False).encode()


def players_csv():
    rows = []
    for name, data in st.session_state.players.items():
        rows.append({
            "Player Name": name,
            "DUPR ID": data["dupr"],
            "Preferred Court": data.get("pref", 0),
            "Games Played": data["games"],
            "Wins": data["wins"],
            "Losses": data["losses"]
        })
    return pd.DataFrame(rows).to_csv(index=False).encode()

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.header("⚙ Setup")

    st.session_state.court_count = st.selectbox(
        "Courts", [2,3,4,5,6],
        index=st.session_state.court_count-2
    )

    # ADD PLAYER (UPDATED)
    with st.form("add", clear_on_submit=True):
        name = st.text_input("Name")
        dupr = st.text_input("DUPR ID")
        skill = st.radio("Skill", ["Beginner","Novice","Intermediate"])

        pref = st.selectbox(
            "Preferred Court",
            ["Any"] + list(range(1, st.session_state.court_count + 1))
        )

        if st.form_submit_button("Add Player") and name:
            pref_val = 0 if pref == "Any" else int(pref)

            st.session_state.queue.appendleft(
                (name, skill.upper(), dupr, pref_val)
            )

            st.session_state.players.setdefault(
                name,
                {"dupr":dupr,"games":0,"wins":0,"losses":0,"pref":pref_val}
            )

    # START
    if st.button("🚀 Start Games"):
        st.session_state.started = True
        st.session_state.courts = {i:None for i in range(1, st.session_state.court_count+1)}
        st.session_state.locked = {i:False for i in st.session_state.courts}
        st.session_state.scores = {i:[0,0] for i in st.session_state.courts}
        st.rerun()

# ======================================================
# MAIN
# ======================================================
auto_fill()

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
# COURTS
# ======================================================
st.divider()
st.subheader("🏟 Live Courts")

cols = st.columns(2)

for i, cid in enumerate(st.session_state.courts):
    with cols[i % 2]:
        st.markdown('<div class="court-card">', unsafe_allow_html=True)

        st.markdown(f"### Court {cid}")
        teams = st.session_state.courts[cid]

        if not teams:
            st.info("Waiting for safe players...")
            st.markdown('</div>', unsafe_allow_html=True)
            continue

        st.write("**Team A**  \n" + " & ".join(fmt(p) for p in teams[0]))
        st.write("**Team B**  \n" + " & ".join(fmt(p) for p in teams[1]))

        st.divider()

        a, b = st.session_state.scores[cid]
        a = st.number_input("Score A", 0, key=f"A_{cid}", value=a)
        b = st.number_input("Score B", 0, key=f"B_{cid}", value=b)

        if st.button("✅ Submit Score", key=f"submit_{cid}"):
            st.session_state.scores[cid] = [a, b]
            finish_match(cid)
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
