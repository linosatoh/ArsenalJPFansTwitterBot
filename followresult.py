# -*- coding: utf-8 -*-

"""
TERMに指定された検索ワードをTwitterに検索を掛けて
15件分をさかのぼって、キーワードを含むTweetをしたユーザを自動的にフォローします。
"""
import sys
import twitter
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

# for utf-8 encode
if 'ascii'==sys.getdefaultencoding():
  stdin = sys.stdin
  stdout = sys.stdout
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdin = stdin
  sys.stdout = stdout

# for twitter OAuth. Fill the fields
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''

# Search words
TERM = u'arsenal OR アーセナル'

# api initialize
API = twitter.Api(
  consumer_key = CONSUMER_KEY,
  consumer_secret = CONSUMER_SECRET,
  access_token_key = ACCESS_KEY,
  access_token_secret = ACCESS_SECRET,
  cache=None)

class followResultPage(webapp.RequestHandler):
  """
  GAEのリクエストハンドラーを継承したクラス
  """
  def get(self):
    """
    ゲットの場合の処理
    """
    search_results = get_search_results(TERM)
    
    follow_dict = {}
    follow_dict_list = []
    
    friends = get_friends()
    for result in search_results:
      if not result.user.screen_name in friends:
        follow_dict.update({'screen_name':result.user.screen_name})
        follow_dict.update({'profile_image_icon':result.user.profile_image_url})
        follow_dict.update({'text':result.text})
        follow_dict_list.append(follow_dict.copy())

    template_values = {
      'following_users':follow_dict_list
    }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

def get_friends():
  """
  Twitterのフォローリストの取得
  """
  return API.GetFriends()

def get_search_results(term):
  """
  検索の実行。言語は日本語限定
  """
  search_results = API.GetSearch(term=term, geocode=None, 
    since_id=None, per_page=15, page=1, lang='ja', show_user='true', 
    query_users='false')
  return search_results


application = webapp.WSGIApplication([('/', followResultPage)],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
