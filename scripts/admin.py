#!/usr/bin/env python

import webapp2
import jinja2
import os
from datetime import date
import logging

from objects.usermeta import UserMeta
from objects.player import Player
from objects.player import PlayerGame
from objects.team import Team
from objects.game import Game
from google.appengine.api import memcache
import utilities
from utilities import *
from google.appengine.api import users
from google.appengine.ext import db
from scores import *

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
jinja_environment.globals['logout']=users.create_logout_url('/')
jinja_environment.globals['page']='admin'

def check_admin(request):
  user=get_meta()
  if not user.admin:
    request.redirect('/')
    
def toggle_lockout(request):
  check_admin(request)
  utilities.toggle_lockout()
  return webapp2.redirect('/admin')

class MenuHandler(webapp2.RequestHandler):
  def get(self):
    check_admin(self)
    template_values={'user_meta':get_meta(),'lockout':lockout()}
    games=Game.all().order('round').run()
    template_values['games']=games
    template=jinja_environment.get_template('templates/admin_menu.html')
    self.response.out.write(template.render(template_values))   

class EditGameHandler(webapp2.RequestHandler):
  def get(self,game_id):
    check_admin(self)
    game=Game.get_by_id(int(game_id))
    players=Player.all().filter('active =',True).order('surname').fetch(1000)
    fielders=PlayerGame.all().filter('game =',game)
    batting_order=sorted(fielders,key=lambda p: p.batting_position)
    bowling_order=sorted(fielders,key=lambda p: p.bowling_position)
    template_values={'user_meta':get_meta(),'game':game,'players':players,'dismissal_types':dismissal_types,'batting_order':batting_order,'bowling_order':bowling_order,
      'fielders':fielders}
    template=jinja_environment.get_template('templates/edit_game.html')
    self.response.out.write(template.render(template_values))
    
  def post(self):
    players={}
    check_admin(self)
    game=Game.get_by_id(int(self.request.get('game')))
    batsmen=[]
    bowlers=[]
    fielders=[]
    
    # TODO: convert to a background task
        
    # Check Duplicates
    for i in range(1,13):
      if self.request.get('batsman-'+str(i)+'-batted'):
        batsmen.append(self.request.get('batsman-'+str(i)))
      if self.request.get('bowler-'+str(i)+'-bowled'):
        bowlers.append(self.request.get('bowler-'+str(i)))
      if self.request.get('fielder-'+str(i)) != '0':
        fielders.append(self.request.get('fielder-'+str(i)))
    
    if len(set(batsmen)) != len(batsmen):
      self.response.out.write("Error. Duplicate batsmen")
      return
    if len(set(bowlers)) != len(bowlers):
      self.response.out.write("Error. Duplicate bowlers")
      return
    if len(set(fielders)) != len(fielders):
      self.response.out.write("Error. Duplicate fielders")
      return
    
    memcache.delete('horse')
    pg=None
    # batting
    for i in range(1,12):
      si='batsman-'+str(i)
      if not self.request.get(si+'-batted') or self.request.get(si) == '0':
        continue
      p_id=self.request.get(si)
      try:
        pg=players[p_id]
      except:
        player=Player.get_by_id(int(p_id))
        pg=PlayerGame(player=player,game=game)
        players[p_id]=pg
      pg.batted=True
      if self.request.get(si+'-not_out'):
        pg.not_out=True
      else:
        pg.not_out=False
      pg.runs=int(self.request.get(si+'-runs',default_value="0"))
      pg.balls_faced=int(self.request.get(si+'-balls',default_value="0"))
      pg.fours_hit=int(self.request.get(si+'-fours',default_value="0"))
      pg.sixes_hit=int(self.request.get(si+'-sixes',default_value="0"))
      if not pg.not_out:
        pg.how_out=db.Category(self.request.get(si+'-how_out').replace('-',' '))
      else:
        pg.how_out=None
      pg.batting_position=i
    
    # bowling
    total_conceded=0
    for i in range(1,12):
      si='bowler-'+str(i)
      if not self.request.get(si+'-bowled') or self.request.get(si) == '0':
        continue
      p_id=self.request.get(si)
      try:
        pg=players[p_id]
      except:
        player=Player.get_by_id(int(p_id))
        pg=PlayerGame(player=player,game=game)
        players[p_id]=pg
      pg.bowled=True
      overs_tokens=self.request.get(si+'-overs',default_value="0.0").split('.')
      pg.overs=int(overs_tokens[0])
      if len(overs_tokens) > 1:
        pg.balls=int(overs_tokens[1])
      else:
        pg.balls=0
      pg.maidens=int(self.request.get(si+'-maidens',default_value="0"))
      pg.runs_conceded=int(self.request.get(si+'-runs',default_value="0"))
      total_conceded+=pg.runs_conceded
      pg.wickets=int(self.request.get(si+'-wickets',default_value="0"))
      pg.wides=int(self.request.get(si+'-wides',default_value="0"))
      pg.no_balls=int(self.request.get(si+'-no_balls',default_value="0"))
      pg.fours=int(self.request.get(si+'-fours',default_value="0"))
      pg.sixes=int(self.request.get(si+'-sixes',default_value="0"))
      pg.bowling_position=i
    
    # fielding
    for i in range(1,13):
      si='fielder-'+str(i)
      if self.request.get(si)=='0':
        continue
      p_id=self.request.get(si)
      try:
        pg=players[p_id]
      except:
        player=Player.get_by_id(int(p_id))
        pg=PlayerGame(player=player,game=game)
        players[p_id]=pg
      pg.catches=int(self.request.get(si+'-catches',default_value="0"))
      pg.drops=int(self.request.get(si+'-drops',default_value="0"))
      pg.diving_drops=int(self.request.get(si+'-diving',default_value="0"))
      pg.non_attempts=int(self.request.get(si+'-non_attempts',default_value="0"))
      pg.run_outs=int(self.request.get(si+'-run_outs',default_value="0"))
      pg.misfields=int(self.request.get(si+'-misfields',default_value="0"))
      pg.other=int(self.request.get(si+'-other',default_value="0"))
      
    # TODO: Validation
    for pg in game.playergame_set:
      pg.delete()
    
    bat_total=0
    bowl_total=0
    bat_scores={}
    bowl_scores={}
    for key,pg in players.iteritems():
      bat_scores[key]=batting_score(pg)
      bat_total+=bat_scores[key]
      bowl_scores[key]=bowling_score(pg,total_conceded)
      bowl_total+=bowl_scores[key]
      pg.fielding_points=fielding_score(pg)
  
    bat_factor = 1
    bowl_factor = 1
    if bat_total > 0:    
      bat_factor = 100.0/bat_total
    if bowl_total > 0:
      if game.overs == 20:
        bowl_factor = 80.0/bowl_total
      else:
        bowl_factor = 100.0/bowl_total
    for key,pg in players.iteritems():
      pg.batting_points=int(round(bat_scores[key]*bat_factor))
      pg.bowling_points=int(round(bowl_scores[key]*bowl_factor))
      pg.put()
      
    completed=self.request.get('completed')
    if completed:
      game_completed(game)
      for key,pg in players.iteritems():
        p=pg.player
        update_prices(p)
        p.put()
    else:
      game.played=False
    game.opposition=self.request.get('opposition')
    game.score=self.request.get('dedication-score')
    game.opposition_score=self.request.get('opposition-score')
    game.result=self.request.get('result')
    game.put()
    
    self.redirect('/admin')
  
