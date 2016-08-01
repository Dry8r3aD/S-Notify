#!/usr/bin/env python
# encoding: utf-8


import requests
import argparse

def postMessage(message,token):
	data = {
		'channel' : 'wf-team',
		'text' : message,
		'token' : token,
		'username' : 'name'
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
	parser = argparse.ArgumentParser()
	parser.add_argument('-m')
	parser.add_argument('-t')
	args = parser.parse_args()
	if args.m and args.t: 
		postMessage(args.m,args.t)


