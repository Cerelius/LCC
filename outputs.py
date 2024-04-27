import pandas
import json
from datetime import date

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

def build_match_json(file_name, match_id, processed_match):
    output_file_path = f"results/{(file_name, match_id)[match_id != '']}_data.json"
    with open(output_file_path, "w") as output_file:
        json.dump(processed_match, output_file)

def build_player_stats_report(player_data):
    with pandas.ExcelWriter(f"results/Player_Stats_{date.today()}.xlsx", engine="openpyxl", mode="w") as writer:
        pandas.DataFrame(player_data).T.to_excel(writer, sheet_name="Player Stats", index=True)