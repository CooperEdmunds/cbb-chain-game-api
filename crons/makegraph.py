import sys
import json
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
print("starting query")
sys.stdout.flush()
all_games_data = Boxscores(datetime(now.year, 12, 1), now)
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

print("done 1")
sys.stdout.flush()
dict_to_write = {"updated":datetime.now().strftime("%x at %I:%M %p"), "graph":graph}
json_to_write = json.dumps(dict_to_write)
print("done 2")
sys.stdout.flush()
with open("data/current_season_graph.json", 'w') as f:
    f.seek(0)
    f.truncate()

    f.write(json_to_write)
print("done 3")
sys.stdout.flush()
