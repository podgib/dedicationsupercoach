#!/usr/bin/env python

import webapp2
import jinja2
import os
from utilities import *
from google.appengine.api import users
import datetime
import base64

from objects.usermeta import UserMeta
from objects.player import Player
from objects.game import Game
from google.appengine.ext import db
import urllib
import json

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
jinja_environment.globals['logout']=users.create_logout_url('/')
jinja_environment.globals['page']='home'

class LoginHandler(webapp2.RequestHandler):
  def get(self):
    access_token=self.request.get('fbtoken')
    if not access_token:
      self.redirect("/")
      return
    profile=json.load(urllib.urlopen("https://graph.facebook.com/me?"+
      urllib.urlencode(dict(access_token=access_token))))
      
    id=profile["id"]
    user=UserMeta.all().filter("fb_id =",id).get()
    if user:
      rand_string=base64.urlsafe_b64encode(os.urandom(32))
      if not user.auth_verify:
        user.auth_verify=[]
      user.auth_verify.append(rand_string)
      self.response.set_cookie("fb_user",id+":"+rand_string,expires=datetime.datetime.now()+datetime.timedelta(days=30));
      user.access_token=access_token
      save_user(user)
      if not self.request.get('app'):
        self.redirect("/")
      else:
        self.response.out.write(json.dumps({"auth":id+":"+rand_string}))
      return
    else:
      if self.request.get('app'):
        self.response.out.write("Error")
        return
      template_values={'first_name':profile["first_name"],'surname':profile["last_name"],'fb_id':id,'access_token':access_token}
      template=jinja_environment.get_template('templates/signup.html')
      self.response.out.write(template.render(template_values))
      
class LogoutHandler(webapp2.RequestHandler):
  def get(self):
    if users.get_current_user():
      self.redirect(users.create_logout_url('/'))
    else:
      try:
        auth_verify=self.request.cookies.get("fb_user").split(':',1)[1]
        user=get_meta()
        if user:
          user.auth_verify.remove(auth_verify)
          save_user(user) 
      except:
        auth_verify=''
      self.response.set_cookie("fb_user", "",expires=datetime.datetime.now())
      self.redirect("/")
    

class SignupHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
    
    user_meta = get_meta()
    if user_meta:
      self.redirect('/team/select')
    
    template_values={'email':user.email()}
    
    template=jinja_environment.get_template('templates/signup.html')
    self.response.out.write(template.render(template_values))
  
  def post(self):
    if get_meta():
      self.redirect("/team/select")
    current_user = users.get_current_user()
    fb_id=None
    auth_verify=[]
    if not current_user:
      fb_id=self.request.get('fb_id')
      if not fb_id:
        self.redirect(users.create_login_url(self.request.uri))
      else:
        rand_string=base64.urlsafe_b64encode(os.urandom(32))
        auth_verify.append(rand_string)
        self.response.set_cookie("fb_user",fb_id+":"+rand_string,expires=datetime.datetime.now()+datetime.timedelta(days=30))
    uid=None
    if current_user:
      uid=current_user.user_id()
    user_meta = UserMeta(first_name=self.request.get('first_name'),
                          surname=self.request.get('surname'),
                          team_name=self.request.get('team_name'),
                          user_id=uid,fb_id=fb_id,access_token=self.request.get('access_token'),auth_verify=auth_verify)
    save_user(user_meta)
    self.redirect('/team/select')
    

class LandingHandler(webapp2.RequestHandler):
    def get(self):
      user_meta=get_meta()
      
      if not user_meta:
        if users.get_current_user():
          return self.redirect("/signup")
        template_values={'FACEBOOK_APP_ID':FACEBOOK_APP_ID,'login':users.create_login_url("/"),'dev_server':dev_server}
        template=jinja_environment.get_template('templates/index.html')
        self.response.out.write(template.render(template_values))
        return
      
      last_game=Game.all().filter('round =',current_round()-1).get()
      last_team=get_team(game=last_game)
      round_score=0
      if last_team:
        round_score=last_team.total_score
      template_values={'user_meta':user_meta,'round_score':round_score}
      if check_mobile():
        template=jinja_environment.get_template('templates/mobile/home.html')
      else:
        template=jinja_environment.get_template('templates/home.html')
      self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/signup',SignupHandler),('/', LandingHandler),('/login',LoginHandler),('/logout',LogoutHandler)],debug=True)
