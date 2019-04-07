
import webapp2
import jinja2
import itertools
import os

from google.appengine.api import users
from google.appengine.ext import ndb

from models import AnagramEngine

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class Add(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if self.request.GET.has_key('add'):
            user_id = users.get_current_user().user_id()
            user_anagram_data = AnagramEngine.query(AnagramEngine.user_id == user_id).fetch()
            template_values = {
                'user': user,
                'anagram_data': user_anagram_data
            }
            template = JINJA_ENVIRONMENT.get_template('templates/add.html')
            self.response.write(template.render(template_values))

    def post(self):
        anagram_list = list()
        user = users.get_current_user()
        if users.get_current_user():
            user_id = users.get_current_user().user_id()
            user_anagram_data = AnagramEngine.query(AnagramEngine.user_id == user_id).fetch()
            if self.request.POST.has_key('button'):
                if self.request.POST.has_key('word'):
                    a_word = self.request.POST['word']
                    anagram_word = ''.join([i for i in a_word if not i.isdigit() and i.isalnum()])
                    anagram_word = anagram_word.lower()
                    anagram_data = AnagramEngine.query(AnagramEngine.user_id == user_id, AnagramEngine.sorted_word == "".join(sorted(anagram_word))).fetch()
                    if len(anagram_data) == 0:
                        self.add_anagram(anagram_word, user_id)
                    else:
                        self.increment_anagram_count(anagram_data, anagram_word)
                elif self.request.POST.has_key('afile'):
                    file_storage = self.request.POST.get('afile')
                    file_data = file_storage.file.read()
                    words = file_data.split('\n')
                    for a_word in words:
                        word = ''.join([i for i in a_word if not i.isdigit() and i.isalnum()])
                        word = word.lower()
                        if len(word) > 0:
                            anagram_data = AnagramEngine.query(AnagramEngine.user_id == user_id,
                                                         AnagramEngine.sorted_word == "".join(sorted(word))).fetch()
                            if len(anagram_data) == 0:
                                self.add_anagram(word, user_id)
                            else:
                                self.increment_anagram_count(anagram_data, word)
            template_values = {
                'user': user,
                'anagram_data': user_anagram_data
            }

        else:
            template_values = {
                'error' : "Please login first",
                'user': user
            }
        template = JINJA_ENVIRONMENT.get_template('templates/main.html')
        self.response.write(template.render(template_values))

    def add_anagram(self, anagram_word, user_id):
        try:
            anagram_list = list()
            for word in itertools.permutations(anagram_word):
                anagram_list.append("".join(word))
            sorted_word = "".join(sorted(anagram_word))
            sorted_key = str(user_id) + "/" + sorted_word
            anagram_details = AnagramEngine(word=anagram_word,
                                      user_key = sorted_key,
                                      sorted_word=sorted_word,
                                      user_id=user_id,
                                      word_count=1,
                                      letter_count=len(sorted_word))
            anagram_details.put()
        except Exception as ex:
            return False

    def increment_anagram_count(self, anagram_data, word):
        try:
            anagram_data = anagram_data[0]
            words = anagram_data.word.split(",")
            if not str(word) in words:
                anagram_data.word = anagram_data.word + "," + word
            anagram_data.word_count = int(anagram_data.word_count) + 1
            anagram_data.put()
        except:
            return False

class Generate(webapp2.RequestHandler):

    def get(self):
        word = ''
        anagram_list = list()
        if users.get_current_user():
            user = users.get_current_user()
            if self.request.GET.has_key('generate'):
                template_values= {
                    'user': user
                }
            elif self.request.GET.has_key('word'):
                a_word = self.request.GET['word']
                anagram_word = ''.join([i for i in a_word if not i.isdigit() and i.isalnum()])
                for let in anagram_word:
                    word = word + let
                    if len(word) < 3:
                        continue
                    else:
                        anagram_list.extend(self.all_permutations(word))
            template_values = {
                'user': user,
                'anagram_list': anagram_list
            }
        else:
            template_values = {
                'error': "Please login first"
            }

        template = JINJA_ENVIRONMENT.get_template('templates/generate.html')
        self.response.write(template.render(template_values))

    def post(self):
        user_id = None
        word = ''
        template_values = {}
        if users.get_current_user():
            user = users.get_current_user()
            user_id = user.user_id()
            if self.request.POST.has_key('button'):
                anagram_list = list()
                a_word = self.request.POST['word']
                anagram_word = ''.join([i for i in a_word if not i.isdigit() and i.isalnum()])
                for let in anagram_word:
                    word = word + let
                    if len(word) < 3:
                        continue
                    else:
                        anagram_list.extend(self.all_permutations(word))

            template_values = {
                 'anagram_list' : anagram_list,
                 'anagram_count' : len(anagram_list),
                 'user': user
             }
        else:
            template_values = {
                'error': "please login first"
            }
        template = JINJA_ENVIRONMENT.get_template('templates/generate.html')
        self.response.write(template.render(template_values))


    def all_permutations(self, input_string):
        if len(input_string) == 1:
            return input_string
        result = []
        for letter in input_string:
            for perm in self.all_permutations(input_string.replace(letter, '', 1)):
                result.append(letter + perm)

        return result

class FindSubAnagram(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if self.request.GET.has_key('find_sub'):
            template_values = {'user': user}
            template = JINJA_ENVIRONMENT.get_template('templates/find_sub.html')
            self.response.write(template.render(template_values))

    def post(self):
        anagram_list = list()
        word = ""
        template_values = {}
        if users.get_current_user():
            user = users.get_current_user()
            if self.request.POST.has_key('button'):
                a_word = self.request.POST['word']
                anagram_word = ''.join([i for i in a_word if not i.isdigit() and i.isalnum()])
                for let in anagram_word:
                    word = word + let
                    if len(word) < 3:
                        continue
                    else:
                        anagram_list.extend(self.all_permutations(word))
                template_values = {
                    'anagram_list': anagram_list,
                    'user': user
                }
        else:
            template_values = {
                'error': "Please login first"
            }

        template = JINJA_ENVIRONMENT.get_template('templates/generate.html')
        self.response.write(template.render(template_values))

    def all_permutations(self, input_string):
        if len(input_string) == 1:
            return input_string
        result = []
        for letter in input_string:
            for perm in self.all_permutations(input_string.replace(letter, '', 1)):
                result.append(letter + perm)

        return result

class Search(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if self.request.GET.has_key('search'):
            template_values= {'present': True,
                              'user': user
                              }
            template = JINJA_ENVIRONMENT.get_template('templates/search.html')
            self.response.write(template.render(template_values))

    def post(self):
        user = users.get_current_user()
        anagram_list = list()
        present = False
        template_values = dict()
        if users.get_current_user():
            user_id = users.get_current_user().user_id()
            if self.request.POST.has_key('button'):
                a_word = sorted(self.request.POST['word'])
                anagram_word = ''.join([i for i in a_word if not i.isdigit()and i.isalnum()])

                anagram_data = AnagramEngine.query(AnagramEngine.user_id==user_id and AnagramEngine.sorted_word==anagram_word).fetch()

                if len(anagram_data) == 0:
                    present = False
                else:
                    present = True
                for word in itertools.permutations(anagram_word):
                    anagram_list.append("".join(word))
            template_values = {
                'word' : self.request.POST['word'],
                'anagram_word' : len(self.request.POST['word']),
                'anagram_count' : len(anagram_list),
                'anagram_list': anagram_list,
                'present' : present,
                'user': user,
                'anagram_data' : anagram_data
            }
        else:
            template_values = {'error' : "Please login first",
                               'user': user
                               }

        template = JINJA_ENVIRONMENT.get_template('templates/search.html')
        self.response.write(template.render(template_values))

class Show(webapp2.RequestHandler):

    def post(self):
        if users.get_current_user():
            user = users.get_current_user()
            user_id = users.get_current_user().user_id()
            anagram_data = AnagramEngine.query(AnagramEngine.user_id==user_id).fetch()

            template_values = {
                    'user': user,
                    'anagram_data': anagram_data
                }
        else:
            template_values ={
                'error': "please login first"
            }
        template = JINJA_ENVIRONMENT.get_template('templates/show.html')
        self.response.write(template.render(template_values))
