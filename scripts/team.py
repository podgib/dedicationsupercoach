#!/usr/bin/env python

import webapp2
import jinja2
import os

from objects.usermeta import UserMeta
from objects.player import *
from objects.team import Team
from utilities import *
from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
jinja_environment.globals['logout']=users.create_logout_url('/')
jinja_environment.globals['page']='team'

class SelectHandler(webapp2.RequestHandler):
  def get(self):
    user=get_meta()
    if not user:
      self.redirect("/")
    team=Team.all().filter("user =",user).get()
    if team:
      self.redirect("/team/edit")
    players=Player.all().filter("active =",True).fetch(100)
    template_values={'user_meta':user,'players':players,'budget':user.budget}
    template=jinja_environment.get_template('templates/select_team.html')
    self.response.out.write(template.render(template_values))
    
  def post(self):
    user_meta=get_meta()
    if not user_meta:
      self.redirect("/")
    team=Team.all().filter('user =',user_meta).get()
    if team:
      self.redirect("/team/edit")
    team = Team(user=user_meta,game=next_game())
    budget=user_meta.budget
    
    selected_batsmen=self.request.get_all('batting')
    selected_bowlers=self.request.get_all('bowling')
    selected_fieldsmen=self.request.get_all('fielding')
    
    if len(selected_batsmen) > 5 or len(selected_bowlers) > 3 or len(selected_fieldsmen) > 3:
      self.response.out.write("Error: too many selected")
      return
    
    if not self.request.get('captain'):
      self.response.out.write("Error: no captain selected")
      return
      
    captain=self.request.get('captain').split(':',1)
    if captain[0] not in ['bat','bowl','field']:
      self.response.out.write("Error: invalid captain selection")
      return
    if captain[0] == 'bat' and captain[1] not in selected_batsmen:
      self.response.out.write("Error: captain must be a member of team")
      return
    if captain[0] == 'bowl' and captain[1] not in selected_bowlers:
      self.response.out.write("Error: captain must be a member of team")
      return
    if captain[0] == 'field' and captain[1] not in selected_fieldsmen:
      self.response.out.write("Error: captain must be a member of team")
      return
    team.captain_type=db.Category(captain[0])
    team.captain=db.get(captain[1])
    
    for key in selected_batsmen:
      player=db.get(key)
      budget-=player.batting_price
      team.batsmen.append(player.key())
    
    for key in selected_bowlers:
      player=db.get(key)
      budget-=player.bowling_price
      team.bowlers.append(player.key())
      
    for key in selected_fieldsmen:
      player=db.get(key)
      budget-=player.fielding_price
      team.fielders.append(player.key())
      
    if budget < 0:
      self.response.out.write("You went over budget")
      return
      
    #if team.game.round > 1:
    #  team1=Team(user=team.user,game=Game.all().filter('round =',1).get(),batsmen=team.batsmen,bowlers=team.bowlers,fielders=team.fielders,captain=team.captain,captain_type=team.captain_type)
    #  team1.put()
      
    team.put()
    user_meta.budget = budget
    save_user(user_meta)
    
    self.redirect('/team')

class ViewHandler(webapp2.RequestHandler):
  def view_game(self,team_id=None):
    user_meta=get_meta()
    if not user_meta:
      self.redirect("/")
    team_user=None
    if team_id:
      team_user=UserMeta.get_by_id(int(team_id))
    else:
      team_user=get_meta()
    
    round=int(self.request.get('round'))
    game=Game.all().filter("round =",round).get()
    team=get_team(team_user,game)
    
    if not team:
      self.response.out.write("Error: team not found")
      return
    
    batsmen=[]
    dnbat=[]
    bowlers=[]
    dnbowl=[]
    fielders=[]
    dnf=[]
    
    batsmen=PlayerGame.all().filter("game =",game).filter("player IN",team.batsmen).run()
    bowlers=PlayerGame.all().filter("game =",game).filter("player IN",team.bowlers).run()
    fielders=PlayerGame.all().filter("game =",game).filter("player IN",team.fielders).run()
      
    template_values={'user_meta':user_meta,'lockout':lockout(),'current_round':current_round,'batsmen':batsmen,'bowlers':bowlers,'fielders':fielders,'team':team,'game':game}
    if check_mobile():
      template=jinja_environment.get_template('templates/mobile/game.html')
    else:
      template=jinja_environment.get_template('templates/game.html')
    self.response.out.write(template.render(template_values))

  def get(self,team_id=None):
    user_meta=get_meta()
    if not user_meta:
      self.redirect("/")
    if self.request.get('round'):
      self.view_game(team_id)
      return
    team_user=None
    if team_id:
      team_user=UserMeta.get_by_id(int(team_id))
    else:
      team_user = get_meta()
    game=next_game()
    round=current_round()-1
    if round < 0:
      round = 5
    if not game:
      game=Game.all().filter("round =", round).get()
    
    team=get_team(team_user,game)
    if not team:
      if team_user.key()!=user_meta.key():
        self.response.out.write("Error: team not found")
      else:
        self.redirect('/team/select')
      return
    batsmen=[]
    bowlers=[]
    fielders=[]
    for key in team.batsmen:
      batsmen.append(Player.get(key))
    for key in team.bowlers:
      bowlers.append(Player.get(key))
    for key in team.fielders:
      fielders.append(Player.get(key))
    template_values={'user_meta':user_meta,'lockout': lockout(),'current_round':current_round(),'batsmen':batsmen,'bowlers':bowlers,'fielders':fielders,'team_user':team_user,'team':team}
    if check_mobile():
      template=jinja_environment.get_template('templates/mobile/view_team.html')
    else:
      template=jinja_environment.get_template('templates/view_team.html')
    self.response.out.write(template.render(template_values))
    
