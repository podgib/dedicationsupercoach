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
    user_meta=get_meta()
    if not user_meta.league:
      self.redirect('/')
      return
    league = League.all().get()
    pools=league.pool_set
    
    template_values={'pools':pools,'user_meta':user_meta}
    template=jinja_environment.get_template('templates/league.html')
    self.response.out.write(template.render(template_values))
    
  def createLeague(self):
    l=League()
    teams=UserMeta.all().fetch(16)
    l.put()
    l.createLeague(teams)
    
class DrawHandler(webapp2.RequestHandler):
  def get(self,category="pool"):
    user_meta=get_meta()
    team=LeagueTeam.all().filter('user =',user_meta).get()
    matches=[]
    if category == "pool":
      matches=Match.all().filter('pool =',team.pool).fetch(15)
    elif category == "all":
      matches=Match.all().fetch(15)
    template_values={'category':category,'user_meta':user_meta,'team':team,'matches':matches}
    template=jinja_environment.get_template('templates/draw.html')
    self.response.out.write(template.render(template_values))
    

app = webapp2.WSGIApplication([('/league',LeagueHandler),('/league/draw',DrawHandler),webapp2.Route('/league/draw/<category>',handler=DrawHandler)],debug=True)