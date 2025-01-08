from multiprocessing.pool import ThreadPool
import data
import streamlit as st
import streamlit_modal as modal
import json
import time
import datetime
import ast
import pageCreator


pool = ThreadPool(processes=2)

states = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", 
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", 
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", 
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", 
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", 
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", 
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", 
    "Wisconsin", "Wyoming"]

countries = countries = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", 
    "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", 
    "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", 
    "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", 
    "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", 
    "Comoros", "Congo, Democratic Republic of the", "Congo, Republic of the", "Costa Rica", 
    "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", 
    "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", 
    "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", 
    "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", 
    "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", 
    "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea, North", 
    "Korea, South", "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", 
    "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", 
    "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", 
    "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", 
    "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", 
    "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama", 
    "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", 
    "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", 
    "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", 
    "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", 
    "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", 
    "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", 
    "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", 
    "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", 
    "Vietnam", "Yemen", "Zambia", "Zimbabwe"]

validCharacters = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

# pool.apply_async(data.refreshData)

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

def searchEvents(startDate, endDate, country, state, teamNumber):
    pool.apply_async(data.findEvents, (startDate, endDate, country, state, teamNumber))

def search(team, match):
    st.session_state["filters"] = [team, match]
    pageCreator.createSearchPage()

@st.fragment(run_every = "25s")
def refreshFilters():
    teams = []
    for i in st.session_state["teamInfo"]:
        teams.append(i)

    st.title("Filter Inputs")

    team = st.selectbox("Filter by Team", ["Select a Team"] + teams)
    match = st.selectbox("Filter by Match", ["Select a Match"] + st.session_state["matches"])

    searchButton = st.button("Search", on_click = search, args = (team, match))

    data.filterInputs(team, match)

refreshInfo()
refreshFilters()

# startDate = st.date_input("Filter by start date", datetime.date(2020, 1, 1))
# endDate = st.date_input("Filter by end date")

# country = st.selectbox("Filter by Country", countries, index = countries.index("United States"), placeholder = "Choose a Country")
# state = st.selectbox("Filter by State (US Only)", ["N/A"] + states, placeholder = "Choose a State")

# teamFilter = st.text_input("Filter by Team Number (Optional)", value = "N/A", placeholder = "Type a team number (Ex. 123A)")

# for i in teamFilter:
#     if i not in validCharacters:
#         teamFilter = teamFilter.replace(i, "")

# if teamFilter == "":
#     teamFilter = "N/A"

# st.selectbox("Event", ["Test1", "Test2"])

# searchButton = st.button("Find Events", on_click = search, args = (startDate, endDate, country, state, teamFilter))