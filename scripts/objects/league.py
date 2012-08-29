from google.appengine.ext import db
from usermeta import UserMeta
from game import Game
import math
import random

class Match(db.Model):
  round=db.IntegerProperty(required=True)
  pool=db.ReferenceProperty(Pool)
  league=db.ReferenceProperty(League)
  teamA=db.ReferenceProperty(UserMeta,collection_name="teamA_set")
  teamB=db.ReferenceProperty(UserMeta,collection_name="teamB_set")
  winner=db.IntegerProperty(default=0)
  played=db.BooleanProperty(default=False)
  
class Pool(db.Model):
  teams=db.ListProperty(db.Key,default=[])
  league=db.ReferenceProperty(League)
  
  def roundRobin(self):
    Match(pool=self,round=1,teamA=teams[0],teamB=teams[1]).put()
    Match(pool=self,round=1,teamA=teams[2],teamB=teams[3]).put()
    Match(pool=self,round=2,teamA=teams[0],teamB=teams[2]).put()
    Match(pool=self,round=2,teamA=teams[1],teamB=teams[3]).put()
    Match(pool=self,round=3,teamA=teams[0],teamB=teams[3]).put()
    Match(pool=self,round=3,teamA=teams[1],teamB=teams[2]).put()
  
class League(db.Model):
  def createLeague(self,teams):
    for team in teams:
      team.league=self
      team.wins=0
      team.losses=0
      team.ties=0
      team.percentage=0
    createFixture(self,teams)
    
  def createFixture(self,teams):
    """
    Fixtures: 4 pools of 4, round robin (3 rounds) then semis
    
    Round robin: AvB,CvD;
                 AvC,BvD;
                 AvD,BvC;
    """
    # Assumes 16 teams exactly
    pools=self.createPools(4,teams)
    for p in pools:
      p.roundRobin()
    
    
  def createPools(self,teams):
    if len(self.teams) < 4:
      return
    numPerPool=int(math.ceil(float(len(self.teams))/4))
    random.shuffle(teams)
    poolA=Pool(league=self,teams=teams[0:numPerPool]).put()
    poolB=Pool(league=self,teams=teams[numPerPool:2*numPerPool]).put()
    poolC=Pool(league=self,teams=teams[2*numPerPool:3*numPerPool]).put()
    poolD=Pool(league=self,teams=teams[3*numPerPool:4*numPerPool]).put()
    return [poolA,poolB,poolC,poolD]