import requests
import os
from mongo_connection import MongoConnection

def process_match(match_id):
    
    match_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/NA1_{match_id}"
    riot_match_data = fetch_riot_data(match_url)
    processed_match = process_match_data(riot_match_data)
    # Fetch and process timeline data
    timeline_url = match_url + "/timeline"
    riot_timeline_data = fetch_riot_data(timeline_url)
    processed_timeline_data = process_timeline_data(riot_timeline_data)
    position_data = get_position_data(riot_match_data["info"]["participants"])
    for position, teams in position_data.items():
        processed_timeline_data[teams[100]]["csd14"] = processed_timeline_data[teams[100]]["cs14"] - processed_timeline_data[teams[200]]["cs14"]
        processed_timeline_data[teams[200]]["csd14"] = processed_timeline_data[teams[200]]["cs14"] - processed_timeline_data[teams[100]]["cs14"]
    # Merge the timeline data with the match data
    processed_match["participants"] = [dict(participant, **processed_timeline_data[participant["puuid"]]) for participant in processed_match["participants"]]
    
    ordered_keys = ["puuid", "player", "champion", "role", "win", "gameLength", "champLevel", "kills", "deaths", "assists", "kda", "kp", "cs", "csm", "cs14", "csd14", "gold", "gpm", "dmg", "dpm", "teamDmg%", "dmgTakenTeam%", "firstBlood", "soloBolos", "tripleKills", "quadraKills", "pentaKills", "multikills", "visionScore", "vspm", "ccTime", "effectiveHealShield", "objectivesStolen"]
    processed_match["participants"] = [{key: participant[key] for key in ordered_keys} for participant in processed_match["participants"]]
    return processed_match
   

def get_position_data(participants):
    position_data = {
        'TOP': {100: None, 200: None},
        'JUNGLE': {100: None, 200: None},
        'MIDDLE': {100: None, 200: None},
        'BOTTOM': {100: None, 200: None},
        'UTILITY': {100: None, 200: None},
    }

    for participant in participants:
        position = participant['teamPosition']
        team = participant['teamId']
        puuid = participant['puuid']
        if position in position_data and team in position_data[position]:
            position_data[position][team] = puuid
    return position_data

def aggregate_player_season_data(match):
    for participant in match["participants"]:
        puuid = participant['puuid']
        #get player season data from db
        db = MongoConnection().get_player_stats_collection()
        player = db.find_one({"puuid": puuid})
        
        if not player:
            player = {
                'puuid': puuid,
                'riotIdGameName': participant['player'],
                'matches': 0,
                'game_minutes': 0,
                'kills': 0,
                'deaths': 0,
                'assists': 0,
                'kda': 0,
                'dmg': 0,
                'dpm': 0,
                'cs': 0,
                'csm': 0,
                'totalCsd14': 0,
                'avgCsd14': 0,
                'first_blood': 0,
                'solo_kills': 0
            }
        player['matches'] += 1
        player['game_minutes'] += round(participant['gameLength'], 2)
        player['kills'] += participant['kills']
        player['deaths'] += participant['deaths']
        player['assists'] += participant['assists']
        if player['deaths'] == 0:
            player['kda'] = player['kills'] + player['assists']
        else:
            player['kda'] = round((player['kills'] + player['assists']) / player['deaths'], 2)
        player['dmg'] += participant['dmg']
        player['dpm'] = round(player['dmg'] / player['game_minutes'], 2)
        player['cs'] += participant['cs']
        player['csm'] = round(player['cs'] / player['game_minutes'], 2)
        player['totalCsd14'] += participant['csd14']
        player['first_blood'] += participant['firstBlood']
        player['solo_kills'] += participant['soloBolos']
        
    # for player in players:
    #     for puuid, pdata in player.items():
    #         pdata['avgCsd14'] = round(pdata['totalCsd14']/pdata["matches"], 1)
        db.update_one({"puuid": puuid}, {"$set": player}, upsert=True)
    

