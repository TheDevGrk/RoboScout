from dotenv import load_dotenv
import os
import time
import json
import datetime
import requests
import math

load_dotenv()

token = os.getenv("token")
email = os.getenv("email")
password = os.getenv("password")
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

def getEventID(sku):
    eventURL = f"https://www.robotevents.com/api/v2/events?sku%5B%5D={sku}&myEvents=false"

    eventData = getURL(eventURL)
    time.sleep(1)

    return eventData["data"][0]["id"]

def fetchEventData(eventSku : str):
    eventID = getEventID(eventSku)
    print("Gathered eventID")

    teamsURL = f"https://www.robotevents.com/api/v2/events/{eventID}/teams"

    teamsData = getURL(teamsURL)
    print("Gathered teamsData")

    time.sleep(1)

    pageNum = teamsData["meta"]["last_page"]

    teamsData = teamsData["data"]

    if pageNum > 1:
        for i in range(2, pageNum + 1):
            teamsData = teamsData + getURL(teamsURL + f"?page={i}")["data"]

    print("Gathered teamsData pages")
    
    teamInfo = {}

    for i in teamsData:
        skillsURL = f"https://www.robotevents.com/api/v2/teams/{i["id"]}/skills?per_page=250"

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

        matchesURL = f"https://www.robotevents.com/api/v2/teams/{i["id"]}/matches?per_page=250"

        matchesData = getURL(matchesURL)

        pageNum = matchesData["meta"]["last_page"]

        matchesData = matchesData["data"]

        if pageNum > 1:
            for n in range(2, pageNum + 1):
                matchesData = matchesData + getURL(matchesURL + f"&page={n}")["data"]

        matches = {}

        for n in matchesData:
            if n["event"]["code"] == eventSku and str(n["name"]).startswith("Qualifier"):
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
        
        print("Just finished", i["number"])
        time.sleep(3)
        
    print("Rankings time!")
    rankingsURL = f"https://www.robotevents.com/api/v2/events/{eventID}/divisions/1/rankings?per_page=250"

    rankingsData = getURL(rankingsURL)["data"]

    rank = 1

    for i in rankingsData:
        results = {}
        
        rank = i["rank"]
        results["wins"] = i["wins"]
        results["losses"] = i["losses"]
        results["ties"] = i["ties"]

        info = teamInfo[i["team"]["name"]]
        info["rank"] = rank
        info["results"] = results

        teamInfo[i["team"]["name"]] = info

    matchURL = f"https://www.robotevents.com/api/v2/events/{eventID}/divisions/1/matches?per_page=250"

    matchData = getURL(matchURL)["data"]

    match = []

    for i in matchData:
        if str(i["name"]).startswith("Qualifier"):
            match.append(i["name"])  

    return [teamInfo, match]

def refreshData():
    while True:
        data = fetchEventData(eventSku)


        teamInfo = data[0]
        matches = data[1]

        file = open("teamInfo.json", "w")
        json.dump(teamInfo, file)
        file.close()

        file = open("matches.txt", "w")
        file.write(str(matches))
        file.close()
        
        time.sleep(600)

def findTeam(number : str):
    returnValue = {}
    findTeamURL = f"https://www.robotevents.com/api/v2/teams?number%5B%5D={number}"

    teamData = getURL(findTeamURL)["data"][0]

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
        if teamData != None:
            findEventsURL = findEventsURL + f"&team%5B%5D={teamData["id"]}"

    eventData = getURL(findEventsURL)["data"]   
    events = []
    for i in eventData:
        events.append({"name" : f"{i["name"]} - {i["start"][:10]}", "sku" : i["sku"]})

    return events

        

