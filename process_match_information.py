import json
import requests
import os
from dotenv import load_dotenv
import pandas
from datetime import date

def main():
    # Accept user input for the file name
    tournament_name = input("Enter the tournament file name (Enter to use LCC_Season_2): ")
    file_path = f"tournaments/{(tournament_name,'LCC_Season_2')[tournament_name == '']}.txt"    
    file_name = file_path.split("/")[-1].split(".")[0]
  
    # Open the file and read the match IDs
    with open(file_path, "r") as file:
        match_ids = file.readlines()

    if not match_ids :
        print("No match IDs found in the file.")
        return
    
    processed_matches = []
    # For each listed match, fetch and transform the data
    for match_id in match_ids:
        match_id = match_id.strip()
        riot_match_data = fetch_match_data("NA1_" + match_id)
        processed_match = process_match_data(riot_match_data)

        # Dump each processed match data to json file for future additional programmatic use
        output_file_path = f"results/{(file_name, match_id)[match_id != '']}_data.json"
        with open(output_file_path, "w") as output_file:
            json.dump(processed_match, output_file)
        # Add to list for excel workbook
        processed_matches.append(processed_match)
    
    build_excel_workbook(processed_matches)
    print("Excel workbook created successfully.")

def fetch_match_data(match_id):
    api_key = os.getenv("RIOT_API_KEY")
    headers = {"X-Riot-Token": api_key}
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch match data: {response.text}")
    return response.json()
        
def process_match_data(match_data):
    match_information = {}
    participant_information = []
    
    match_information["game_id"] = match_data["metadata"]["matchId"]
    
    for participant in match_data["info"]["participants"]:
        participant_information.append(process_participant_data(participant))
    match_information["participants"] = participant_information
    return match_information

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

def build_excel_workbook(matches):
    
    with pandas.ExcelWriter(f"results/Stats_Report_{date.today()}.xlsx", engine="openpyxl", mode="w") as writer:
        for match in matches:
            pandas.DataFrame(match["participants"]).to_excel(writer, sheet_name=f"{match['game_id']}", index=False)
            for participant in match["participants"]:
                sheet_name = f"{participant['riotIdGameName']}"
                if sheet_name in writer.sheets:
                    startrow = writer.sheets[sheet_name].max_row
                    df = pandas.DataFrame(participant, index=[0])
                    df.to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=False, header=False)
                else:
                    pandas.DataFrame(participant, index=[0]).to_excel(writer, sheet_name=sheet_name, index=False)


load_dotenv(dotenv_path=".env", verbose=True, override=True)           
main()