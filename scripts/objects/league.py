from google.appengine.ext import db
from usermeta import UserMeta
from game import Game
import math
import random

class Match(db.Model):
  round=db.IntegerProperty(required=True)
  pool=db.ReferenceProperty(Pool)
  teamA=db.ReferenceProperty(UserMeta,collection_name="teamA_set")
  teamB=db.ReferenceProperty(UserMeta,collection_name="teamB_set")
  winner=db.IntegerProperty(default=0)
  played=db.BooleanProperty(default=False)
  
class Pool(db.Model):
  teams=db.ListProperty(db.Key,default=[])
  
  def roundRobin(self):
    Match(pool=self,round=1,teamA=teams[0],teamB=teams[1]).put()
    Match(pool=self,round=1,teamA=teams[2],teamB=teams[3]).put()
    Match(pool=self,round=2,teamA=teams[0],teamB=teams[2]).put()
    Match(pool=self,round=2,teamA=teams[1],teamB=teams[3]).put()
    Match(pool=self,round=3,teamA=teams[0],teamB=teams[3]).put()
    Match(pool=self,round=3,teamA=teams[1],teamB=teams[2]).put()
  
class LeagueTeam(db.Model):
  user=db.ReferenceProperty(UserMeta)
  league=db.ReferenceProperty(League)
  wins=db.IntegerProperty(default=0)
  losses=db.IntegerProperty(default=0)
  draws=db.IntegerProperty(default=0)
  percentage=db.FloatProperty(default=0.0)
  pool=db.ReferenceProperty(Pool)
  
class League(db.Model):
  matches=db.ListProperty(db.Key,default=[])
  pools=db.ListProperty(db.Key,default=[])
    
  def createFixture(self,teams=None):
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
    
    
  def createPools(self,teams=None):
    if teams==None:
      teams=list(self.usermeta_set)
    if len(self.teams) < 4:
      return
    numPerPool=int(math.ceil(float(len(self.teams))/4))
    random.shuffle(teams)
    poolA=Pool(teams=teams[0:numPerPool]).put()
    poolB=Pool(teams=teams[numPerPool:2*numPerPool]).put()
    poolC=Pool(teams=teams[2*numPerPool:3*numPerPool]).put()
    poolD=Pool(teams=teams[3*numPerPool:4*numPerPool]).put()
    for p in [poolA,poolB,poolC,poolD]:
      self.pools.append(p.key())
    return [poolA,poolB,poolC,poolD]
    
  def createMatches(self):
  if matches and len(matches) > 