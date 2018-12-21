import json
import os
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

    s3_client = boto3.client('s3',
                          aws_access_key_id=os.environ['aws_access_key_id'],
                          aws_secret_access_key=os.environ['aws_secret_access_key'],
                          region_name=os.environ['region']
                          )

    s3_client.download_file('graphs-cbbchaingame', 'current_season_graph.json', 'current_season.json')

    data = json.loads(open('current_season.json').read())

    response = {"updated": data["updated"], "wins" : data["graph"][team]}
    return json.dumps(response)


if __name__ == '__main__':
    app.run(debug=True)
