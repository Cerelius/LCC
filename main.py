from flask import Flask, request, jsonify
from dotenv import load_dotenv
from process_match_reports import process_match, aggregate_player_season_data
from flask_cors import CORS
from mongo_connection import MongoConnection

app = Flask(__name__)
CORS(app)

matches = MongoConnection().get_matches_collection()
player_stats = MongoConnection().get_player_stats_collection()

@app.route('/')
def sanity_check():
    return "Welcome to the LCC API!"

@app.route('/add_match', methods=['POST'])
def add_match():
    print('Adding match')
    data = request.json
    if matches.find_one({"match_id": "NA1_" + data["match_id"]}) is None:
        processed_match = process_match(data["match_id"])
        matches.insert_one(processed_match)
        
        aggregate_player_season_data(processed_match)
        
        
        return jsonify({'message': 'Match added successfully'})
    else:
        return jsonify({'message': 'Match already exists'})

@app.route('/get_all_matches', methods=['GET'])
def get_all_matches():
    match_data = list(matches.find({}, {'_id': 0}))
    return jsonify(match_data)

@app.route('/match/<match_id>', methods=['GET'])
def get_match(match_id):
    match_data = matches.find_one({"match_id": match_id}, {'_id': 0})
    return jsonify(match_data)

@app.route('/player_stats', methods=['GET'])
def get_player_stats():
    player_data = list(player_stats.find({}, {'_id': 0}))
    return jsonify(player_data)
 
if __name__ == '__main__':
    load_dotenv(dotenv_path=".env", verbose=True, override=True)  
    app.run(debug='true', host='0.0.0.0')