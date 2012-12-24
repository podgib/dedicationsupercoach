from google.appengine.ext import db
from google.appengine.api import users
from objects.game import Game
from objects.player import Player
from objects import team
from objects.team import Team
from objects.usermeta import UserMeta
from google.appengine.api import memcache
import webapp2
import os

FACEBOOK_APP_ID="383493568371686"
FACEBOOK_APP_SECRET="1db733ef265fda306c9782747ae76e75"
dev_server=os.environ.get('SERVER_SOFTWARE','').startswith('Development')

dismissal_types=["Bowled","Caught","Run out","LBW","Stumped","Timed Out","Handling the ball"]

class Utilities(db.Model):
  current_round=db.IntegerProperty(default=1)
  final_game=db.IntegerProperty(default=1)
  next_game=db.ReferenceProperty(Game)
  lockout=db.BooleanProperty(default=False)
  
def lockout():
  lockout=memcache.get("lockout")
  if lockout is not None:
    return lockout
  else:
    lockout = Utilities.all().get().lockout
    memcache.add("lockout",lockout)
    return lockout
  
def toggle_lockout():
  utilities=Utilities.all().get()
  utilities.lockout = not utilities.lockout
  memcache.set("lockout",utilities.lockout)
  utilities.put()
  
def current_round():
  current_round=memcache.get("current_round")
  if current_round is not None:
    return current_round
  else:
    current_round=Utilities.all().get().current_round
    memcache.add("current_round",current_round)
    return current_round
    
def set_current_round(round):
  utilities=Utilities.all().get()
  utilities.current_round = round
  memcache.set("current_round",round)
  utilities.put()
  
def get_meta(user=None):
  if not user:
    user=users.get_current_user()
  if not user:
    return fb_get_meta()
  meta=memcache.get("u"+user.user_id())
  if meta is not None:
    return meta
  else:
    meta=UserMeta.all().filter('user_id =',user.user_id()).get()
    if meta is not None:
      memcache.add("u"+user.user_id(),meta)
    return meta
    
def fb_get_meta():
  fb=webapp2.get_request().cookies.get("fb_user")
  if not fb:
    fb=webapp2.get_request().get("auth")
  if fb:
    fb=fb.split(":",1)
    meta=memcache.get("fb"+fb[0])
    if meta is None:
      meta=UserMeta.all().filter('fb_id =',fb[0]).get()
      if meta is not None:
        memcache.add("fb"+fb[0],meta)
    if meta is not None:
      if len(fb)> 1 and fb[1] in meta.auth_verify:
        return meta
      else:
        return None
  else:
    return None

def save_user(meta):
  meta.put()
  if meta.fb_id:
    memcache.set("fb"+meta.fb_id,meta)
  if meta.user_id:
    memcache.set("u"+meta.user_id,meta)
  
def next_game():
  next_game=memcache.get("next_game")
  if next_game is not None:
    return next_game
  else:
    utilities=Utilities.all().get()
    next_game=utilities.next_game
    memcache.add("next_game",next_game)
    return next_game
  
def game_completed(game):
  utilities=Utilities.all().get()
  next_game=Game.all().filter('round =',utilities.next_game.round+1).get()
  if next_game:
    team.finish_round(game,next_game)
  game.played=True
  if game.key() == utilities.next_game.key():
    utilities.next_game=next_game
    memcache.set("next_game",next_game)
    if utilities.next_game:
      utilities.current_round=utilities.next_game.round
      memcache.set("current_round",utilities.current_round)
    utilities.lockout=False
    memcache.set("lockout",False)
    utilities.put()
    for u in UserMeta.all().run():
      u.round_trades=2
      save_user(u)
  
def get_team(user_meta=None,game=None):
  if not user_meta:
    user_meta=get_meta()
  if not game:
    game=next_game()
  if not game:
    game=Game.all().filter('round =',current_round()-1)
  return Team.all().filter('user =',user_meta).filter('game =',game).get()
  
def selected_available(selected_keys,active_only=True):
  selected=[]
  available=[]
  all_players=set(Player.all(keys_only=True).filter('active =',active_only).fetch(1000))
  #selected_keys=set(selected_keys)
  available_keys=all_players.difference(selected_keys)
  for key in selected_keys:
    selected.append(db.get(key))
  for key in available_keys:
    available.append(db.get(key))
  return (selected,available)
  
def check_mobile():
  return False
  #agent=webapp2.get_request().user_agent.lower()
  #return agent.find('mobi') >= 0 and agent.find('ipad') < 0