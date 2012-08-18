#!/usr/bin/env python

import webapp2
import jinja2
import os

from objects.usermeta import UserMeta
from objects.game import Game
from utilities import *
from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
jinja_environment.globals['logout']=users.create_logout_url('/')
jinja_environment.globals['page']='games'

class ViewHandler(webapp2.RequestHandler):
  def get(self,game_id=None):
    user_meta=get_meta()
    if not user_meta:
      self.redirect("/")
    game=Game.get_by_id(int(game_id))
    if not game_id:
      game=next_game()
    players=game.playergame_set
    template_values={'game':game, 'user_meta':user_meta,
        'batsmen':sorted([b for b in players if b.batted],key=lambda player: player.batting_position),
        'bowlers':sorted([b for b in players if b.bowled],key=lambda player: player.bowling_position),
        'fielders':players}
    if check_mobile():
      template=jinja_environment.get_template('templates/mobile/game.html')
    else:
      template=jinja_environment.get_template('templates/game.html')
    self.response.out.write(template.render(template_values))

class ListHandler(webapp2.RequestHandler):
  def get(self):
    user_meta=get_meta()
    if not user_meta:
      self.redirect("/")
    next=next_game()
    template_values={'user_meta':user_meta,'next_game':next,'lockout':lockout()}
    template_values['future_games']=Game.all().filter('round >',next.round).order('round').run()
    template_values['past_games']=Game.all().filter('round <',next.round).order('round').run()
    if check_mobile():
      template=jinja_environment.get_template('templates/mobile/games.html')
    else:
      template=jinja_environment.get_template('templates/games.html')
    self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([webapp2.Route('/games/<game_id>',handler=ViewHandler),
                              ('/games',ListHandler)],debug=True)
