from google.appengine.ext import ndb


class AnagramEngine(ndb.Model):
    word = ndb.StringProperty(indexed=True)
    word_count = ndb.IntegerProperty()
    sorted_word = ndb.StringProperty()
    letter_count = ndb.IntegerProperty()
    user_key = ndb.StringProperty()
    user_id = ndb.StringProperty()
