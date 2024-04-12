import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    # Accept user input for the file name
    match_id = input("Enter the match ID (Enter to use sample data): ")
    file_path = "tests/match_information_response.json"    
    file_name = file_path.split("/")[-1].split(".")[0]
    if match_id == "":
        # Open the test file for processing
        with open(file_path, "r") as file:
            # Process the file contents
            match_data = json.load(file)
    # Fetch data from the API if match ID is provided
    else:
        match_data = fetch_match_data("NA1_" + match_id)
    
    match_information = process_match_data(match_data)
    
    # Output the processed data to a new file
    output_file_path = f"results/{(file_name, match_id)[match_id != '']}_process.json"
    with open(output_file_path, "w") as output_file:
        json.dump(match_information, output_file)


def fetch_match_data(match_id):
    api_key = os.getenv("RIOT_API_KEY")
    headers = {"X-Riot-Token": api_key}
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=headers)
    return response.json()

def process_participant_data(participant_data):
    participant_information = {}
    participant_information["puuid"] = participant_data["puuid"]
    participant_information["riotIdGameName"] = participant_data["riotIdGameName"]
    participant_information["championName"] = participant_data["championName"]
    participant_information["teamId"] = participant_data["teamId"]
    participant_information["lane"] = participant_data["lane"]
    participant_information["win"] = participant_data["win"]
    participant_information["kills"] = participant_data["kills"]
    participant_information["deaths"] = participant_data["deaths"]
    participant_information["assists"] = participant_data["assists"]
    participant_information["totalDamageDealtToChampions"] = participant_data["totalDamageDealtToChampions"]
    participant_information["visionScore"] = participant_data["visionScore"]
    return participant_information
        
def process_match_data(match_data):
    match_information = {}
    participant_information = []
    
    match_information["game_id"] = match_data["metadata"]["matchId"]
    
    for participant in match_data["info"]["participants"]:
        participant_information.append(process_participant_data(participant))
    match_information["participants"] = participant_information
    
    return match_information

main()