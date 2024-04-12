import json
import requests
import os
from dotenv import load_dotenv

def main():
    # Accept user input for the file name
    match_id = input("Enter the match ID (Enter to use sample data): ")
    if match_id == "":
        file_path = "tests/match_information_response.json"    
        # Open the test file for processing
        with open(file_path, "r") as file:
            # Process the file contents
            match_data = json.load(file)
        file_name = file_path.split("/")[-1].split(".")[0]
    # Fetch data from the API if match ID is provided
    else:
        match_data = fetch_match_data("NA1_" + match_id)
    
    match_information = process_match_data(match_data)
    
    # Output the processed data to a new file
    output_file_path = f"results/{(file_name, match_id)[match_id != ""]}_process.json"
    with open(output_file_path, "w") as output_file:
        json.dump(match_information, output_file)


def fetch_match_data(match_id):
    api_key = os.getenv("RIOT_API_KEY")
    headers = {"X-Riot-Token": api_key}
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=headers)
    return response.json()
        
def process_match_data(match_data):
    match_information = {}
    
    print(match_data)
    
    match_information["game_id"] = match_data["metadata"]["matchId"]
    return match_information

main()