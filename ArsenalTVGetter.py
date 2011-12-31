# -*- coding: utf-8 -*-

"""
first. searching アーセナル from http://tv.so-net.ne.jp/
second. tweet TV Program about Arsenal in Japan.
"""
import sys
import os
from BeautifulSoup import BeautifulSoup
from urllib import urlopen
import urllib
import twitter
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

# SearchWords
QUERY_PARAM = u'アーセナル'

# for utf-8 encode
if 'ascii'==sys.getdefaultencoding():
  stdin = sys.stdin
  stdout = sys.stdout
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdin = stdin
  sys.stdout = stdout

# for twitter OAuth. fill your account
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''

# api initialize
API = twitter.Api(
  consumer_key = CONSUMER_KEY,
  consumer_secret = CONSUMER_SECRET,
  access_token_key = ACCESS_KEY,
  access_token_secret = ACCESS_SECRET,
  cache=None)

def get_match_program(program_titles, program_dates):
  """
  return list[{match_title, match_detail}]
  exclude same time contents
  """
  match_dict = {}
  match_programs = []
  insert_flag = 'true'

  for i in range(len(program_titles)):
    # if not include アーセナル, skip.
    if program_titles[i].find(QUERY_PARAM) < 0:
      continue
    for j in range(len(match_programs)):
      if match_programs[j]['match_detail'][0:21] == program_dates[i][0:21]:
        insert_flag = 'false'
        break
      else:
        insert_flag = 'true'
    if insert_flag == 'true':
      match_dict.update({"match_title":program_titles[i]})
      match_dict.update({"match_detail":program_dates[i]})
      match_programs.append(match_dict.copy())
      insert_flag = 'false'

  return match_programs

def get_match_lists():
  param = urllib.urlencode({'stationPlatformId':'0',
                          'condition.keyword':u'アーセナル', 
                          'submit':u'検索'})
  soup = BeautifulSoup(urlopen('http://tv.so-net.ne.jp/schedulesBySearch.action?'
                             +param))

  # get Program titles
  program_titles_tmp = soup.findAll('h2')
  program_titles = []
  for program_title_tmp in program_titles_tmp:
    if program_title_tmp.find('a') != None:
      program_title = program_title_tmp.find('a').contents
      program_titles.append(program_title[0])

  # get Program date
  program_dates_tmp = soup.findAll('p',{'class':'utileListProperty'})
  program_dates = []
  for program_date_tmp in program_dates_tmp:
    program_date_str = program_date_tmp.contents
    program_dates.append(program_date_str[0])

  return program_titles, program_dates

def get_tweet_texts(match_programs):
  tweet_texts = []
  for match_program in match_programs:
    tweet_text = match_program['match_title'] + ' ' + match_program['match_detail'] + ' #ArsenalJP'
    tweet_texts.append(tweet_text)

  return tweet_texts

def tweet_match(tweet_texts):
  for tweet_text in tweet_texts:
    API.PostUpdate(tweet_text)


class ArsenalTVTwetter(webapp.RequestHandler):
  def get(self):
    program_titles, program_dates = get_match_lists()
    match_programs = get_match_program(program_titles, program_dates)
    tweet_texts = get_tweet_texts(match_programs)
    tweet_match(tweet_texts)

    template_values = {
      'match_programs':match_programs
    }

    path = os.path.join(os.path.dirname(__file__), 'tweetmatch.html')
    self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication([('/ArsenalTVGetter', ArsenalTVTwetter)],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()