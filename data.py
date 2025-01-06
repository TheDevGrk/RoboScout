from dotenv import load_dotenv
import os
import time
import json
import datetime
import requests

# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC


load_dotenv()

token = os.getenv("token")
email = os.getenv("email")
password = os.getenv("password")
bravePath = os.getenv("bravePath")
driverPath = os.getenv("driverPath")
eventSku = os.getenv("eventSku")

# options = Options()
# options.add_argument('log-level=3')
# options.headless = True
# options.binary_location = bravePath
# service = Service(driverPath)

file = open("token.txt", "r")
token = file.read()
file.close()

headers = {
    "Authorization" : "Bearer " + token
}

def getURL(url):
    response = requests.get(url, headers = headers)

    print(response.status_code)
    return response.json()

def fetchEventData(eventSku : str):
    print(0)
    eventURL = f"https://www.robotevents.com/api/v2/events?sku%5B%5D={eventSku}&myEvents=false"

    eventData = getURL(eventURL)
    time.sleep(1)

    print(1)

    eventID = eventData["data"][0]["id"]
    teamsURL = f"https://www.robotevents.com/api/v2/events/{eventID}/teams"

    print(1.1)

    teamsData = getURL(teamsURL)
    time.sleep(1)
    print(1.11)
    pageNum = teamsData["meta"]["last_page"]

    print(1.2)

    teamsData = teamsData["data"]

    print(2)

    if pageNum > 1:
        for i in range(2, pageNum + 1):
            teamsData = teamsData + getURL(teamsURL + f"?page={i}")["data"]

    
    teamInfo = {}
    print(3)
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

    matchURL = f"https://www.robotevents.com/api/v2/events/{eventID}/divisions/1/matches"

    matchData = getURL(matchURL)["data"]

    match = []

    for i in matchesData:
        match.append(i["name"])       

    return [teamInfo, eventID, match]

def refreshData():
    while True:
        data = fetchEventData(eventSku)

        print(5)

        teamInfo = data[0]
        eventID = data[1]
        matches = data[2]

        file = open("teamInfo.txt", "w")
        file.write(str(teamInfo).replace("'", '"'))
        file.close()
        print(2)
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