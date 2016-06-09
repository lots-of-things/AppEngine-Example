import webapp2

from index import IndexHandler, ChooseHandler
from auth import LoginHandler
from article import AddArticleHandler, ViewArticleHandler, AddCommentHandler, AddQuestionHandler
from vote import AddVoteHandler, AddAnswerHandler

# Here we can set up more advanced routing rules
APP = webapp2.WSGIApplication([
    (r'/', IndexHandler),
    (r'/choose', ChooseHandler),
    (r'/login', LoginHandler),
    (r'/submit', AddArticleHandler),
    (r'/article/(\d+)', ViewArticleHandler),
    (r'/article/(\d+)/comment', AddCommentHandler),
    (r'/article/(\d+)/question', AddQuestionHandler),
    (r'/vote/(\d+)/(\w+)', AddVoteHandler),
    (r'/ans/(\d+)/(\w+)', AddAnswerHandler),
], debug=True)
