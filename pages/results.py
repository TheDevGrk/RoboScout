import streamlit as st
import data as dataModule
import json

st.set_page_config("Display Results")

st.title("Results")
homeButton = st.button("Home")

if homeButton:
    st.switch_page("main.py")
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
    if data[i]["disqualified"]:
        teamResult = st.expander(f"{i} - Rank #{data[i]["rank"]} ({data[i]["percentage"]}%) |       Warning: This team was disqualified from the Scouting Rankings and their score may be highly inaccurate!")
    else:
        teamResult = st.expander(f"{i} - Rank #{data[i]["rank"]} ({data[i]["percentage"]}%)")

    if data[i]["disqualified"]:
        teamResult.error("This team was \"disqualified\" from the Scouting Rankings for: " + data[i]["dqReason"] + ".  Be cautious when selecting this team, their score could be highly inaccurate.")

    teamResult.write(f"**Scout Score**: {data[i]["score"]} out of {data[i]["possible"]}")

    teamResult.write(f"**Basic Bot**: {data[i]["Basic Bot"]}")
    teamResult.write(f"**State Qualified**: {data[i]["State Qualified"]}")
    teamResult.write(f"**Autonomous Side**: {data[i]["Autonomous Side"]}")
    teamResult.write(f"**Autonomous Scoring Capabilities (Points)**: {data[i]["Autonomous Scoring Capabilities (Points)"]}")


    if data[i]["Autonomous Tasks Able to be Completed"] == "Data Not Provided":
            teamResult.write(f"**Autonomous Tasks Able to be Completed**: Data Not Provided")
    else:
        teamResult.write(f"**Autonomous Tasks Able to be Completed**: ")
        for n in data[i]["Autonomous Tasks Able to be Completed"]:
            teamResult.write("  - " + n)
        st.markdown('''
    <style>
    [data-testid="stMarkdownContainer"] ul{
        list-style-position: inside;
    }
    </style>
    ''', unsafe_allow_html=True)
        
    teamResult.write(f"**Can Score on Wall Stakes**: {data[i]["Can Score on Wall Stakes"]}")
    teamResult.write(f"**Can Score on High Stake**: {data[i]["Can Score on High Stake"]}")
    teamResult.write(f"**Elevation Level**: {data[i]["Elevation Level"]}")
    teamResult.write(f"**Scoring Success Rate (%)**: {data[i]["Scoring Success Rate (%)"]}")
    teamResult.write(f"**Robo Speed (RPM)**: {data[i]["Robo Speed (RPM)"]}")
    teamResult.write(f"**Mobile Goal Moving Capabilities (Grip Strength)**: {data[i]["Mobile Goal Moving Capabilities (Grip Strength)"]}")
    teamResult.write(f"**Potential to be Bullied (Estimated Weight in Pounds)**: {data[i]["Potential to be Bullied (Estimated Weight in Pounds)"]}")
    teamResult.write(f"**W/L Ratio**: {data[i]["W/L Ratio"]}")
    teamResult.write(f"**Best Autonomous Skills Run Score**: {data[i]["Best Autonomous Skills Run Score"]}")
    teamResult.write(f"**Best Driver Skills Run Score**: {data[i]["Best Driver Skills Run Score"]}")
    teamResult.write(f"**Autonomous Skills Rank**: {data[i]["Autonomous Skills Rank"]}")
    teamResult.write(f"**Driver Skills Rank**: {data[i]["Driver Skills Rank"]}")





    
    
    
    

    
