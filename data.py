from dotenv import load_dotenv
import os
import time
import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


load_dotenv()

token = os.getenv("token")
email = os.getenv("email")
password = os.getenv("password")
bravePath = os.getenv("bravePath")
driverPath = os.getenv("driverPath")
eventSku = os.getenv("eventSku")

options = Options()
options.add_argument('log-level=3')
options.headless = True
options.binary_location = bravePath
service = Service(driverPath)


def fetchEventData(eventSku : str):
    driver = webdriver.Chrome(service=service, options=options)
    eventURL = f"https://www.robotevents.com/api/v2/events?sku%5B%5D={eventSku}&myEvents=false"
    loginURL = "https://www.robotevents.com/auth/login"

    try:
        driver.get(loginURL)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))

        emailField = driver.find_element(By.NAME, "email")
        emailField.send_keys(email)

        passwordField = driver.find_element(By.NAME, "password")
        passwordField.send_keys(password)

        passwordField.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(EC.url_changes(loginURL))

        driver.get(eventURL)

        eventSource = driver.page_source
        jsonStart = eventSource.find("<pre>")
        jsonEnd = eventSource.find("</pre>")

        eventSource = eventSource[jsonStart + 5:jsonEnd]

        eventData = json.loads(eventSource)

        eventID = eventData["data"][0]["id"]
        teamsURL = f"https://www.robotevents.com/api/v2/events/{eventID}/teams"

        driver.get(teamsURL)
        
        teamsSource = driver.page_source
        jsonStart = teamsSource.find("<pre>")
        jsonEnd = teamsSource.find("</pre>")

        teamsSource = teamsSource[jsonStart + 5:jsonEnd]
        teamsData = json.loads(teamsSource)
        pageNum = teamsData["meta"]["last_page"]

        teamsData = teamsData["data"]

        if pageNum > 1:
            for i in range(2, pageNum + 1):
                driver.get(teamsURL + f"?page={i}")

                teamsSource = driver.page_source
                jsonStart = teamsSource.find("<pre>")
                jsonEnd = teamsSource.find("</pre>")

                teamsSource = teamsSource[jsonStart + 5:jsonEnd]
                teamsData = teamsData + json.loads(teamsSource)["data"]

        
        teamInfo = {}

        for i in teamsData:
            skillsURL = f"https://www.robotevents.com/api/v2/teams/{i["id"]}/skills?per_page=500"

            driver.get(skillsURL)
            
            skillsSource = driver.page_source
            jsonStart = skillsSource.find("<pre>")
            jsonEnd = skillsSource.find("</pre>")

            skillsSource = skillsSource[jsonStart + 5:jsonEnd]
            skillsData = json.loads(skillsSource)["data"]

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



            matchesURL = f"https://www.robotevents.com/api/v2/teams/{i["id"]}/matches?per_page=1000"

            driver.get(matchesURL)

            matchesSource = driver.page_source
            jsonStart = matchesSource.find("<pre>")
            jsonEnd = matchesSource.find("</pre>")

            matchesSource = matchesSource[jsonStart + 5:jsonEnd]
            matchesData = json.loads(matchesSource)

            pageNum = matchesData["meta"]["last_page"]

            matchesData = matchesData["data"]

            if pageNum > 1:
                for n in range(2, pageNum + 1):
                    driver.get(matchesURL + f"?page={n}")

                    matchesSource = driver.page_source
                    jsonStart = matchesSource.find("<pre>")
                    jsonEnd = matchesSource.find("</pre>")

                    matchesSource = matchesSource[jsonStart + 5:jsonEnd]
                    matchesData = matchesData + json.loads(matchesSource)["data"]

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
            
        rankingsURL = f"https://www.robotevents.com/api/v2/events/{eventID}/divisions/1/rankings"

        driver.get(rankingsURL)

        rankingsSource = driver.page_source
        jsonStart = rankingsSource.find("<pre>")
        jsonEnd = rankingsSource.find("</pre>")

        rankingsSource = rankingsSource[jsonStart + 5:jsonEnd]
        rankingsData = json.loads(rankingsSource)["data"]

        rank = 0
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

        
        
    finally:
        driver.quit()

    return teamInfo

def refreshData():
    teamInfo = fetchEventData(eventSku)

    file = open("teamInfo.txt", "w")
    file.write(str(teamInfo).replace("'", '"'))
    file.close()