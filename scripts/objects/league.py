from google.appengine.ext import db
from usermeta import UserMeta
from game import Game
import math
import random

from ..utilities import *

class League(db.Model):
  def createLeague(self,teams):
    league_teams=[]
    for t in teams:
      team=LeagueTeam(user=t)
      t.league=True
      save_user(t)
      team.put()
      league_teams.append(team)
    self.createFixture(league_teams)
    
  def createFixture(self,teams):
    """
    Fixtures: 4 pools of 4, round robin (3 rounds) then semis
    
    Round robin: AvB,CvD;
                 AvC,BvD;
                 AvD,BvC;
    """
    # Assumes 16 teams exactly
    pools=self.createPools(teams=teams)
    for p in pools:
      p.roundRobin()
    
  def createPools(self,teams):
    if len(teams) < 4:
      return
    numPerPool=int(math.ceil(float(len(teams))/4))
    random.shuffle(teams)
    poolA=Pool(league=self)
    poolB=Pool(league=self)
    poolC=Pool(league=self)
    poolD=Pool(league=self)
    for p in [poolA,poolB,poolC,poolD]:
      p.put()
    for i in range(0,4):
      teams[i].pool=poolA
      teams[4+i].pool=poolB
      teams[8+i].pool=poolC
      teams[12+i].pool=poolD
    for t in teams:
      t.put()
    return [poolA,poolB,poolC,poolD]

class Pool(db.Model):
  league=db.ReferenceProperty(League)
  
  def roundRobin(self):
    teams=self.leagueteam_set
    Match(pool=self,round=1,teamA=teams[0],teamB=teams[1]).put()
    Match(pool=self,round=1,teamA=teams[2],teamB=teams[3]).put()
    Match(pool=self,round=2,teamA=teams[0],teamB=teams[2]).put()
    Match(pool=self,round=2,teamA=teams[1],teamB=teams[3]).put()
    Match(pool=self,round=3,teamA=teams[0],teamB=teams[3]).put()
    Match(pool=self,round=3,teamA=teams[1],teamB=teams[2]).put()

class LeagueTeam(db.Model):
  user=db.ReferenceProperty(UserMeta)
  wins=db.IntegerProperty(default=0)
  losses=db.IntegerProperty(default=0)
  draws=db.IntegerProperty(default=0)
  points=db.IntegerProperty(default=0)
  percentage=db.IntegerProperty(default=0)
  pool=db.ReferenceProperty(Pool)
  
  def set_wins(self,wins):
    self.wins=wins
    self.points=4*self.wins+2*self.draws
  
  def set_draws(self,draws):
    self.draws=draws
    self.points=4*self.wins+2*self.draws    

class Match(db.Model):
  round=db.IntegerProperty(required=True)
  pool=db.ReferenceProperty(Pool)
  league=db.ReferenceProperty(League)
  teamA=db.ReferenceProperty(LeagueTeam,collection_name="teamA_set")
  teamB=db.ReferenceProperty(LeagueTeam,collection_name="teamB_set")
  winner=db.IntegerProperty(default=0)
  played=db.BooleanProperty(default=False)