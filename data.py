from dotenv import load_dotenv
import os
import time
import json
import datetime
import requests

load_dotenv()

token = os.getenv("token")
email = os.getenv("email")
password = os.getenv("password")
bravePath = os.getenv("bravePath")
driverPath = os.getenv("driverPath")
eventSku = os.getenv("eventSku")

file = open("token.txt", "r")
token = file.read()
file.close()

headers = {
    "Authorization" : "Bearer " + token
}

def getURL(url):
    response = requests.get(url, headers = headers)

    print(response.status_code)

    if response.status_code != 200:
        print(url)
    return response.json()

def fetchEventData(eventSku : str):
    eventURL = f"https://www.robotevents.com/api/v2/events?sku%5B%5D={eventSku}&myEvents=false"

    eventData = getURL(eventURL)
    time.sleep(1)

    eventID = eventData["data"][0]["id"]
    teamsURL = f"https://www.robotevents.com/api/v2/events/{eventID}/teams"

    teamsData = getURL(teamsURL)

    time.sleep(1)

    pageNum = teamsData["meta"]["last_page"]

    teamsData = teamsData["data"]

    if pageNum > 1:
        for i in range(2, pageNum + 1):
            teamsData = teamsData + getURL(teamsURL + f"?page={i}")["data"]

    
    teamInfo = {}

    for i in teamsData:
        skillsURL = f"https://www.robotevents.com/api/v2/teams/{i["id"]}/skills?per_page=500"

        skillsData = getURL(skillsURL)["data"]

        autonSkills = 0
        driverSkills = 0
        autonSkillsRank = 1
        driverSkillsRank = 1

        for n in skillsData:
            if n["season"]["id"] == 190:
                if n["type"] == "programming":
                    if n["rank"] != autonSkillsRank and n["event"]["id"] == eventID:
                        autonSkillsRank = n["rank"]
                    elif n["score"] > autonSkills:
                        autonSkills = n["score"]

                elif n["type"] == "driver":
                    if n["rank"] != driverSkillsRank and n["event"]["id"] == eventID:
                        driverSkillsRank = n["rank"]
                    elif n["score"] > driverSkills:
                        driverSkills = n["score"]

        skills = {"auton" : autonSkills, "autonRank" : autonSkillsRank, "driver" : driverSkills, "driverRank" : driverSkillsRank}

        print(i["number"])

        matchesURL = f"https://www.robotevents.com/api/v2/teams/{i["id"]}/matches?per_page=1000"

        matchesData = getURL(matchesURL)

        pageNum = matchesData["meta"]["last_page"]

        matchesData = matchesData["data"]

        if pageNum > 1:
            for n in range(2, pageNum + 1):
                matchesData = matchesData + getURL(matchesURL + f"?page={n}")["data"]

        matches = {}

        for n in matchesData:
            if n["event"]["code"] == eventSku:
                teams = {}

                blue = n["alliances"][0]["teams"]
                red = n["alliances"][1]["teams"]

                # Checks which alliance the team is a part of and adds their team number first and then their alliance's team number

                if (blue[0]["team"]["name"] == i["number"]):
                    teams["alliance"] = [i["number"], blue[1]["team"]["name"], "Blue", n["alliances"][0]["score"]]

                elif (blue[1]["team"]["name"] == i["number"]):
                    teams["alliance"] = [i["number"], blue[0]["team"]["name"], "Blue", n["alliances"][0]["score"]]

                elif (red[0]["team"]["name"] == i["number"]):
                    teams["alliance"] = [i["number"], red[1]["team"]["name"], "Red", n["alliances"][1]["score"]]

                elif (red[1]["team"]["name"] == i["number"]):
                    teams["alliance"] = [i["number"], red[0]["team"]["name"], "Red", n["alliances"][1]["score"]]
                

                if teams["alliance"][2] == "Blue":
                    teams["opponents"] = [red[0]["team"]["name"], red[1]["team"]["name"], "Red", n["alliances"][1]["score"]]
                
                else:
                    teams["opponents"] = [blue[0]["team"]["name"], blue[1]["team"]["name"], "Blue", n["alliances"][0]["score"]]

                result = ""

                if teams["alliance"][3] > teams["opponents"][3]:
                    result = "Win"
                elif teams["alliance"][3] < teams["opponents"][3]:
                    result = "Loss"
                elif teams["alliance"][3] == teams["opponents"][3]:
                    result = "Tie"
                else:
                    result = "Invalid Match Result"

                matches[n["name"]] = {"teams" : teams, "result" : result}

        teamInfo[i["number"]] = {"name" : i["team_name"], "organization" : i["organization"], "id" : i["id"],
                                    "skills" : skills, "matches" : matches}
        
        time.sleep(3)
        
    rankingsURL = f"https://www.robotevents.com/api/v2/events/{eventID}/divisions/1/rankings?per_page=100"

    rankingsData = getURL(rankingsURL)["data"]

    rank = 1
    results = {}

    for i in rankingsData:
            rank = i["rank"]
            results["wins"] = i["wins"]
            results["losses"] = i["losses"]
            results["ties"] = i["ties"]

            info = teamInfo[i["team"]["name"]]
            info["rank"] = rank
            info["results"] = results

            teamInfo[i["team"]["name"]] = info

    matchURL = f"https://www.robotevents.com/api/v2/events/{eventID}/divisions/1/matches?per_page=100"

    matchData = getURL(matchURL)["data"]

    match = []

    for i in matchData:
        if str(i["name"]).startswith("Qualifier"):
            match.append(i["name"])  

    return [teamInfo, eventID, match]

