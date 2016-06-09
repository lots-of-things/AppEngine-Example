import jinja2
import logging
import os
import webapp2

from google.appengine.api import memcache
from google.appengine.api import users

from models.content import Article, Comment, Question
from models.auth import User

# This just says to load templates from the same directory this file exists in
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname('resources/templates/')))

class AddArticleHandler(webapp2.RequestHandler):

  def post(self):
    article = Article(title=self.request.POST['article-title'], url=self.request.POST['article-url'], why=self.request.POST['article-why'])

    # Attach our user if the submitter is logged in, but we do allow anonymous posts
    user = users.get_current_user()
    if user:
      article.submitter = User.key_from_user(user)
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
    user = User.get_or_create_by_user(google_user)
    article = Article.get_by_id(article_id)
    comment_content = self.request.POST['comment']
    if not comment_content or comment_content.strip() == '':
      return self.redirect('/article/%d' % article_id, body="Empty comment submitted")
    comment = Comment(user=user.key, article=article.key, content=comment_content)
    comment.put()
    return self.redirect('/article/%d' % article_id, body="Thank you for your comment")

class AddQuestionHandler(webapp2.RequestHandler):
  def post(self, article_id):
    article_id = int(article_id)
    google_user = users.get_current_user()
    user = User.get_or_create_by_user(google_user)
    article = Article.get_by_id(article_id)
    question_content = self.request.POST['question']
    ans = self.request.POST['answer']=='true'
    if not question_content or question_content.strip() == '':
      return self.redirect('/article/%d' % article_id, body="You're question needs words.")
    question = Question(user=user.key, article=article.key, content=question_content, answer=ans, tries=0, correct=0)
    question.put()
    return self.redirect('/article/%d' % article_id, body="Thank you for your question")

class ViewArticleHandler(webapp2.RequestHandler):

  def get(self, article_id):
    """Generate a page for a specific article"""
    template_values = {}

    user = users.get_current_user()
    if user:
      template_values['user'] = user
      template_values['google_logout_url'] = users.create_logout_url('/')
    else:
      template_values['google_login_url'] = users.create_login_url('/login?final=/article/%d' % int(article_id))

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
    question_list = []
    for comment in Question.query(Question.article == article.key).order(Question.rating):
      comment_values = {}
      comment_values['id'] = comment.key.id()
      # Another fine example of an anti-pattern
      comment_values['user'] = comment.user.get()
      comment_values['posted'] = comment.posted.strftime("%A, %d. %B %Y %I:%M%p")
      comment_values['content'] = comment.content
      comment_values['answer'] = comment.answer
      question_list.append(comment_values)

    template_values['questions'] = question_list
    template = jinja_environment.get_template('article.html')
    self.response.out.write(template.render(template_values))
