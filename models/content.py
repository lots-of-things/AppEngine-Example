from google.appengine.ext import ndb

from auth import OUser

# Our basic user submitted content
class Article(ndb.Model):
  title = ndb.StringProperty(required=True)
  url = ndb.TextProperty(required=True)
  why = ndb.TextProperty(required=True)
  submitted = ndb.DateTimeProperty(auto_now_add=True)
  submitter = ndb.KeyProperty(kind=OUser)
  rating = ndb.FloatProperty(default=0.5)
  mark = ndb.IntegerProperty(default=-1)

class Comment(ndb.Model):
  article = ndb.KeyProperty(kind=Article)
  ouser = ndb.KeyProperty(kind=OUser)
  posted = ndb.DateTimeProperty(auto_now_add=True)
  content = ndb.TextProperty(required=True)

class Question(ndb.Model):
  article = ndb.KeyProperty(kind=Article)
  ouser = ndb.KeyProperty(kind=OUser)
  posted = ndb.DateTimeProperty(auto_now_add=True)
  content = ndb.TextProperty(required=True)
  answer = ndb.BooleanProperty(required=True)
  tries = ndb.IntegerProperty(required=True)
  correct = ndb.IntegerProperty(required=True)
  rating = ndb.FloatProperty(default=0.5)
