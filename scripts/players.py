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

app = webapp2.WSGIApplication([('/players',ListHandler),
  webapp2.Route('/players/<id>/<name>',handler=PlayerHandler),
  webapp2.Route('/players/<id>',handler=PlayerHandler)],debug=True)