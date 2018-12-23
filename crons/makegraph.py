import sys
import os
import json
import boto3
import pytz
from datetime import datetime, tzinfo
from collections import defaultdict

from sportsreference.ncaab.boxscore import Boxscores

class GameNode:
   def __init__(self, game):
      self.team = game["winning_name"]
      self.opponent = game["losing_name"]
      self.differential = abs(game["home_score"] - game["away_score"])


# Instantiate S3 client
s3_client = boto3.client('s3',
                      aws_access_key_id=os.environ['aws_access_key_id'],
                      aws_secret_access_key=os.environ['aws_secret_access_key'],
                      region_name=os.environ['region']
                      )

last_updated = datetime(datetime.utcnow().year, 8, 15)
current_graph = {}
try:
  # Get the graph stored in S3 and write it to a local file
  s3_client.download_file(os.environ['bucket'], 'current_season_graph.json', 'current_graph.json')
  data = json.loads(open('current_graph.json').read())
  os.remove('current_graph.json')

  # Parse last updated date
  last_updated_str = data['updated']
  last_updated = datetime.strptime(last_updated_str, "%x at %I:%M %p")

  current_graph = data['graph']
except:
  pass

# Get the games between the last updated date and now
all_games_data = Boxscores(last_updated, datetime.utcnow())
data = all_games_data.games

new_graph = defaultdict(list)

# Add all of the nodes from the current graph
for team in current_graph.keys():
    new_graph[team].extend(current_graph[team])

# Iterate over all of the new games just fetched
for date in data.keys():
    games = data[date]

    for game in games:
        winner = game["winning_name"]

        # Only add D1 games
        if(game["non_di"] != True and game['winning_name'] != None):
            game_record = GameNode(game)
            # If this game isn't already in the graph, add it
            if(game_record.__dict__ not in new_graph[winner]):
                new_graph[winner].append(game_record.__dict__)

# Convert the new graph and time to a json file
dict_to_write = {"updated":datetime.utcnow().strftime("%x at %I:%M %p"), "graph":new_graph}
json_to_write = json.dumps(dict_to_write)
open('new_graph.json', 'w').write(json_to_write)

# Upload the json file to S3
s3_client.upload_file('new_graph.json', os.environ['bucket'], 'current_season_graph.json')

os.remove('new_graph.json')
