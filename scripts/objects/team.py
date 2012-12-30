from google.appengine.ext import db

from game import Game
from usermeta import UserMeta
from player import *

class Team(db.Model):
  user=db.ReferenceProperty(UserMeta,required=True)
  game=db.ReferenceProperty(Game,required=True)
  batting_score=db.IntegerProperty(default=0)
  bowling_score=db.IntegerProperty(default=0)
  fielding_score=db.IntegerProperty(default=0)
  total_score=db.IntegerProperty(default=0)
  
  batsmen=db.ListProperty(db.Key,default=[])
  bowlers=db.ListProperty(db.Key,default=[])
  fielders=db.ListProperty(db.Key,default=[])
  
  captain=db.ReferenceProperty(Player)
  captain_type=db.CategoryProperty()

  def copy_to_next_round(self):
    game=Game.all().filter('round =',self.game.round+1).get()
    t=Team(user=self.user,batsmen=self.batsmen,bowlers=self.bowlers,fielders=self.fielders,game=game,captain=self.captain,captain_type=self.captain_type)
    t.put()
    self.user.round_trades = min(self.user.total_trades,2)

  def calculate_scores(self):
    prior_score=self.user.total_points-self.batting_score-self.bowling_score-self.fielding_score
    batting_score=0
    bowling_score=0
    fielding_score=0

    batsmen=PlayerGame.all().filter("game =",self.game).filter("player IN",self.batsmen).run()
    bowlers=PlayerGame.all().filter("game =",self.game).filter("player IN",self.bowlers).run()
    fielders=PlayerGame.all().filter("game =",self.game).filter("player IN",self.fielders).run()
    captain=PlayerGame.all().filter("game =",self.game).filter("player =",self.captain).get()
    for b in batsmen:
      batting_score+=b.batting_points
    for b in bowlers:
      bowling_score+=b.bowling_points
    for b in fielders:
      fielding_score+=b.fielding_points
      
    if captain:
      if self.captain_type == 'bat':
        batting_score+=captain.batting_points
      elif self.captain_type == 'bowl':
        bowling_score+=captain.bowling_points
      elif self.captain_type == 'field':
        fielding_score+=captain.fielding_points
    
    self.batting_score = batting_score
    self.bowling_score = bowling_score
    self.fielding_score = fielding_score
    self.total_score = batting_score+bowling_score+fielding_score
    if self.user:
      self.user.total_points = prior_score + self.total_score
      self.user.put()
    self.put()
    
  
  def drop_player(self,player,type):
    list=[]
    if type == 'batsman':
      list=self.batsmen
    elif type == 'bowler':
      list=self.bowlers
    elif type == 'fielder':
      list=self.fielders
    if player.key() in list:
      list.remove(player.key())
      return True
    else:
      return False
      
  def pick_player(self,player,type):
    if type == 'batsman':
      list=self.batsmen
    elif type == 'bowler':
      list=self.bowlers
    elif type == 'fielder':
      list=self.fielders
    if player.key() in list:
      return False
    else:
      list.append(player.key())
      return True
    
def finish_round(game,next_game):
  teams=Team.all().filter('game =',game).run()
  for team in teams:
    team.calculate_scores()
    if not game.played and next_game:
      team.copy_to_next_round()