class HorseHandler(webapp2.RequestHandler):
  def get(self):
    check_admin(self)
    template_values={'user_meta':get_meta()}
    
    player_scores = memcache.get('horse')
    if player_scores is None:    
      players=Player.all().run()
      player_scores=[]
      for p in players:
        score=0
        games=p.playergame_set
        for g in games:
          if g.batted and not g.not_out and g.how_out == 'bowled':
            score += 1
          if g.batted and g.runs == 0 and not g.not_out:
            if g.balls_faced <= 1:
              score += 4
            else:
              score += 3
          score += 2*g.sixes
          score += 3*g.drops + g.diving_drops + 4*g.non_attempts + g.misfields + g.other
        player_scores.append([p.first_name + ' ' + p.surname,score])
        player_scores=sorted(player_scores,key=lambda player: -player[1])
      memcache.add('horse',player_scores)
        
    template_values['player_scores']=player_scores
    template=jinja_environment.get_template('templates/horse.html')
    self.response.out.write(template.render(template_values))
    

class ResetHandler(webapp2.RequestHandler):
  def get(self):
    check_admin(self)
    template_values={'user_meta':get_meta()}
    template=jinja_environment.get_template('templates/reset.html')
    self.response.out.write(template.render(template_values))
    
  def post(self):
    if self.request.get('code')!='RESET':
      return self.response.out.write("Reset failed. No harm done")
    check_admin(self)
    players=Player.all().run()
    for p in players:
      p.batting_price=p.initial_batting_price
      p.bowling_price=p.initial_bowling_price
      p.fielding_price=p.initial_fielding_price
      p.put()
		
    usermetas=UserMeta.all().run()
    for u in usermetas:
      u.total_trades=10
      u.round_trades=2
      u.total_points=0
      u.put()
    
    teams=Team.all().run()
    for t in teams:
      if t.game.round > 1:
        t.delete()
      else:
        t.batting_score=0
        t.bowling_score=0
        t.fielding_score=0
        t.total_score=0
        t.put()
        
    playergames=PlayerGame.all().run()
    for p in playergames:
      p.delete()
      
    games=Game.all().run()
    for g in games:
      g.played=False
      g.result='tie'
      g.score="0/0"
      g.opposition_score="0/0"
      g.batExtras=0
      g.bowlExtras=0
      g.put()
      
    u=Utilities.all().get()
    u.current_round=1
    u.next_game=Game.all().filter('round =',1).get()
    u.lockout=False
    u.put()
    
    memcache.flush_all()
    self.response.out.write('System reset. I hope you meant to do that!');
    
