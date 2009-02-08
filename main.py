#coding: utf-8
#Xurrency.comから取得したRSSをJSONに変換するサービス
import sys
sys.path.append("./lib")

from appengine_utilities import cache
from appengine_utilities import cron
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
import feedparser
import demjson
import logging

def log(val):
  logging.info(val)

class LocalCache:
  local_cache = cache.Cache()

  def get(self,key):
    return self.local_cache[key]

  def update(self,key):
    data_url = 'http://xurrency.com' + key
    feed_xml = urlfetch.fetch(data_url).content
    feed_obj = feedparser.parse(feed_xml)
    feed_json = demjson.encode(feed_obj.entries)
    self.local_cache[key] = feed_json

  get    = classmethod(get)
  update = classmethod(update)

class Result(webapp.RequestHandler):
  def get(self):
    req = self.request
    path = req.path
    log('request path:' + path)
    try:
      value = LocalCache.get(path)
      self.response.out.write(value)
    except KeyError:
      log('no value. update.')
      LocalCache.update(path)
      self.redirect(req.path) 

application = webapp.WSGIApplication([('/.*',Result)],
                                      debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()

