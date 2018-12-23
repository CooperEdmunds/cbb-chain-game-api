import json
import os
import boto3
from flask import Flask, jsonify, request
from datetime import datetime
from collections import defaultdict
from queue import Queue

from sportsreference.ncaab.boxscore import Boxscores

app = Flask(__name__)

class GameNode:
   def __init__(self, game, date):
      self.team = game["winning_name"]
      self.opponent = game["losing_name"]
      self.differential = abs(game["home_score"] - game["away_score"])


@app.route('/wins', methods=['GET'])
def get_wins():
    # Instantiate S3 client
    s3_client = boto3.client('s3',
                          aws_access_key_id=os.environ['aws_access_key_id'],
                          aws_secret_access_key=os.environ['aws_secret_access_key'],
                          region_name=os.environ['region']
                          )

    request_params = request.values
    team = request_params['team']

    # Get graph data from S3
    s3_client.download_file(os.environ['bucket'], 'current_season_graph.json', 'current_season.json')
    data = json.loads(open('current_season.json').read())
    os.remove('current_season.json')

    response = {"updated": data["updated"], "wins" : data["graph"][team]}
    return json.dumps(response)


@app.route('/chains', methods=['GET'])
def get_chains():
    # Instantiate S3 client
    s3_client = boto3.client('s3',
        aws_access_key_id=os.environ['aws_access_key_id'],
        aws_secret_access_key=os.environ['aws_secret_access_key'],
        region_name=os.environ['region']
    )

    request_params = request.values
    teamA = request_params['teamA']
    teamB = request_params['teamB']
    excluded_teams = json.loads(request_params['excluded_teams'])

    # Get graph from S3
    s3_client.download_file(os.environ['bucket'], 'current_season_graph.json', 'current_season.json')
    graph = json.loads(open('current_season.json').read())['graph']
    os.remove('current_season.json')

    def make_chains(teamA, target, exclude, max_num, link_limit):
        answers = []
        history_queue = Queue()

        history_queue.put([teamA])

        while(len(answers) < max_num and history_queue.qsize() > 0):
            history = history_queue.get()

            if(len(history) > link_limit): return answers

            last_team = history[len(history) - 1]

            if(last_team == target):
                answers.append(" -> ".join(history))
                continue

            if(last_team not in graph):
                continue

            wins = graph[last_team]

            for win in wins:
                opponent = win['opponent']
                if(opponent not in history and opponent not in exclude):
                    new_history = history[:]
                    new_history.append(opponent)
                    history_queue.put(new_history)

        return answers

    a_to_b_chains = make_chains(teamA, teamB, excluded_teams, 30, 8)
    b_to_a_chains = make_chains(teamB, teamA, excluded_teams, 30, 8)

    response = {"a_to_b_chains": a_to_b_chains, "b_to_a_chains" : b_to_a_chains}
    return json.dumps(response)

if __name__ == '__main__':
    app.run(debug=True)
