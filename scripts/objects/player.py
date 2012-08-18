from google.appengine.ext import db
from game import Game

class Player(db.Model):
  first_name=db.StringProperty(required=True)
  surname=db.StringProperty(required=True)
  initial_batting_price=db.IntegerProperty(default=0)
  initial_bowling_price=db.IntegerProperty(default=0)
  initial_fielding_price=db.IntegerProperty(default=0)
  batting_price=db.IntegerProperty(default=0)
  bowling_price=db.IntegerProperty(default=0)
  fielding_price=db.IntegerProperty(default=0)
  active=db.BooleanProperty(default=True)
  description=db.TextProperty()
  
class PlayerGame(db.Model):
  game=db.ReferenceProperty(Game)
  player=db.ReferenceProperty(Player)
  
  # Batting
  batted=db.BooleanProperty(default=False)
  not_out=db.BooleanProperty(default=False)
  runs=db.IntegerProperty(default=0)
  balls_faced=db.IntegerProperty(default=0)
  fours_hit=db.IntegerProperty(default=0)
  sixes_hit=db.IntegerProperty(default=0)
  how_out=db.CategoryProperty()
  batting_position=db.IntegerProperty(default=12)
  batting_points=db.IntegerProperty(default=0)
 
  # Bowling
  bowled=db.BooleanProperty(default=False)
  overs=db.IntegerProperty(default=0)
  balls=db.IntegerProperty(default=0)
  maidens=db.IntegerProperty(default=0)
  runs_conceded=db.IntegerProperty(default=0)
  wickets=db.IntegerProperty(default=0)
  wides=db.IntegerProperty(default=0)
  no_balls=db.IntegerProperty(default=0)
  fours=db.IntegerProperty(default=0)
  sixes=db.IntegerProperty(default=0)
  bowling_position=db.IntegerProperty(default=12)
  bowling_points=db.IntegerProperty(default=0)

  # Fielding
  catches=db.IntegerProperty(default=0)
  drops=db.IntegerProperty(default=0)
  diving_drops=db.IntegerProperty(default=0)
  non_attempts=db.IntegerProperty(default=0)
  run_outs=db.IntegerProperty(default=0)
  misfields=db.IntegerProperty(default=0)
  other=db.IntegerProperty(default=0)
  fielding_points=db.IntegerProperty(default=0)
