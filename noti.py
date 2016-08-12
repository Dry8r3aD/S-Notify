#!/usr/bin/env python
# encoding: utf-8


import requests
import argparse

from web import parse_weather

def postMessage(message,token):
	data = {
		'channel' : 'wf-team',
		'text' : message,
		'token' : token,
		'username' : '날씨맨'
#    	'as_user' :,
#		'parse' :,
#		'link_names' :,
#		'attachments' :,
#		'unfurl_links' :,
#		'unfurl_media' :,
#		'icon_url':,
#		'icon_emoji':
	}
	api_name = 'chat.postMessage'
	r = requests.post('https://slack.com/api/{api_name}'.format(api_name = api_name),data=data)

if __name__ == "__main__":
#	parser = argparse.ArgumentParser()
#	parser.add_argument('-m')
#	parser.add_argument('-t')
#	args = parser.parse_args()

#	if args.m and args.t: 
#    	postMessage(args.m,args.t)
    ws = parse_weather('1156054000')
    build_str = ""
    w = ws[0]
#   for w in ws:
    for k in w.keys():
        v = w[k]
        build_str = build_str +  str(k)  + ' - ' + str(v) + ' '

    postMessage(build_str,  'xoxp-2745544825-39319659127-67642701462-fbc21db3ca')

