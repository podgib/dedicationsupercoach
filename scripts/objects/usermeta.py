from google.appengine.ext import db

class UserMeta(db.Expando):
  """Holds information about a user"""
  user_id = db.StringProperty()
  fb_id = db.StringProperty()
  access_token = db.StringProperty()
  auth_verify=db.ListProperty(str)
  
  first_name = db.StringProperty()
  surname = db.StringProperty()
  admin = db.BooleanProperty(default=False)
  
  team_name = db.StringProperty()
  
  budget=db.IntegerProperty(default=200000)
  total_trades=db.IntegerProperty(default=10)
  round_trades=db.IntegerProperty(default=2)
  
  total_points=db.IntegerProperty(default=0)
  
  dateCreated = db.DateTimeProperty(auto_now_add=True)
  dateModified = db.DateTimeProperty(auto_now=True)