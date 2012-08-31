import webapp2
import jinja2
import os
from utilities import *

from objects.usermeta import UserMeta
from objects.league import *
from google.appengine.ext import db

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
jinja_environment.globals['logout']=users.create_logout_url('/')
jinja_environment.globals['page']='league'

class LeagueHandler(webapp2.RequestHandler):
  def get(self):
    l=League()
    teams=UserMeta.all().fetch(16)
    l.put()
    l.createLeague(teams)

app = webapp2.WSGIApplication([('/league',LeagueHandler)],debug=True)