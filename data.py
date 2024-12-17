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

            teamInfo[i["number"]] = [i["team_name"], i["organization"], i["id"], skills]
        
    finally:
        driver.quit()

    return teamInfo

def refreshData():
    while True:
        teamInfo = fetchEventData(eventSku)

        file = open("teamInfo.txt", "w")
        file.write(str(teamInfo))
        file.close()

        time.sleep(300)