class EditHandler(webapp2.RequestHandler):
  def get(self):
    if lockout():
      self.response.out.write('Lockout in place')
      return
    user = get_meta()
    if not user:
      self.redirect("/")
    game = next_game()
    team=get_team(user,game)
    template_values={'user_meta':user,'lockout':lockout(),'budget':user.budget,'round_trades':user.round_trades,'total_trades':user.total_trades}
    
    template_values['selected_batsmen'], template_values['available_batsmen'] = selected_available(team.batsmen)
    
    template_values['selected_bowlers'], template_values['available_bowlers'] = selected_available(team.bowlers)
    
    template_values['selected_fielders'], template_values['available_fielders'] = selected_available(team.fielders)
    
    template_values['captain_type']=team.captain_type
    template_values['captain']=team.captain
    
    template=jinja_environment.get_template('templates/edit_team.html')
    self.response.out.write(template.render(template_values))
    
  def post(self):
    if lockout():
      self.response.out.write('Lockout in place')
      return
    user = get_meta()
    if not user:
      self.redirect("/")
    game = next_game()
    team=get_team(user,game)
    # batsmen
    dropped_batsmen = self.request.get_all('dropped_batsmen')
    picked_batsmen = self.request.get_all('picked_batsmen')
    dropped_bowlers = self.request.get_all('dropped_bowlers')
    picked_bowlers = self.request.get_all('picked_bowlers')
    dropped_fielders = self.request.get_all('dropped_fielders')
    picked_fielders = self.request.get_all('picked_fielders')
    
    trades = len(picked_batsmen)+len(picked_bowlers)+len(picked_fielders)
    if trades > user.round_trades:
      self.response.out.write("Error: insufficient trades remaining")
      return
    
    user.round_trades -= trades
    user.total_trades -= trades
    
    captain=self.request.get('captain')
    if(captain):
      tokens=captain.split(':',1)
      captain_player=Player.get_by_id(int(tokens[1]))
      if tokens[0] not in ['bat','bowl','field']:
        self.response.out.write("Error: invalid captain selection")
        return
      if tokens[0] == 'bat' and (tokens[1] in dropped_batsmen or captain_player.key() not in team.batsmen):
        self.response.out.write("Error: captain must be a member of team")
        return
      if tokens[0] == 'bowl' and (tokens[1] in dropped_bowlers or captain_player.key() not in team.bowlers):
        self.response.out.write("Error: captain must be a member of team")
        return
      if tokens[0] == 'field' and (tokens[1] in dropped_fielders or captain_player.key() not in team.fielders):
        self.response.out.write("Error: captain must be a member of team")
        return
      team.captain_type=db.Category(tokens[0])
      team.captain=captain_player
    else:
      team.captain=None
      team.captain_type=None
    
    budget=user.budget
    for p in dropped_batsmen:
      player = Player.get_by_id(int(p))
      if team.drop_player(player,'batsman'):
        budget += player.batting_price
      else:
        self.response.out.write("Error: dropped player not in team")
        return
    for p in dropped_bowlers:
      player = Player.get_by_id(int(p))
      if team.drop_player(player,'bowler'):
        budget += player.bowling_price
      else:
        self.response.out.write("Error: dropped player not in team")
        return
    for p in dropped_fielders:
      player = Player.get_by_id(int(p))
      if team.drop_player(player,'fielder'):
        budget += player.fielding_price
      else:
        self.response.out.write("Error: dropped player not in team")
        return
    for p in picked_batsmen:
      player = Player.get_by_id(int(p))
      if team.pick_player(player,'batsman'):
        budget -= player.batting_price
      else:
        self.response.out.write("Error")
        return
    for p in picked_bowlers:
      player = Player.get_by_id(int(p))
      if team.pick_player(player,'bowler'):
        budget -= player.bowling_price
      else:
        self.response.out.write("Error")
        return
    for p in picked_fielders:
      player = Player.get_by_id(int(p))
      if team.pick_player(player,'fielder'):
        budget -= player.fielding_price
      else:
        self.response.out.write("Error")
        return
    
    if budget < 0:
      self.response.out.write("Error: budget exceeded")
      return
    user.budget = budget
    save_user(user)
    team.put()
    self.redirect('/team')
    
class LadderHandler(webapp2.RequestHandler):
  def get(self):
    user_meta=get_meta()
    if not user_meta:
      self.redirect("/")
    teams=UserMeta.all().order('-total_points')
    template_values={'user_meta':user_meta,'page':'ladder','teams':teams}
    if check_mobile():
      template=jinja_environment.get_template('templates/mobile/ladder.html')
    else:
      template=jinja_environment.get_template('templates/ladder.html')
    self.response.out.write(template.render(template_values))
    

app = webapp2.WSGIApplication([('/team/ladder',LadderHandler),
                               ('/team/select',SelectHandler),
                               ('/team',ViewHandler),
                               ('/team/edit',EditHandler),
                               webapp2.Route('/team/<team_id>',handler=ViewHandler)],debug=True)