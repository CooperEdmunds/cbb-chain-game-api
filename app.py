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
    excluded_teams = json.loads(request_params['excludedTeams'])

    # Get graph from S3
    s3_client.download_file(os.environ['bucket'], 'current_season_graph.json', 'current_season.json')
    graph = json.loads(open('current_season.json').read())['graph']
    os.remove('current_season.json')

    def team_not_in_chain(team, chain):
        for win in chain:
            if(win['l'] == team or win['w'] == team):
                return False
        return True

    def make_chains(team_a, target, exclude, max_num, link_limit):
        chains = []
        chains_queue = Queue()

        edges_set = set()
        edges = []

        nodes = []

        nodes_dict = {}
        team_a_wins = graph[team_a]
        for win in team_a_wins:
            chains_queue.put([win])

        while(len(chains) < max_num and chains_queue.qsize() > 0):
            chain = chains_queue.get()

            if(len(chain) > link_limit):
                break

            last_win = chain[len(chain) - 1]
            opponent = last_win['l']

            if(opponent == target):
                chains.append(chain)
                for win in chain:
                    winner = win['w']
                    if winner not in nodes_dict:
                        nodes.append({ "id": len(nodes_dict), "label": winner, "title": winner })
                        nodes_dict[winner] = len(nodes_dict)

                    loser = win['l']
                    if loser not in nodes_dict:
                        nodes.append({ "id": len(nodes_dict), "label": loser, "title": loser })
                        nodes_dict[loser] = len(nodes_dict)

                    edge_string = winner + "/-/" + loser
                    if edge_string not in edges_set:
                        edges_set.add(edge_string)
                        edges.append({"from": nodes_dict[winner], "to": nodes_dict[loser]})

                continue

            if(opponent not in graph):
                continue

            wins = graph[opponent]

            for win in wins:
                opponent_2 = win['l']
                if(team_not_in_chain(opponent_2, chain) and opponent_2 not in exclude):
                    new_chain = chain[:]
                    new_chain.append(win)
                    chains_queue.put(new_chain)

        return {"chains":chains, "nodes":nodes, "edges":edges}

    a_to_b_data = make_chains(teamA, teamB, excluded_teams, 30, 7)
    b_to_a_data = make_chains(teamB, teamA, excluded_teams, 30, 7)

    response = {"a_to_b": a_to_b_data, "b_to_a" : b_to_a_data}
    return json.dumps(response)

if __name__ == '__main__':
    app.run(debug=True)
