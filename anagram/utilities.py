from google.appengine.ext import ndb
from google.appengine.api import users
from myuser import MyUser
from anagram import AnagramEngine
import logging
import re  # regex

def get_login_url(main_page):
    return users.create_login_url(main_page.request.uri)


def get_logout_url(main_page):
    return users.create_logout_url(main_page.request.uri)
