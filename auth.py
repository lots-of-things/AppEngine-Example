import logging
import webapp2

from google.appengine.api import users

from models.auth import OUser

class LoginHandler(webapp2.RequestHandler):

  def post(self):
      # Here you could attempt to create an account through other APIs that could have been passed in
      # Or log them into your local API using a username/password in self.request.POST perhaps
      # but for this app, we just give up and tell them we couldn't figure it out.
      self.response.write('You could not be logged in')

  def get(self):
    # Get the logged in user from the Google Users API
    # https://developers.google.com/appengine/docs/python/users/
    google_user = users.get_current_user()
    if google_user:
      # Use a user entity in our datastore so we can get their nickname etc. for other users to see
      # Also to tie content created by them on oneth back to their user account
      ouser = OUser.get_or_create_ouser_by_user(google_user)
      logging.info("%s has logged in" % ouser.user.email())

      # The docs indicate that an existing user could change their email address or nickname, which could require
      # the user entity to be updated, so handle that case here
      if ouser.user != google_user:
        logging.info("OUser %s has updated their google account" % ouser.nickname)
        ouser.user = google_user
        ouser.put()

      if self.request.get('final'):
        return self.redirect(self.request.get('final'), body="Thanks for logging in")

      return self.redirect('/', body="Thanks for logging in")
    else:
      # You could display a login form here if you had alternative methods of logging in
      logging.warning("A user could not be logged in")
      self.response.write('You could not be logged in')

def ouser_vars(current_url):
    template_values = {}

    user = users.get_current_user()

    if user:
      template_values['ouser'] = OUser.get_or_create_ouser_by_user(user)
      template_values['google_logout_url'] = users.create_logout_url(current_url)
    else:
      template_values['google_login_url'] = users.create_login_url('/login?final='+current_url)

    return template_values
