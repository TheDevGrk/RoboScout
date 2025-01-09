import json
import streamlit as st

st.set_page_config("Filter Results", initial_sidebar_state = "collapsed")

if "disabled" not in st.session_state:
    st.session_state["disabled"] = False

def disableWidgets():
    disabled = st.session_state["disabled"]
    if disabled:
        st.session_state["disabled"] = False
    else:
        st.session_state["disabled"] = True


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
            disabled = st.session_state["disabled"]

            try:
                key = n + "-" + info["key"]
            except:
                key = n

            if type == "checkbox":
                if n == "Basic Bot":
                    st.checkbox(n, key = key, on_change = disableWidgets)
                else:
                    st.checkbox(n, key = key, disabled = disabled)

            elif type == "selectbox":
                st.selectbox(n, info["options"], key = key, disabled = disabled)

            elif type == "slider":
                st.slider(n, info["range"][0], info["range"][1], step = info["step"], key = key, disabled = disabled)



createSearchPage()