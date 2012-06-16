#!/usr/bin/env python

import tornado, tornado.ioloop, tornado.httpclient

import json, urllib

def handle_request(response):
    if response.error:
        print "Error:", response.error
    else:
        result = json.loads(response.body)
        print result[1]
    tornado.ioloop.IOLoop.instance().stop()

http_client = tornado.httpclient.AsyncHTTPClient()
request_url = "http://suggestqueries.google.com/complete/search?client=firefox&q="
request_url_bing = "http://api.bing.com/osjson.aspx?"
request_term = "an "

events = { 'query' : request_term.lower() }
request = urllib.urlencode(events)

http_client.fetch(request_url_bing + request, handle_request)
tornado.ioloop.IOLoop.instance().start()
