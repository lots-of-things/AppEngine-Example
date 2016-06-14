import jinja2
import logging
import os
import webapp2

from google.appengine.api import memcache
from google.appengine.api import users

from models.content import Article, Comment, Question
from models.vote import Answer
from models.auth import OUser

from auth import ouser_vars

# This just says to load templates from the same directory this file exists in
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname('resources/templates/')))

class AddArticleHandler(webapp2.RequestHandler):

  def post(self):
    article = Article(title=self.request.POST['article-title'], url=self.request.POST['article-url'], why=self.request.POST['article-why'])

    # Attach our user if the submitter is logged in, but we do allow anonymous posts
    google_user = users.get_current_user()
    if google_user:
      article.submitter = OUser.key_from_user(google_user)
    article_key = article.put()

    # Invalidate the article list in memcache, It will get rebuilt next time the front page is loaded
    memcache.delete("articles_list")

    # Redirect on POST is a common web technique, designed to keep people from accidentally
    # resubmitting the same form repeatedly
    return self.redirect('/article/%d' % article_key.id(), body="Thanks for your submission!")

class AddCommentHandler(webapp2.RequestHandler):
  def post(self, article_id):
    article_id = int(article_id)
    google_user = users.get_current_user()
    ouser = OUser.get_or_create_ouser_by_user(google_user)
    article = Article.get_by_id(article_id)
    comment_content = self.request.POST['comment']
    if not comment_content or comment_content.strip() == '':
      return self.response.write("empty comments are dumb" )
    comment = Comment(ouser=ouser.key, article=article.key, content=comment_content)
    comment.put()
    return self.response.write("cool story" )

class AddQuestionHandler(webapp2.RequestHandler):
  def post(self, article_id):
    article_id = int(article_id)
    google_user = users.get_current_user()
    ouser = OUser.get_or_create_ouser_by_user(google_user)
    article = Article.get_by_id(article_id)
    question_content = self.request.POST['question']
    ans = self.request.POST['answer']=='true'
    if not question_content or question_content.strip() == '':
      return self.response.write("your question needs words" )
    question = Question(ouser=ouser.key, article=article.key, content=question_content, answer=ans, tries=0, correct=0)
    question.put()
    return self.response.write("<p>Thanks for the question</p><a href=/article/"+ str(article_id)+">Back to article</a>" )

class ViewArticleHandler(webapp2.RequestHandler):

  def get(self, article_id):
    """Generate a page for a specific article"""
    template_values = {}

    template_values.update(ouser_vars('/article/%d' % int(article_id)))

    article = Article.get_by_id(int(article_id))
    article_values = {
      'title': article.title,
      'url': article.url,
      'why': article.why,
      'submitted': article.submitted,
      'rating': article.rating,
      'id': article_id,
    }

    if article.submitter:
      submitter = article.submitter.get()
      if submitter:
        article_values['submitter'] = submitter.nickname


    # Merge the two sets of variables together
    template_values.update(article_values)

    # Add in any comments that might exist
    comment_list = []
    # for comment in Comment.query(Comment.article == article.key).order(Comment.posted):
    #   comment_values = {}
    #   comment_values['id'] = comment.key.id()
    #   # Another fine example of an anti-pattern
    #   comment_values['user'] = comment.user.get()
    #   comment_values['posted'] = comment.posted.strftime("%A, %d. %B %Y %I:%M%p")
    #   comment_values['content'] = comment.content
    #   comment_list.append(comment_values)

    # Add in any questions that might exist
    google_user = users.get_current_user()
    if google_user:
        ouser = OUser.get_or_create_ouser_by_user(google_user)
        question_list = []
        for que in Question.query(Question.article == article.key).order(Question.rating):
          que_values = {}
          que_values['id'] = que.key.id()
          # Another fine example of an anti-pattern
          que_values['ouser'] = que.ouser.get()
          que_values['posted'] = que.posted.strftime("%A, %d. %B %Y %I:%M%p")
          que_values['content'] = que.content
          que_values['answer'] = que.answer
          que_values['displayq'] = (Answer.find(question_key=que.key, ouser_key=ouser.key) == None)
          question_list.append(que_values)
        template_values['questions'] = question_list
    else:
        ouser = None


    template = jinja_environment.get_template('article.html')
    self.response.out.write(template.render(template_values))
