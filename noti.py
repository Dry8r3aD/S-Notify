import requests
import argparse



def postMessage(message):
	data = {
		'channel' : 'wf-team',
		'text' : message,
		'token' : 'xoxp-2745544825-39319659127-44099752723-933c5d1165',
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
	args = parser.parse_args()
	if args.m: 
		postMessage(args.m)

