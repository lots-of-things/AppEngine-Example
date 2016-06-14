from google.appengine.ext import ndb

from auth import OUser
from content import Article, Question

UPVOTE = 1
DOWNVOTE = -1

# Two models used to calculate the content rating
class Vote(ndb.Model):
  article = ndb.KeyProperty(kind=Article)
  ouser = ndb.KeyProperty(kind=OUser)
  voted = ndb.DateTimeProperty(auto_now_add=True)
  value = ndb.IntegerProperty(choices=(UPVOTE,DOWNVOTE), required=True)

  @classmethod
  def create(cls, article_key, ouser_key, value):
    # Compose a key that ensures a user can only vote on the same article once
    # any other votes will just overwrite the same entity no matter the type
    key = ndb.Key('Vote', '%s:%s' % (article_key.id(), ouser_key.id()))
    return Vote(key=key, ouser=ouser_key, article=article_key, value=value)

class Answer(ndb.Model):
  question = ndb.KeyProperty(kind=Question)
  ouser = ndb.KeyProperty(kind=OUser)
  value = ndb.BooleanProperty()

  @classmethod
  def find(cls, question_key, ouser_key):
    key = ndb.Key('Answer', '%s:%s' % (question_key.id(), ouser_key.id()))
    return key.get()

  @classmethod
  def create(cls, question_key, ouser_key, val):
    key = ndb.Key('Answer', '%s:%s' % (question_key.id(), ouser_key.id()))
    if(key.get()):
      return None
    return Answer(key=key, ouser=ouser_key, question=question_key, value=val)