def refreshData():
    while True:
        data = fetchEventData(eventSku)

        global globalEventID

        teamInfo = data[0]
        globalEventID = data[1]
        matches = data[2]

        file = open("teamInfo.json", "w")
        json.dump(teamInfo, file)
        file.close()

        print(1)

        file = open("matches.txt", "w")
        file.write(str(matches))
        file.close()
        
        time.sleep(600)

def findTeam(number : str):
    returnValue = {}
    findTeamURL = f"https://www.robotevents.com/api/v2/teams?number%5B%5D={number}"

    teamData = getURL(findTeamURL)["data"]

    if teamData != []:
        returnValue = {"id" : teamData["id"], "number" : teamData["number"], "name" : teamData["team_name"], "organization" : teamData["organization"]}
    else:
        returnValue = None

        return returnValue

def findEvents(startDate : datetime.date = datetime.date(2020, 1, 1),
                endDate : datetime.date = datetime.date.today(),
                country : str = "United States", state : str = "N/A",
                teamNumber : str = "N/A"):
    
    region = ""

    if country != "United States" or (country == "United States" and state == "N/A"):
        region = country
    else:
        region = state

    findEventsURL = f"https://www.robotevents.com/api/v2/events?start={startDate}&end={endDate}&region={region}"

    if teamNumber != "N/A":
        teamData = findTeam(teamNumber)
        findEventsURL = findEventsURL + f"team%5B%5D={teamData["id"]}"

        eventData = getURL(findEventsURL)["data"]   

