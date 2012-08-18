from google.appengine.ext import db

class Game(db.Model):
  opposition=db.StringProperty(default="TBA")
  played=db.BooleanProperty(default=False)
  result=db.CategoryProperty()
  location=db.StringProperty(default="TBA")
  overs=db.IntegerProperty(default=50)
  score=db.StringProperty(default="0/0")
  opposition_score=db.StringProperty(default="0/0")
  round=db.IntegerProperty()
  
  date=db.DateProperty()
  
  batExtras=db.IntegerProperty(default=0)
  bowlExtras=db.IntegerProperty(default=0)