def fetch_riot_data(url):
    api_key = os.getenv("RIOT_API_KEY")
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(f"Failed to fetch match data: {response.text}")
    return response.json()
        
def process_match_data(match_data):
    match_information = {}
    participant_information = []
    
    match_information["match_id"] = match_data["metadata"]["matchId"]
    
    for participant in match_data["info"]["participants"]:
        participant_information.append(process_participant_data(participant))
    match_information["participants"] = participant_information
    return match_information

def process_timeline_data(timeline_data):
     #Find 14 minute
    for frame in timeline_data["info"]["frames"]:
        #840000 is the millisecond timestamp for 14 minutes. Timestamps are not exact, so we need to check a range of timestamps
        if frame["timestamp"] > 840000 and frame["timestamp"] < 850000:
            minute_14 = frame["participantFrames"]
            break
    #Find Game participants
    participant_data_dict = {}
    for participant in timeline_data["info"]["participants"]:
        puuid = participant["puuid"]
        participant_id = participant["participantId"]
        #Match participant data with 14 minute data
        for pid, pdata in minute_14.items():
            if str(pid) == str(participant_id):
                participant_data_dict[puuid] = pdata
    
    #Pull and aggregate data from timeline per participant
    participants = {}
    for puuid, pdata in participant_data_dict.items():
        participant_data_14 = {}
        participant_data_14["cs14"] = pdata["minionsKilled"] + pdata["jungleMinionsKilled"]
        participants[puuid] = participant_data_14
    return participants

def process_participant_data(participant_data):
    participant_information = {}
    participant_information["puuid"] = participant_data["puuid"]
    participant_information["player"] = participant_data["riotIdGameName"]
    participant_information["champion"] = participant_data["championName"]
    participant_information["role"] = participant_data["teamPosition"]
    participant_information["win"] = participant_data["win"]
    participant_information["gameLength"] = round(participant_data["challenges"]["gameLength"]/60, 1)
    participant_information["champLevel"] = participant_data["champLevel"]
    participant_information["kills"] = participant_data["kills"]
    participant_information["deaths"] = participant_data["deaths"]
    participant_information["assists"] = participant_data["assists"]
    participant_information["kda"] = round(participant_data["challenges"]["kda"], 2)
    participant_information["kp"] = round(participant_data["challenges"]["killParticipation"], 2)
    
    participant_information["cs"] = participant_data["totalMinionsKilled"] + participant_data["neutralMinionsKilled"]
    participant_information["csm"] = round(participant_information["cs"]/participant_information["gameLength"], 2)
   
    participant_information["gold"] = participant_data["goldEarned"]
    participant_information["gpm"] = round(participant_data["challenges"]["goldPerMinute"],2)
    participant_information["objectivesStolen"] = participant_data["objectivesStolen"]
    
    participant_information["dmg"] = participant_data["totalDamageDealtToChampions"]
    participant_information["dpm"] = round(participant_data["challenges"]["damagePerMinute"],2)
    participant_information["teamDmg%"] = round(participant_data["challenges"]["teamDamagePercentage"]*100, 0)
    participant_information["dmgTakenTeam%"] = round(participant_data["challenges"]["damageTakenOnTeamPercentage"]*100, 0 )

    participant_information["firstBlood"] = participant_data["firstBloodKill"]
    participant_information["soloBolos"] = participant_data["challenges"]["soloKills"]

    participant_information["tripleKills"] = participant_data["tripleKills"]
    participant_information["quadraKills"] = participant_data["quadraKills"]
    participant_information["pentaKills"] = participant_data["pentaKills"]
    participant_information["multikills"] = participant_data["challenges"]["multikills"]
    
    participant_information["visionScore"] = participant_data["visionScore"]
    participant_information["vspm"] = round(participant_data["challenges"]["visionScorePerMinute"],2)
    participant_information["ccTime"] = participant_data["totalTimeCCDealt"]
    participant_information["effectiveHealShield"] = round(participant_data["challenges"]["effectiveHealAndShielding"],0)
    return participant_information