def filterInputs(team, match):

    # output = {"popup" : None, "title" : None, "subtitle" : None, "inputs" : {}}

    output = {"popup" : None, "title" : None, "sections" : []}

    def addSection(heading: str, inputs: dict):
        output["sections"].append({
            "heading" : heading,
            "inputs" : inputs
        })    


    file = open("teamInfo.json", "r")
    teamInfo = json.load(file)
    file.close()

    if team == "Select a Team":
        team = None
    if match == "Select a Match":
        match = None
    
    if match == None and team == None:
        output["popup"] = "You must choose some filters!"
    
    elif match != None and team!= None:

        for i in teamInfo:

            if i == team:

                matchFound = False

                for n in teamInfo[i]["matches"]:
                    if n == match:
                        matchFound = True
                        matchInfo = team[i]["matches"][n]
                        break
                
                if matchFound == False:
                    output["popup"] = f"{team} was not in {match}"

                else:
                    output["title"] = team

                    inputs = {}
                    
                    inputs["Carried Status"] = {"type" : "selectbox", "options" : ["Neither team was carried.", "Yes, got carried.", "No, carried the other team."]}
                    
                    inputs["Violations"] = {"type" : "selectbox", "options" : ["None", "Minor", "Major"]}

                    inputs["Driving Skills Rating"] = {"type" : "slider", "range": [0, 10], "step" : 0.25}
                    
                    inputs["Autonomous Rating"] = {"type" : "slider", "range": [0, 10], "step" : 0.25}


                    addSection(match, inputs)


                break

    elif team != None and match == None:
        output["title"] = team

        inputs = {}
        
        # This should disable all the rest of the fields if it is checked since it is an auto deny
        inputs["Basic Bot"] = {"type" : "checkbox"}

        inputs["Autonomous Side"] = {"type" : "selectbox", "options" : ["Select an Option", "Left", "Right", "Ambidexterous"]}
        inputs["Autonomous Scoring Capabilities (Points)"] = {"type" : "slider", "range" : [0, 50], "step" : 1}
        inputs["Autonomous Tasks Able to be Completed"] = {"type" : "multiselect", "options" : ["At least three rings scored", 
                                                                                                "A minimum of two stakes with at least one ring scored",
                                                                                                 "Not contacting or breaking the plane of the Starting Line",
                                                                                                 "Contacting the ladder"]}

        inputs["Can Score on Wall Stakes"] = {"type" : "checkbox"}
        inputs["Can Score on High Stake"] = {"type" : "checkbox"}

        inputs["Elevation Level"] = {"type" : "slider", "range" : [0, 3], "step" : 1}

        inputs["Scoring Success Rate (%)"] = {"type" : "slider", "step" : 1}

        inputs["Mobile Goal Moving Capabilities (Grip Strength)"] = {"type" : "slider", "range" : [0, 10], "step" : 1}

        inputs["Robot Speed (RPM)"] = {"type" : "number_input", "range" : [0, 1000], "step" : 5}

        # inputs["Ability To Bully (Strength)"] = {}
        inputs["Potential to be Bullied (Estimated Weight in Pounds)"] = {"type" : "slider", "range" : [0, 5], "step" : 0.1}

        inputs["Drivetrain Wheel Composition"] = {"type" : "selectbox", "options" : ["Select an Option", "All Omniwheels", "Partially Omniwheels", "No Omniwheels"]}

        addSection("General Info", inputs)

        # TODO add code to create inputs for each of their matches here
        
        file = open("teamInfo.json", "r")
        teamInfo = json.load(file)
        file.close()

        teamInfo = teamInfo[team]

        for i in teamInfo["matches"]:
            inputs = {}
            
            inputs["Carried Status"] = {"type" : "selectbox", "options" : ["Neither team was carried.", "Yes, got carried.", "No, carried the other team."]}
            
            inputs["Violations"] = {"type" : "selectbox", "options" : ["None", "Minor", "Major"]}

            inputs["Driving Skills Rating"] = {"type" : "slider", "range": [0, 10], "step" : 0.25}
            
            inputs["Autonomous Rating"] = {"type" : "slider", "range": [0, 10], "step" : 0.25}

            addSection(i, inputs)


    elif team == None and match != None:
        matchURL = f"https://www.robotevents.com/api/v2/events/{globalEventID}/divisions/1/matches?per_page=250"

        matchData = getURL(matchURL)["data"]

        for i in matchData:
            if i["name"] == match:
                matchData = i

                break

        output["title"] = match

        for n in matchData["alliances"]:
            for i in n["teams"]:
                inputs = {}
                
                inputs["Carried Status"] = {"type" : "selectbox", "options" : ["Neither team was carried.", "Yes, got carried.", "No, carried the other team."]}
                
                inputs["Violations"] = {"type" : "selectbox", "options" : ["None", "Minor", "Major"]}

                inputs["Driving Skills Rating"] = {"type" : "slider", "range": [0, 10], "step" : 0.25}
                
                inputs["Autonomous Rating"] = {"type" : "slider", "range": [0, 10], "step" : 0.25}

                addSection(i["team"]["name"], inputs)

    
    with open("output.json", "w") as file:
        json.dump(output, file)

    return output