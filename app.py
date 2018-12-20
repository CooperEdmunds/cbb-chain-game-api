from flask import Flask, jsonify
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

@app.route('/chains', methods=['GET'])
def get_chains():
    # team_one = request.json['team_one']
    # team_two = request.json['team_two']
    # start_date = request.json['start_date']
    # end_date = request.json['end_date']

    team_one = "duke"
    team_two = "purdue"
    start_date = "2018-10-15"
    end_date = "2018-12-15"

    all_games_data = Boxscores(datetime(2018, 10, 30), datetime(2018, 11, 20))
    data = all_games_data.games

    graph = defaultdict(list)

    for date in data.keys():
        games = data[date]

        for game in games:
            winner = game["winning_name"]

            game_record = GameNode(game, date)
            graph[winner].append(game_record.__dict__)

    return jsonify(graph)

if __name__ == '__main__':
    app.run(debug=True)
