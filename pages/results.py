import streamlit as st
import data as dataModule
import json

st.set_page_config("Display Results")\

st.title("Results")
st.warning("All results were calculated based off of values that were either manually inputted or automatically gathered from the robotevents.com API.  These rankings should not be used as the only metric for determining which teams you choose to form an alliance with during elimination rounds, as the values are subjective and are based on unofficial calculations.")

dataModule.calculateResults()

file = open("results.json", "r")
data = json.loads(file.read())
file.close()

ranks = []

for i in data:
    ranks.append(i)

for n in range(len(ranks) - 1, 0, -1):
    swapped = False

    for i in range(n):
        if data[ranks[i]]["percentage"] > data[ranks[i + 1]]["percentage"]:
            ranks[i], ranks[i + 1] = ranks[i + 1], ranks[i]

            swapped = True
        
    if not swapped:
        break

ranks.reverse()

for i in data:
    data[i]["rank"] = ranks.index(i) + 1

for i in ranks:
    teamResult = st.expander(f"{i} - Rank #{data[i]["rank"]} ({data[i]["percentage"]}%)")
    if data[i]["disqualified"]:
        teamResult.warning("This team was \"disqualified\" from the rankings for: " + data[i]["dqReason"])

    
    

    
