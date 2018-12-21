import json
from flask import Flask, jsonify, request
from datetime import datetime
from collections import defaultdict

from sportsreference.ncaab.boxscore import Boxscores

app = Flask(__name__)

class GameNode:
   def __init__(self, game, date):
      self.team = game["winning_name"]
      self.opponent = game["losing_name"]

      if(game["home_name"] == game["winning_name"]):
          self.winner_score = game["home_score"]
          self.loser_score = game["away_score"]
      else:
          self.winner_score = game["away_score"]
          self.loser_score = game["home_score"]

      self.home_team = game["home_name"]
      self.date = date

   def __str__(self):
     print("beat %s by %d @ %s" % opponent, winner_score - loser_score, home_team)


@app.route('/wins', methods=['GET'])
def get_wins():
    request_params = request.values
    team = request_params['team']

    data = {}
    try:
        with open('data/current_season_graph.json', 'r') as f:
            graph_json = f.read()
            data = json.loads(graph_json)
    except OSError as e:
        print(e)

    response = {"updated": data["updated"], "wins" : data["graph"][team]}
    return json.dumps(response)


if __name__ == '__main__':
    app.run(debug=True)