def filterInputs(team, match):
    output = {"popup" : None, "title" : None, "sections" : []}

    def addSection(heading: str, inputs: dict):
        output["sections"].append({
            "heading" : heading,
            "inputs" : inputs
        })    


    file = open("teamInfo.json", "r")
    teamInfo = json.load(file)
    file.close()
    
    if match == None and team == None:
        output["popup"] = "You must choose some filters!"
    
    elif match != None and team!= None:

        for i in teamInfo:

            if i == team:

                matchFound = False

                for n in teamInfo[i]["matches"]:
                    if n == match:
                        matchFound = True
                        # matchInfo = team[i]["matches"][n]
                        break
                
                if matchFound == False:
                    output["popup"] = f"{team} was not in {match}"

                else:
                    output["title"] = team

                    inputs = {}
                    
                    inputs["Carried Status"] = {"type" : "selectbox", "options" : ["Neither team was carried.", "Yes, got carried.", "No, carried the other team."], "key" : team + "-" + match}

                    inputs["Driving Skills Rating"] = {"type" : "slider", "range": [0.0, 10.0], "step" : 0.25, "key" : team + "-" + match}
                    
                    inputs["Autonomous Rating"] = {"type" : "slider", "range": [0.0, 10.0], "step" : 0.25, "key" : team + "-" + match}

                    inputs["Violations"] = {"type" : "violationModule", "key" : team + "-" + match}


                    addSection(match, inputs)


                break

    elif match == None:
        output["title"] = team

        inputs = {}
        
        # This should disable all the rest of the fields if it is checked since it is an auto deny
        inputs["Basic Bot"] = {"type" : "checkbox", "key" : team + "-general"}

        inputs["State Qualified"] = {"type" : "checkbox", "key" : team + "-general"}

        inputs["Autonomous Side"] = {"type" : "selectbox", "options" : ["Left", "Right", "Ambidexterous", "No Auton"], "key" : team + "-general"}
        inputs["Autonomous Scoring Capabilities (Points)"] = {"type" : "slider", "range" : [0, 25], "step" : 1, "key" : team + "-general"}
        inputs["Autonomous Tasks Able to be Completed"] = {"type" : "multiselect", "options" : ["At least three rings scored", 
                                                                                                "A minimum of two stakes with at least one ring scored",
                                                                                                 "Not contacting or breaking the plane of the Starting Line",
                                                                                                 "Contacting the ladder"], "key" : team + "-general"}

        inputs["Can Score on Wall Stakes"] = {"type" : "checkbox", "key" : team + "-general"}
        inputs["Can Score on High Stake"] = {"type" : "checkbox", "key" : team + "-general"}

        inputs["Elevation Level"] = {"type" : "slider", "range" : [0, 3], "step" : 1, "key" : team + "-general"}

        inputs["Scoring Success Rate (%)"] = {"type" : "slider", "range" : [0, 100], "step" : 1, "key" : team + "-general"}

        inputs["Mobile Goal Moving Capabilities (Grip Strength)"] = {"type" : "slider", "range" : [0, 10], "step" : 1, "key" : team + "-general"}

        inputs["Robot Speed (RPM)"] = {"type" : "number_input", "range" : [0, 1000], "step" : 5, "key" : team + "-general"}

        # inputs["Ability To Bully (Strength)"] = {}
        inputs["Potential to be Bullied (Estimated Weight in Pounds)"] = {"type" : "slider", "range" : [0.0, 25.0], "step" : 0.5, "key" : team + "-general"}

        inputs["Drivetrain Wheel Composition"] = {"type" : "selectbox", "options" : ["All Omniwheels", "Partially Omniwheels", "No Omniwheels"], "key" : team + "-general"}

        addSection("General Info", inputs)

        
        file = open("teamInfo.json", "r")
        teamInfo = json.load(file)
        file.close()

        teamInfo = teamInfo[team]

        for i in teamInfo["matches"]:
            if str(i).startswith("Qualifier"):
                inputs = {}
                
                inputs["Carried Status"] = {"type" : "selectbox", "options" : ["Neither team was carried.", "Yes, got carried.", "No, carried the other team."], "key" : team + "-" + i}

                inputs["Driving Skills Rating"] = {"type" : "slider", "range": [0.0, 10.0], "step" : 0.25, "key" : team + "-" + i}
                
                inputs["Autonomous Rating"] = {"type" : "slider", "range": [0.0, 10.0], "step" : 0.25, "key" : team + "-" + i}

                inputs["Violations"] = {"type" : "violationModule", "key" : team + "-" + i}

                addSection(i, inputs)


    elif team == None:
        eventID = getEventID(eventSku)
        matchURL = f"https://www.robotevents.com/api/v2/events/{eventID}/divisions/1/matches?per_page=250"

        matchData = getURL(matchURL)["data"]

        for i in matchData:
            if i["name"] == match:
                matchData = i

                break

        output["title"] = match

        for n in matchData["alliances"]:
            for i in n["teams"]:
                color = n["color"]

                inputs = {}
                
                inputs["Carried Status"] = {"type" : "selectbox", "options" : ["Neither team was carried.", "Yes, got carried.", "No, carried the other team."], "key" : i["team"]["name"] + "-" + match}
                
                inputs["Driving Skills Rating"] = {"type" : "slider", "range": [0.0, 10.0], "step" : 0.25, "key" : i["team"]["name"] + "-" + match}
                
                inputs["Autonomous Rating"] = {"type" : "slider", "range": [0.0, 10.0], "step" : 0.25, "key" : i["team"]["name"] + "-" + match}

                inputs["Violations"] = {"type" : "violationModule", "key" : i["team"]["name"] + "-" + match}

                addSection(f":{color}[{i["team"]["name"]}]", inputs)

    
    with open("output.json", "w") as file:
        json.dump(output, file)
        file.close()

    return output

