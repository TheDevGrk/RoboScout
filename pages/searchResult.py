import json
import streamlit as st

st.set_page_config("Filter Results", initial_sidebar_state = "collapsed")

# TODO disable rest of auton fields if "No Auton" is selected in auto side select menu

if "disabled" not in st.session_state:
    st.session_state["disabled"] = False

def disableWidgets(key):
    disabled = st.session_state["disabled"]
    if disabled:
        st.session_state["disabled"] = False
    else:
        st.session_state["disabled"] = True

    saveValue(key)

def saveValue(key):
    file = open("values.json", "r")
    data = json.loads(file.read())
    file.close()

    data[key] = st.session_state[key]


    file = open("values.json", "w")
    json.dump(data, file)
    file.close()

    
    

def createSearchPage():
    if "filterData" not in st.session_state:
        st.switch_page("main.py")
        return

    data = st.session_state["filterData"]
    
    title = st.title(data["title"])

    for i in data["sections"]:
        heading = st.header(i["heading"])
        
        for n in i["inputs"]:
            info = i["inputs"][n]
            type = info["type"]
            disabled = st.session_state["disabled"]

            key = n + "-" + info["key"]

            file = open("values.json", "r")
            data = json.loads(file.read())
            file.close()

            try:
                value = data[key]
            except:
                value = None

            if type == "checkbox":
                if value == None:
                    value = False

                if n == "Basic Bot":
                    st.checkbox(n, key = key, on_change = lambda key = key : disableWidgets(key), value = value)
                else:
                    st.checkbox(n, key = key, disabled = disabled, on_change = lambda key = key : saveValue(key), value = value)

            elif type == "selectbox":
                if value != None:
                    value = info["options"].index(value)

                st.selectbox(n, info["options"], key = key, disabled = disabled, on_change = lambda key = key : saveValue(key), index = value)

            elif type == "slider":
                st.slider(n, info["range"][0], info["range"][1], step = info["step"], key = key, disabled = disabled, on_change = lambda key = key : saveValue(key), value = value)

homeButton = st.button("Home")

if homeButton:
    st.switch_page("main.py")


createSearchPage()