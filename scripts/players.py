#!/usr/bin/env python

import webapp2
import jinja2
import os

from objects.usermeta import UserMeta
from objects.player import Player
from objects.team import Team
from utilities import *
from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
jinja_environment.globals['logout']=users.create_logout_url('/')
jinja_environment.globals['page']='players'

class ListHandler(webapp2.RequestHandler):
  def get(self):
    user_meta=get_meta()
    if not user_meta:
      self.redirect("/")
    players=Player.all().filter('active =',True).run()
    template_values={'user_meta':user_meta,'players':players}
    if check_mobile():
      template=jinja_environment.get_template('templates/mobile/players.html')
    else:
      template=jinja_environment.get_template('templates/players.html')
    self.response.out.write(template.render(template_values))
    
class PlayerHandler(webapp2.RequestHandler):
  def get(self,id,name=None):
    user_meta=get_meta()
    if not user_meta:
      self.redirect("/")
    player=Player.get_by_id(int(id))
    no_layout=self.request.get('noLayout')
    template_values={'user_meta':user_meta,'player':player,'no_layout':no_layout}
    if check_mobile():
      template=jinja_environment.get_template('templates/mobile/player.html')
    else:
      template=jinja_environment.get_template('templates/player.html')
    self.response.out.write(template.render(template_values))
    
class StatsHandler(webapp2.RequestHandler):
  def get(self):
    template_values={'user_meta':get_meta()}
    players=Player.all().run()
    ps=[]
    for p in players:
      bat_runs=0
      innings=0
      not_outs=0
      balls_faced=0
      highest=0
      ducks=0
      bat_fours=0
      bat_sixes=0
      overs=0
      maidens=0
      wickets=0
      bowl_runs=0
      wides=0
      no_balls=0
      catches=0
      run_outs=0
      misfields=0
      drops=0
      diving=0
      non_attempts=0
      other=0
      games=p.playergame_set
      for g in games:
        bat_runs+=g.runs
        if g.batted:
          innings += 1
          if g.runs == 0 and not g.not_out:
            ducks +=1
        if g.not_out:
          not_outs+=1
        if g.runs > highest:
          highest=g.runs
        bat_fours+=g.fours_hit
        bat_sixes+=g.sixes_hit
        balls_faced+=g.balls_faced
        overs+=g.overs+1/6.0*g.balls
        maidens+=g.maidens
        wickets+=g.wickets
        bowl_runs+=g.runs_conceded
        wides+=g.wides
        no_balls+=g.no_balls
        catches+=g.catches
        drops+=g.drops
        drops+=g.diving_drops
        diving+=g.diving_drops
        run_outs+=g.run_outs
        misfields+=g.misfields
        non_attempts+=g.non_attempts
        other+=g.other
      bat_average=0
      if innings-not_outs > 0:
        bat_average=bat_runs*1.0/(innings-not_outs)
      else:
        bat_average='-'
      bowl_strike_rate=0
      bowl_average=0
      economy=0
      if wickets > 0:
        bowl_average=bowl_runs*1.0/wickets
        bowl_strike_rate=overs*6.0/wickets
      if overs > 0:
        economy=bowl_runs*1.0/overs
      pl={'first_name':p.first_name,'surname':p.surname,
      'bat_runs':bat_runs,'innings':innings,'not_outs':not_outs,'balls_faced':balls_faced,
      'bat_average':bat_average,'highest_score':highest,'bat_strike_rate':bat_runs*100.0/balls_faced,
      'ducks':ducks,'bat_fours':bat_fours,'bat_sixes':bat_sixes,'overs':str(int(overs))+'.'+str(int(overs-int(overs))),
      'bowl_runs':bowl_runs,'wides':wides,'no_balls':no_balls,'bowl_average':bowl_average,'bowl_strike_rate':bowl_strike_rate,
      'economy':economy,'catches':catches,'run_outs':run_outs,'misfields':misfields,'drops':drops,'diving':diving,'non_attempts':non_attempts,
      'other':other,'wickets':wickets,'maidens':maidens}
      ps.append(pl)

        
    template_values['players']=ps
    template=jinja_environment.get_template('templates/stats.html')
    self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/players',ListHandler),
  ('/players/stats',StatsHandler),
  webapp2.Route('/players/<id>/<name>',handler=PlayerHandler),
  webapp2.Route('/players/<id>',handler=PlayerHandler)],debug=True)