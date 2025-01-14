import streamlit as st
import json
import data

st.set_page_config("Search")

display = st.button("Display Results")
if display:
    st.switch_page("pages/results.py")


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

refreshFilters()