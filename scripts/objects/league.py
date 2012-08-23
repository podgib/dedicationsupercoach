from google.appengine.ext import db
from usermeta import UserMeta
from game import Game
import math
import random

class Match(db.Model):
  round=db.IntegerProperty(required=True)
  game=db.ReferenceProperty(Game)
  teamA=db.ReferenceProperty(UserMeta,collection_name="teamA_set")
  teamB=db.ReferenceProperty(UserMeta,collection_name="teamB_set")
  winner=db.IntegerProperty(default=0)
  played=db.BooleanProperty(default=False)
  
class Pool(db.Model):
  teams=db.ListProperty(db.Key,default=[])
  
class LeagueTeam(db.Model):
  user=db.ReferenceProperty(UserMeta)
  wins=db.IntegerProperty(default=0)
  losses=db.IntegerProperty(default=0)
  draws=db.IntegerProperty(default=0)
  percentage=db.FloatProperty(default=0.0)
  
class League(db.Model):
  matches=db.ListProperty(db.Key,default=[])
  poolA=db.ListProperty(db.Key,default=[])
  poolB=db.ListProperty(db.Key,default=[])
  poolC=db.ListProperty(db.Key,default=[])
  poolD=db.ListProperty(db.Key,default=[])
  
  def createFixture(self):
    # Assumes 16 teams exactly
    self.createPools(4)
    
  def createPools(self):
    if len(self.teams) < 4:
      return
    numPerPool=int(math.ceil(float(len(self.teams))/4))
    teams=list(self.usermeta_set)
    random.shuffle(teams)
    self.poolA=teams[0:numPerPool]
    self.poolB=teams[numPerPool:2*numPerPool]
    self.poolC=teams[2*numPerPool:3*numPerPool]
    self.poolD=teams[3*numPerPool:4*numPerPool]
    return [poolA,poolB,poolC,poolD]
    
  def createMatches(self):
  if matches and len(matches) > 