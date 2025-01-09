import json
import streamlit as st
import data as dataModule

# store filters as session states when button is pressed since that is unique to device
# then here grab those session states, feed it to the filterInputs functions, take that output data, and create the page here
# should make it unique to each device in a pretty simple way

st.set_page_config("Filter Results", initial_sidebar_state = "collapsed")

def createSearchPage():
    filterInfo = st.session_state["filters"]

    data = dataModule.filterInputs(filterInfo[0], filterInfo[1])

    if data["popup"] != None:
        st.write(f":red[{data["popup"]}]")
        return
    
    title = st.title(data["title"])

    # TODO 1st priority should be working on the page system (switching to page and then displaying on correct page), worry about page generation after

    # after page generation is done, redirect to the website/search page