class ScriptHandler(webapp2.RequestHandler):
  def get(self):
    check_admin(self)
    us=UserMeta.all().run()
    for u in us:
      budget=209000
      team=Team.all().filter('user =',u).get()
      if team:
        for k in team.batsmen:
          p=db.get(k)
          budget -= p.batting_price
        for k in team.bowlers:
          p=db.get(k)
          budget -= p.bowling_price
        for k in team.fielders:
          p=db.get(k)
          budget -= p.fielding_price
        u.budget = budget
        save_user(u)


class InitHandler(webapp2.RequestHandler):
  def get(self):
    check_admin(self)
    games=Game.all().run()
    for g in games:
      g.delete()
    days=[26,27,28,28,29,30]
    for i in range(1,6):
      g=Game(round=i,date=date(2012,12,days[i]))
      g.put()
    us=Utilities.all().run()
    for u in us:
      u.delete()
    u=Utilities()
    u.current_round=1
    u.next_game=Game.all().filter('round =',1).get()
    u.put()
    teams=Team.all().run()
    for t in teams:
      t.delete()
    games=PlayerGame.all().run()
    for g in games:
      g.delete()
    self.response.out.write('done')
    player=Player(first_name="any",surname="player",active=False)
    player.put()

app = webapp2.WSGIApplication([('/admin',MenuHandler),
                               ('/admin/toggle_lockout',toggle_lockout),
                               ('/admin/game',EditGameHandler),
                               ('/admin/reset',ResetHandler),
                               ('/admin/horse',HorseHandler),
                               ('/admin/script',ScriptHandler),
                               webapp2.Route('/admin/game/<game_id>',handler=EditGameHandler)],debug=True)