from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from process_match_reports import process_match

app = Flask(__name__)

client = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))

db = client['lcc_lol']
matches = db['matches']

@app.route('/add_match', methods=['POST'])
def add_match():
    print('Adding match')
    data = request.json
    print({"match_id": "NA1_" + data["match_id"]})
    if matches.find_one({"match_id": "NA1_" + data["match_id"]}) is None:
        processed_match = process_match(data["match_id"])
        matches.insert_one(processed_match)
        return jsonify({'message': 'Match added successfully'})
    else:
        return jsonify({'message': 'Match already exists'})

if __name__ == '__main__':
    load_dotenv(dotenv_path=".env", verbose=True, override=True)  
    app.run(debug='true', host='0.0.0.0')