from flask import Flask, request, jsonify
app = Flask(__name__)
from redis import Redis
from rq import Queue
from async_tasks import process_match

q = Queue(connection=Redis())

@app.route('/add_match', methods=['POST'])
def add_match():
    print('Adding match')
    data = request.json
    # Add match to queue
    q.enqueue('process_match', data)
    return jsonify({'message': 'Match added successfully'})

if __name__ == '__main__':
    app.run(debug='true', host='0.0.0.0')