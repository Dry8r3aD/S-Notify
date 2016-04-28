#!/usr/bin/env python
# encoding: utf-8


import requests
import argparse

from web import parse_weather

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt



def make_weather_image(data):
    min_temp = 9999
    max_temp = -9999

    temps = []
    times = [] 
    i = 0
    for d in data:
        temp = float(d['temp'])
        temps.append(temp)
        times.append(i*3)
        i = i+1
        if temp < min_temp:
            min_temp = temp
        if temp > max_temp:
            max_temp = temp
    plt.title("Today's Temperature")
    plt.xlabel('Time')
    plt.ylabel('Temp')
    plt.plot(times,temps,'b-')
    plt.plot(times,temps,'ro')
    plt.grid(True)
    plt.axis( [0,len(data)*3 , min_temp - 5, max_temp +5])
    plt.savefig("test.png")


def upload_file(channels,token,filename,title,initial_comment):
	data = {
		'channels' : channels,
		'token' : token,
		'filename' : filename,
		'title' : title,
		'username':'날씨맨',
		'initial_comment' : initial_comment
#    	'as_user' :,
#		'parse' :,
#		'link_names' :,
#		'attachments' :,
#		'unfurl_links' :,
#		'unfurl_media' :,
#		'icon_url':,
#		'icon_emoji':
	}
	with open(filename,'rb') as f:
		api_name = 'files.upload'
		r = requests.post('https://slack.com/api/{api_name}'.format(api_name = api_name),data=data,files={'file':f})


def post_message(message,token):
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
	upload_file('wf-team,@ywlee','xoxp-2745544825-39319659127-69811901892-caea7c9848','ss.png','dsfd','sdfsdf')
#    ws = parse_weather('1156054000')
#   make_weather_image(ws)
#   build_str = ""
#    w = ws[0]
#   for w in ws:
#    for k in w.keys():
#        v = w[k]
#        build_str = build_str +  str(k)  + ' - ' + str(v) + ' '
#    print build_str
#    post_message(build_str,  'xoxp-2745544825-39319659127-67642701462-fbc21db3ca')

