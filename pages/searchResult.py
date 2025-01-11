import json
import streamlit as st

st.set_page_config("Filter Results", initial_sidebar_state = "collapsed")

# TODO add "history" feature to save inputted data from previous competitions for future use
# TODO add "crowdsourced" data when accounts are added and it is opened for public use
# TODO change violations from drop down to a new section where you can press a button to add a violation

if "disabled" not in st.session_state:
    st.session_state["disabled"] = False

if "autonDisabled" not in st.session_state:
    st.session_state["autonDisabled"] = False

def disableWidgets(key):
    disabled = st.session_state["disabled"]
    if disabled:
        st.session_state["disabled"] = False
    else:
        st.session_state["disabled"] = True

    saveValue(key)

def disableAutonWidgets(key):
    autonDisabled = st.session_state["autonDisabled"]

    if autonDisabled and not st.session_state[key] == "No Auton":
        st.session_state["autonDisabled"] = False
    elif st.session_state[key] == "No Auton":
        st.session_state["autonDisabled"] = True

    saveValue(key)

def saveValue(key):
    # NOTE: have to truncate match part of key for violations when adding it to values so that it can be added to the list of violations for that team properly
    file = open("values.json", "r")
    data = json.loads(file.read())
    file.close()

    data[key] = st.session_state[key]


    file = open("values.json", "w")
    json.dump(data, file)
    file.close()
    
def saveViolation(key: str):
    file = open("values.json", "r")
    data = json.loads(file.read())
    file.close()

    severity = st.session_state[key + "-severity"]
    notes = st.session_state[key + "-notes"]

    match = key[key.find("Qualifier"):]
    key = key[:key.find("-Qualifier")]

    try:
        data[key].append({"severity" : severity, "notes" : notes, "match" : match})
    except:
        data[key] = []
        data[key].append({"severity" : severity, "notes" : notes, "match" : match})

    file = open("values.json", "w")
    json.dump(data, file)
    file.close()

@st.dialog("Add A Violation")
def addViolationDialog(key):
    st.selectbox("Severity", ["Minor", "Major"], None, key = key + "-severity")
    st.text_input("Violation Notes (Optional)", placeholder = "Type something", key = key + "-notes")

    if st.button("Save Violation", key = key + "saveButton", on_click = lambda key = key: saveViolation(key)):
        st.rerun()

def createSearchPage():
    if "filterData" not in st.session_state:
        st.switch_page("main.py")
        return

    data = st.session_state["filterData"]
    
    title = st.title(data["title"])
    
    file = open("values.json", "r")
    valueData = json.loads(file.read())
    file.close()

    try:
        st.session_state["disabled"] = valueData["Basic Bot-" + data["title"] + "-general"]
    except:
        st.session_state["disabled"] = False

    for i in data["sections"]:
        heading = st.header(i["heading"])
        
        for n in i["inputs"]:
            info = i["inputs"][n]
            type = info["type"]
            disabled = st.session_state["disabled"]

            key = n + "-" + info["key"]

            if disabled == False and n.startswith("Autonomous") and not n == "Autonomous Side":
                disabled = st.session_state["autonDisabled"]

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
                
                if n == "Autonomous Side":
                    st.selectbox(n, info["options"], key = key, disabled = disabled, on_change = lambda key = key : disableAutonWidgets(key), index = value)
                else:
                    st.selectbox(n, info["options"], key = key, disabled = disabled, on_change = lambda key = key : saveValue(key), index = value)

            elif type == "slider":
                st.slider(n, info["range"][0], info["range"][1], step = info["step"], key = key, disabled = disabled, on_change = lambda key = key : saveValue(key), value = value)

            elif type == "violationModule":
                addViolation = st.button("Add a Violation", on_click = lambda key = key: addViolationDialog(key), key = key)
                
                

homeButton = st.button("Home")

if homeButton:
    st.switch_page("main.py")


createSearchPage()