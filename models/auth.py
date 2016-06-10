from google.appengine.ext import ndb

class OUser(ndb.Model):
  user = ndb.UserProperty(required=True, indexed=False)
  vote = ndb.FloatProperty(default=0)
  joined = ndb.DateProperty(auto_now_add=True)
  about = ndb.TextProperty()

  # In case users don't want to display their Google "name", they can override it here
  local_nickname = ndb.StringProperty(indexed=False)

  @classmethod
  def key_from_user(cls, user):
    # Construct the key using the user_id that is assured to be constant as our identifier
    # This also serves as a good example of how to tie entities together without requiring a query
    return ndb.Key('OUser', user.user_id())

  @classmethod
  def create(cls, user):
    key = cls.key_from_user(user)
    return cls(key=key, user=user)

  @classmethod
  def get_or_create_ouser_by_user(cls, user):
    key = cls.key_from_user(user)
    ouser = key.get()
    if not ouser:
      ouser = cls.create(user)
      ouser.put()
    return ouser

  @property
  def nickname(self):
    if self.local_nickname:
      return self.local_nickname
    else:
      return self.user.nickname()
