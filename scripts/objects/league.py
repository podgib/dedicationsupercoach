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
  
class League(db.Model):
  teams=db.ListProperty(int)
  matches=db.ListProperty(db.Key)
  poolA=db.ListProperty(int,default=[])
  poolB=db.ListProperty(int,default=[])
  poolC=db.ListProperty(int,default=[])
  poolD=db.ListProperty(int,default=[])
  
  def createFixture(self):
    # Assumes 16 teams exactly
    self.createPools(4)
    
  def createPools(self):
    numPerPool=int(math.ceil(float(len(self.teams))/4))
    
    return pools