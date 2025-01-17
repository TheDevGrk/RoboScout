import streamlit as st
import json
import ast
import data
from multiprocessing.pool import ThreadPool


st.set_page_config("Search")

pool = ThreadPool(processes=2)

pool.apply_async(data.refreshData)

display = st.button("Display Results")
if display:
    st.switch_page("pages/results.py")


@st.fragment(run_every="25s")
def refreshInfo():
    file = open("teamInfo.json", "r")
    teamInfo = json.load(file)
    file.close()

    file = open("matches.txt", "r")
    matches = file.read()
    file.close()
    
    st.session_state["teamInfo"] = teamInfo
    st.session_state["matches"] = ast.literal_eval(matches)

@st.fragment(run_every = "25s")
def refreshFilters():
    teams = []
    for i in st.session_state["teamInfo"]:
        teams.append(i)

    st.title("Filter Inputs")

    team = st.selectbox("Filter by Team", teams, index = None)
    match = st.selectbox("Filter by Match", st.session_state["matches"], index = None)

    searchButton = st.button("Search")

    if searchButton:
        filterData = data.filterInputs(team, match)

        if filterData["popup"] != None:
            st.write(f":red[{filterData["popup"]}]")

        else:
            st.session_state["filterData"] = filterData
            st.switch_page("pages/searchResult.py")

refreshInfo()
refreshFilters()