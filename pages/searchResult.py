import json
import streamlit as st
import data as dataModule

# store filters as session states when button is pressed since that is unique to device
# then here grab those session states, feed it to the filterInputs functions, take that output data, and create the page here
# should make it unique to each device in a pretty simple way

st.set_page_config("Filter Results", initial_sidebar_state = "collapsed")

def createSearchPage():
    if "filterData" not in st.session_state:
        return

    data = st.session_state["filterData"]
    
    title = st.title(data["title"])

    for i in data["sections"]:
        heading = st.header(i["heading"])
        
        for n in i["inputs"]:
            info = i["inputs"][n]
            type = info["type"]

            if type == "checkbox":
                st.checkbox(n)

            elif type == "selectbox":
                st.selectbox(n, info["options"])

            elif type == "slider":
                st.slider(n, info["range"][0], info["range"][1], step = info["step"])

    # TODO 1st priority should be working on the page system (switching to page and then displaying on correct page), worry about page generation after

    # after page generation is done, redirect to the website/search page


createSearchPage()