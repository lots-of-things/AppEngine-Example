import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users

from models.content import Article, Question
from models.vote import Vote, Answer
from models.vote import UPVOTE, DOWNVOTE
from models.auth import OUser

class AddVoteHandler(webapp2.RequestHandler):

  def post(self, article_id, vote_type):
    article = Article.get_by_id(int(article_id))

    google_user = users.get_current_user()
    if google_user:
      ouser = OUser.get_or_create_ouser_by_user(google_user)
      if(ouser):
        ouser_key = OUser.key_from_user(google_user)
        if ouser_key:
          vote = Vote.create(article_key=article.key, ouser_key=ouser_key, value=DOWNVOTE)
          article.rating = article.rating + ouser.vote
          ouser.vote=0



      ndb.put_multi([article, vote, ouser])

      return self.redirect('/', body="Thanks for your vote! <a href='/choose'>Back to main</a> (later show voting statistics here)")
    return self.redirect('/', body="Must be logged in to vote.")

  def get(self, article_id, vote_type):
    return self.post(article_id, vote_type)

class AddAnswerHandler(webapp2.RequestHandler):

  def post(self, question_id, ans_type):
    question = Question.get_by_id(int(question_id))
    article_id = question.article.id()
    google_user = users.get_current_user()
    if google_user:
      ouser = OUser.get_or_create_ouser_by_user(google_user)
    if ouser:
      if not Answer.find(question_key=question.key, ouser_key=ouser.key):
          question.tries = question.tries + 1
          # TODO Votes are now being created properly, Add update requests to a pull queue
          gotit = False
          if ans_type == 'true':
              ans = Answer.create(question_key=question.key, ouser_key=ouser.key, val=True)
              if question.answer == True:
                  question.correct += question.correct + 1
                  gotit = True
          else:
              ans = Answer.create(question_key=question.key, ouser_key=ouser.key, val=False)
              if question.answer == False:
                  question.correct += question.correct + 1
                  gotit = True
          ans.put()
          extra = ""
          if gotit:
              ouser.vote=ouser.vote+1
              extra = "You got 1 point."
          question.put()
          ouser.put()
          return self.response.write("<p>answer was "+str(question.answer)+". "+extra+" </p><a href=/article/"+ str(article_id)+">Back to article</a>")
    return self.response.write("need user and can't have voted already...")

  def get(self, article_id, vote_type):
    return self.post(article_id, vote_type)

class PopHandler(webapp2.RequestHandler):

  def get(self):
      articles = Article.query(Article.mark==0).order(Article.mark).fetch(1)
      for article in articles:
          article.mark=1
          article.put()
      articles = Article.query(Article.mark<0).order(Article.mark, -Article.rating).fetch(1)
      for article in articles:
          article.mark=0
          article.put()
      return self.redirect('/', body="Popped.")
