import sys
import os
import json
import boto3
from datetime import datetime
from collections import defaultdict

from sportsreference.ncaab.boxscore import Boxscores

class GameNode:
   def __init__(self, game, date):
      # self.team = game["winning_name"]
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


now = datetime.now()
all_games_data = Boxscores(datetime(now.year, 12, 15), now)
data = all_games_data.games

graph = defaultdict(list)

for date in data.keys():
    games = data[date]

    for game in games:
        winner = game["winning_name"]

        # Only add D1 games
        if(game["non_di"] != True):
            game_record = GameNode(game, date)
            graph[winner].append(game_record.__dict__)

dict_to_write = {"updated":datetime.now().strftime("%x at %I:%M %p"), "graph":graph}
json_to_write = json.dumps(dict_to_write)

open('current_season.json', 'w').write(json_to_write)

s3_client = boto3.client('s3',
                      aws_access_key_id=os.environ['aws_access_key_id'],
                      aws_secret_access_key=os.environ['aws_secret_access_key'],
                      region_name=os.environ['region']
                      )

s3_client.upload_file('current_season.json', 'graphs-cbbchaingame', 'current_season_graph.json')