def calculateResults():
    file = open("teamInfo.json", "r")
    autoData = json.loads(file.read())
    file.close()

    file = open("values.json", "r")
    manData = json.loads(file.read())
    file.close()

    results = {}

    for team in autoData:
        teamResult = {}
        score = 0
        possibleScore = 0
        disqualified = False
        dqReason = "Not Disqualified"
        dqStates = []
        insufficientData = 0
        insufficientMatchData = 0

        generalTag = "-" + team + "-general"

        lastMatches = []

        matchesLen = len(autoData[team]["matches"])
        matchesLooped = 0
        for i in autoData[team]["matches"]:
            matchesLooped += 1

            if matchesLooped > matchesLen - 2:
                lastMatches.append(i)
        

        matchesWithData = 0
        generalDataTest = False
        matchesDataTest = True
        try:
            test = manData["Basic Bot" + generalTag]
            generalDataTest = True
            for match in autoData[team]["matches"]:
                test = manData["Driving Skills Rating-" + team + "-" + match]
                matchesWithData += 1
        except:
            if matchesWithData < math.floor(len(autoData[team]["matches"])):
                disqualified = True
                matchesDataTest = False
                dqReason = "Not Enough Data Provided"
                dqStates.append("No Matches")
            if generalDataTest == False:
                disqualified = True
                dqReason = "Not Enough Data Provided"
                dqStates.append("No General")

        teamResult["Basic Bot"] = "Data Not Provided"
        teamResult["State Qualified"] = "Data Not Provided"
        teamResult["Autonomous Side"] = "Data Not Provided"
        teamResult["Autonomous Scoring Capabilities (Points)"] = "Data Not Provided"
        teamResult["Autonomous Tasks Able to be Completed"] = "Data Not Provided"
        teamResult["Can Score on Wall Stakes"] = "Data Not Provided"
        teamResult["Can Score on High Stake"] = "Data Not Provided"
        teamResult["Elevation Level"] = "Data Not Provided"
        teamResult["Scoring Success Rate (%)"] = "Data Not Provided"
        teamResult["Robo Speed (RPM)"] = "Data Not Provided"
        teamResult["Mobile Goal Moving Capabilities (Grip Strength)"] = "Data Not Provided"
        teamResult["Potential to be Bullied (Estimated Weight in Pounds)"] = "Data Not Provided"
        teamResult["Drivetrain Wheel Composition"] = "Data Not Provided"

        if "No General" not in dqStates:
            if manData["Basic Bot" + generalTag]:
                disqualified = True
                dqReason = "Having a \"Basic Bot\""
            teamResult["Basic Bot"] = manData["Basic Bot" + generalTag]


            possibleScore += 15
            if manData["State Qualified" + generalTag]:
                score += 15
            teamResult["State Qualified"] = manData["State Qualified" + generalTag]



            if manData["Autonomous Side" + generalTag] != None:
                possibleScore += 5
            else:
                insufficientData += 1
            match manData["Autonomous Side" + generalTag]:
                case "Right":
                    score += 3
                case "Left":
                    score += 3
                case "No Auton":
                    score -= 5
                case "Ambidexterous":
                    score += 5
            teamResult["Autonomous Side"] = manData["Autonomous Side" + generalTag]


            if manData["Autonomous Scoring Capabilities (Points)" + generalTag] != 0:
                possibleScore += 4
                score += math.floor(manData["Autonomous Scoring Capabilities (Points)" + generalTag] / 3)
            else:
                insufficientData += 1
            teamResult["Autonomous Scoring Capabilities (Points)"] = manData["Autonomous Scoring Capabilities (Points)" + generalTag]


            tasks = manData["Autonomous Tasks Able to be Completed" + generalTag]
            possibleScore += 6
            if "At least three rings scored" in tasks:
                score += 2
            if "A minimum of two stakes with at least one ring scored" in tasks:
                score += 3
            if "Not contacting or breaking the plane of the Starting line" not in tasks:
                score -= 4
            if "Contacting the ladder" in tasks:
                score += 1
            teamResult["Autonomous Tasks Able to be Completed"] = manData["Autonomous Tasks Able to be Completed" + generalTag]


            possibleScore += 1
            if manData["Can Score on Wall Stakes" + generalTag]:
                score += 1
            if manData["Can Score on High Stake" + generalTag]:
                score -= 1
            teamResult["Can Score on Wall Stakes"] = manData["Can Score on Wall Stakes" + generalTag]
            teamResult["Can Score on High Stake"] = manData["Can Score on High Stake" + generalTag]


            possibleScore += 2
            match manData["Elevation Level" + generalTag]:
                case 1:
                    score += 1
                case 2:
                    score += 2
                case 3:
                    score += 1
            teamResult["Elevation Level"] = manData["Elevation Level" + generalTag]

            
            successRate = manData["Scoring Success Rate (%)" + generalTag]
            if successRate != 0:
                possibleScore += 6
            else:
                insufficientData += 1
            if 0 < successRate <= 25:
                score -= 10
            elif 25 < successRate <= 50:
                score -= 5
            elif 75 < successRate <= 90:
                score += 3
            elif successRate > 90:
                score += 6
            teamResult["Scoring Success Rate (%)"] = successRate


            speed = manData["Robot Speed (RPM)" + generalTag]
            if speed != 0:
                possibleScore += 9
            else:
                insufficientData += 1
            if 0 < speed <= 100:
                score -= 8
            elif 100 < speed <= 200:
                score -= 4
            elif 200 < speed <= 300:
                score += 1
            elif 300 < speed <= 400:
                score += 2
            elif 400 < speed <= 500:
                score += 5
            elif 500 < speed <= 600:
                score += 7
            elif speed > 600:
                score += 9
            teamResult["Robo Speed (RPM)"] = speed


            gripStrength = manData["Mobile Goal Moving Capabilities (Grip Strength)" + generalTag]
            if gripStrength != 0:
                possibleScore += 3
            else:
                insufficientData += 1
            if 0 < gripStrength <= 5:
                score -= 3
            elif 5 < gripStrength <= 7:
                score += 1
            elif gripStrength > 8:
                score += 3
            teamResult["Mobile Goal Moving Capabilities (Grip Strength)"] = gripStrength


            weight = manData["Potential to be Bullied (Estimated Weight in Pounds)" + generalTag]
            if weight != 0:
                possibleScore += 6
            else:
                insufficientData += 1
            if 0 < weight <= 5:
                score -= 10
            elif 15 < weight <= 20:
                score += 3
            elif weight > 20:
                score += 6
            teamResult["Potential to be Bullied (Estimated Weight in Pounds)"] = weight


            if manData["Drivetrain Wheel Composition" + generalTag] != None:
                possibleScore += 3
            else:
                insufficientData += 1
            match manData["Drivetrain Wheel Composition" + generalTag]:
                case "All Omniwheels":
                    score -= 5
                case "Partially Omniwheels":
                    score += 3
                case "No Omniwheels":
                    score -= 2
            teamResult["Drivetrain Wheel Composition"] = manData["Drivetrain Wheel Composition" + generalTag]


        matchResult = {}
        if "No Matches" not in dqStates:
            if (0 < manData["Driving Skills Rating-" + team + "-" + lastMatches[0]] <= 2 or
                0 < manData["Driving Skills Rating-" + team + "-" + lastMatches[1]] <= 2) or (
                0 < manData["Autonomous Rating-" + team + "-" + lastMatches[0]] <= 2 or
                0 < manData["Autonomous Rating-" + team + "-" + lastMatches[1]] <= 2):
                disqualified = True
                dqReason = "Driving Skills / Autonomous Rating is too low"


            for i in autoData[team]["matches"]:
                matchTag = "-" + team + "-" + i
                matchData = autoData[team]["matches"][i]

                carriedStatus = manData["Carried Status" + matchTag]
                driveSkill = manData["Driving Skills Rating" + matchTag]
                autonRating = manData["Autonomous Rating" + matchTag]
                teamScore = matchData["teams"]["alliance"][3]
                opponentScore = matchData["teams"]["opponents"][3]

                matchResult[i] = {"Carried Status" : carriedStatus, "Driving Skills Rating" : driveSkill, "Autonomous Rating" : autonRating,
                                   "result" : matchData["result"], "Alliance's Score" : teamScore, "Opponent's Score" : opponentScore}

                if carriedStatus == None and driveSkill == 0 and autonRating == 0:
                    insufficientMatchData += 3
                    continue

                # maybe change how this is scored depending on whether they won or lost
                if carriedStatus != None:
                    possibleScore += 4
                else:
                    insufficientMatchData += 1
                match carriedStatus:
                    case "Neither team was carried.":
                        score += 1
                    case "Yes, got carried.":
                        score -= 6
                    case "No, carried the other team.":
                        score += 4


                if driveSkill != 0:
                    possibleScore += 9
                else:
                    insufficientMatchData += 1
                if 0 < driveSkill <= 2:
                    score -= 5
                elif 2 < driveSkill <= 5:
                    score -= 6 - driveSkill
                elif 5 < driveSkill < 7:
                    score += 1
                elif 7 <= driveSkill < 9:
                    score += 3
                elif 9 <= driveSkill < 10:
                    score += 6
                elif driveSkill == 10:
                    score += 9


                if autonRating != 0:
                    possibleScore += 4
                else:
                    insufficientMatchData += 1
                if 0 < autonRating <= 2:
                    score -= 5
                elif 2 < autonRating <= 5:
                    score -= -1
                elif 5 < autonRating < 7:
                    score += 1
                elif 7 <= autonRating < 9:
                    score += 2
                elif 9 <= autonRating < 10:
                    score += 3
                elif autonRating == 10:
                    score += 4


                possibleScore += 3
                if teamScore > 16:
                    score += math.ceil((teamScore - 16) / 8)
                
                possibleScore += 5
                if opponentScore < 15 and teamScore >= 15:
                    score += 5
                elif opponentScore >= 15 and teamScore >= 15:
                    score += math.floor(teamScore / (opponentScore * 1.25))
                elif teamScore < 15 and opponentScore >= 15:
                    score -= 5
                
                possibleScore += 5
                match matchData["result"]:
                    case "Win":
                        score += 5
                    case "Loss":
                        score -= 5
            
            
        violationResult = {}
        if "No General" not in dqStates and "No Matches" not in dqStates:
            for i in manData["Violations-" + team]:
                violationResult[i] = {"Severity" : i["severity"], "Notes" : i["notes"]}
                match i["severity"]:
                    case "Minor":
                        score -= 5
                    case "Major":
                        score -= 15


        score -= math.floor(autoData[team]["rank"] / 2)

        possibleScore += 14
        score += math.ceil(autoData[team]["skills"]["auton"] / 6)
        score -= math.floor(autoData[team]["skills"]["autonRank"] / 6)
        score += math.ceil(autoData[team]["skills"]["driver"] / 6)
        score -= math.floor(autoData[team]["skills"]["driverRank"] / 6)

        teamResult["Best Autonomous Skills Run Score"] = autoData[team]["skills"]["auton"]
        teamResult["Best Driver Skills Run Score"] = autoData[team]["skills"]["driver"]
        teamResult["Autonomous Skills Rank"] = autoData[team]["skills"]["autonRank"]
        teamResult["Driver Skills Rank"] = autoData[team]["skills"]["driverRank"]
        
        possibleScore += 4
        if autoData[team]["results"]["losses"] == 0:
            winLossRatio =  math.ceil(autoData[team]["results"]["wins"] / 2)
            score += winLossRatio
        else:
            winLossRatio = math.ceil(autoData[team]["results"]["wins"] / (autoData[team]["results"]["losses"] * 2))
            score += winLossRatio
        teamResult["W/L Ratio"] = winLossRatio
        

        if possibleScore == 0:
            possibleScore = 1
        percentage = round((score / possibleScore) * 100, 2)

        if insufficientData >= 4:
            disqualified = True
            dqReason = "Not Enough General Data Provided"
        elif insufficientMatchData >= 13:
            disqualified = True
            dqReason = "Not Enough Match Data Provided"
        elif percentage < 0:
            disqualified = True
            dqReason = "Receiving a negative scoring percentage"

        if possibleScore == 1:
            possibleScore = 0

        teamResult["score"] = score
        teamResult["possible"] = possibleScore
        teamResult["disqualified"] = disqualified
        teamResult["dqReason"] = dqReason
        teamResult["percentage"] = percentage
        teamResult["matches"] = matchResult
        teamResult["violations"] = violationResult

        results[team] = teamResult

    file = open("results.json", "w")
    json.dump(results, file)
    file.close()