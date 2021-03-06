#!/usr/bin/env python
# encoding: utf-8


import sys
import subprocess
import os
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def make_weather_image(data):
    min_temp = 9999
    max_temp = -9999

    temps = []
    times = [] 
    i = 0
    base_time = int(data[0]['time'])
    for d in data:
        temp = float(d['temp'])
        temps.append(temp)
        times.append(base_time + i*3)
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
    plt.axis( [base_time,base_time + len(data)*3 , min_temp - 5, max_temp +5])
    plt.savefig("test.png")


def upload_file(channels,token,filename,title,initial_comment):
	data = {
		'channels' : channels,
		'token' : token,
		'filename' : filename,
		'title' : title,
		'username':'날씨맨',
		'initial_comment' : initial_comment
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
	}
	api_name = 'chat.postMessage'
	r = requests.post('https://slack.com/api/{api_name}'.format(api_name = api_name),data=data)


def crawl_region_weather(region_code):
    url = 'http://www.kma.go.kr/wid/queryDFSRSS.jsp?zone=%s' % region_code 
    source_code  = requests.get(url)
    return BeautifulSoup(source_code.text,'lxml')
    
def parse_region_name(region_code):
    weather_soup = crawl_region_weather(region_code)
    return weather_soup.find('category').text

def parse_weather( region_code ):
    weather_soup = crawl_region_weather(region_code)
    weather_data = weather_soup.find('body').data
    weather = []
    while True:
        if weather_data == None:
            break
        w = {'time':weather_data.hour.text,
            'temp':weather_data.temp.text,
            'precipitation_prob':weather_data.pop.text,
            'amount_of_precipitation':weather_data.r12.text,
            'humidity':weather_data.reh.text}
        weather.append(w)
        weather_data = weather_data.find_next_sibling()
    return weather

def find_search_area(search_type="search_area" , sido_code=None , gugun_code=None, dong_code=None ):
    base_url = 'http://www.kma.go.kr/weather/lifenindustry/sevice_rss.jsp'


    if sido_code != None or gugun_code != None or dong_code != None:
        if sido_code != None:
            url = base_url + ( '?sido=%s' % sido_code)
        if gugun_code != None:
            url = url + ( '&gugun=%s' % gugun_code)
        if dong_code !=None:
            url = url + ( '&dong=%s' % dong_code)
    else:
        url = base_url

    source_code = requests.get(url)
    plain_text = source_code.text

    soup = BeautifulSoup(plain_text,'lxml')
    search_area_soup = soup.find(id=search_type).option

    if search_area_soup == None:
        return None
    area = [] 
    while True:
        search_area_soup = search_area_soup.find_next_sibling()
        if search_area_soup == None:
            break
        area.append({'args':[search_area_soup['value']],'display':search_area_soup.find(text=True),'sub':None})
    return area

def find_search_area_sido():
    return find_search_area("search_area")

def find_search_area_gugun(sido_code):
    return find_search_area("search_area2",sido_code)

def find_search_area_dong(sido_code , gugun_code):
    return find_search_area("search_area3",sido_code,gugun_code)

def register_sido_gugun_dong(arg_list):
    region_name = parse_region_name(arg_list[0])
    region_key  = arg_list[0]
    for region in g_registered_region_list:
        if region['key']== region_key:
            print '이미 등록되어 있습니다.'
            return None
    g_registered_region_list.append({'name':region_name,'key':arg_list[0]})
    save_region()
    print region_name
    print '지역이 등록되었습니다.'
    return None

def get_cmd_list_by_find_search_area_dong(arg_list):
    dong_list = find_search_area_dong(arg_list[0],arg_list[1])
    for dong in dong_list:
        dong['sub'] = register_sido_gugun_dong
    return dong_list

def get_cmd_list_by_find_search_area_gugun(arg_list):
    gugun_list = find_search_area_gugun(arg_list[0])
    for gugun in gugun_list:
        gugun['sub'] = get_cmd_list_by_find_search_area_dong
        gugun['args'].insert(0,arg_list[0]) 
    return gugun_list

def get_cmd_list_by_find_search_area_sido(arg_list):
    sido_list = find_search_area_sido()
    for sido in sido_list:
        sido['sub'] = get_cmd_list_by_find_search_area_gugun
    return sido_list

def unregister_region(arg_list):
    if len(g_registered_region_list) == 0:
        print '등록된 지역이 없습니다.'
        return None
    print '등록된 리스트'
    for region in g_registered_region_list:
        print region['key']+':'+ region['name']
    print '---------------------------------------------'
    n = input('삭제할 키값을 입력하세요:')

    b_del = False
    for i,dic in enumerate(g_registered_region_list):
        print dic['key']
        if dic['key'] == str(n):
            g_registered_region_list.pop(i)
            b_del = True
    if b_del == True:
        print '삭제되었습니다.'
    else:
        print '키가 없습니다.'
    save_region()
    return None

def save_region():
    if len(g_registered_region_list) == 0:
        return
    with open('slack_region','w') as f:
        for region in g_registered_region_list:
            f.write(region['key']+'\n')

def load_region():
    global g_registered_region_list 
    g_registered_region_list = []
    if os.path.exists('slack_region') is False:
        return 
    with open('slack_region','r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip('\n')
            g_registered_region_list.append({'name':parse_region_name(line) , 'key':line})

def load_slack_key():
    global g_registered_slack_key
    if os.path.exists('slack_key') is False:
        return 
    with open('slack_key','r') as f:
        g_registered_slack_key = f.read()
	g_registered_slack_key = g_registered_slack_key.replace('\n','').strip()

def save_slack_key():
    if g_registered_slack_key == "":
        return False 
    with open('slack_key','w') as f:
        f.write(g_registered_slack_key)
    return True

def register_slack_key(arg_list):
    global g_registered_slack_key
    n = raw_input('슬랙토큰을 입력하세요:')
    g_registered_slack_key =  n 
    print g_registered_slack_key
    if save_slack_key() == True:
        print '슬랙토큰이 등록되었습니다.'
    else:
        print '슬랙토큰이 등록에 실패했습니다.'
    return None

def load_channel():
	global g_registered_slack_channel
	if os.path.exists('slack_channel') is False:
		return
	with open('slack_channel','r') as f:
		g_registered_slack_channel = f.readlines()
	tmp_list = []
	for slack_channel in g_registered_slack_channel:
	 	slack_channel = slack_channel.replace('\n','')
		slack_channel = slack_channel.strip()
		if slack_channel != '':
			tmp_list.append(slack_channel)
	g_registered_slack_channel = tmp_list

def save_channel():
	if g_registered_slack_channel.count == 0:
		return False
	with open('slack_channel','w') as f:
		for slack_channel in g_registered_slack_channel:
			f.write(slack_channel)
			f.write('\n')
	return True

def register_channel(arg_list):
    n = raw_input('채널을 입력하세요:')
# 채널인지 검증
    try:
        g_registered_slack_channel.index(n)
        print '채널이 이미 있습니다.'
        return None
    except ValueError:
        pass

    g_registered_slack_channel.append(n)
    save_channel()
    print '채널이 등록되었습니다.'
    return None

def unregister_channel(arg_list):
    if len(g_registered_slack_channel) is 0:
        print '등록된 채널이 없습니다.'
        return None
    build_str = ''
    for slack_channel in g_registered_slack_channel:
        build_str = build_str + slack_channel + ' '
    print '등록된 채널리스트 : ' + build_str
    n = raw_input('삭제할 채널을 입력하세요:')

    try:
        g_registered_slack_channel.remove(n)
        save_channel()
        print '채널이 삭제 되었습니다.'
    except ValueError:
        print '채널삭제 실패하였습니다.'

def make_current_crontab_file(filename):
    try: 
	cmd_str = 'crontab -l > %s' % filename
        ret = subprocess.call(cmd_str,shell=True)
        if ret < 0 :
            print '크론탭불러오기 실패'
            return False
    except OSError:
        print '크론탭불러오기 실패'
        return False
    return True

def apply_crontab_file(filename):
	try:
		cmd_str = 'crontab %s' % filename
		ret = subprocess.call(cmd_str,shell=True)
		if ret < 0 :
			print '크론탭 등록 실패'
	except OSError:
		print '크론탭 등록 실패'

def get_crontab_info(arg_list):

	tmp_crontab_file = 'tmp_crontab'
	if make_current_crontab_file(tmp_crontab_file) == False:
		return None
	save_lines = []
	with open(tmp_crontab_file,'r') as f:
		lines  = f.readlines()
		for line in lines:
			if line.find(g_program_name) != -1:
				splited = line.split(' ')
				display_str = '분- ' + splited[0] + '    시간- ' + splited[1] + '    요일- '+ splited[4]
				save_lines.append({'display':display_str, 'sub':unregister_time , 'args':[line]})
	if len(save_lines) == 0:
		print '삭제할 리스트가 없습니다.'
		return None
	return save_lines

def make_crontab_line(info):
    build_str =  str(info['min']) + ' ' + str(info['hour']) + ' * * ' + info['dow'] +' ' + g_program_name +' -b True \n'
    return build_str

def set_crontab_info(info):
	tmp_crontab_file = 'tmp_crontab'

	make_current_crontab_file(tmp_crontab_file)
	crontab_line = make_crontab_line(info)
	with open(tmp_crontab_file,'a') as f:
		f.write(crontab_line)
	apply_crontab_file(tmp_crontab_file)

def print_dow(dow):
    if len(dow) == 0 :
        print '선택된 요일이 없습니다.'
        return 
    dow_strs = ['일요일','월요일','화요일','수요일','목요일','금요일','토요일']
    build_str = ''

    for d in dow:
        build_str = build_str + dow_strs[d] + ' '
    print '선택요일:' + build_str 

def register_time(arg_list):
    dow = []
    while True:
        print_dow(dow)
        print '0. 일요일'
        print '1. 월요일'
        print '2. 화요일'
        print '3. 수요일'
        print '4. 목요일'
        print '5. 금요일'
        print '6. 토요일'
        print '7. 모든요일'
        print '8. 요일선택 끝내기'
        n = input( '요일을 선택하세요:')
        if n == 8:
            if len(dow) == 0:
                return None
            else:
                break
        elif n == 7:
            dow = [0,1,2,3,4,5,6]
        elif n >= 0 and n <=6 :
            try:
                dow.remove(n)
            except ValueError:
                dow.append(n)
                dow.sort()

    while True:
        n = input('등록할 시간을 입력하세요 (0 ~ 23):')
        if n >= 0 or n  < 24:
            t_hour = n
            break

    while True:
        n = input('등록할 분을 입력하세요 (0 ~59):')
        if n >= 0 or n < 59:
            t_min = n
            break

    dow = [ str(i) for i in dow]
    set_crontab_info({'min':t_min,'hour':t_hour,'dow':','.join(dow)})
    return None

def unregister_time(arg_list):
	org_str = arg_list[0]
	tmp_crontab_file =  'tmp_crontab'
	tmp_crontab_file_2 = 'tmp_crontab_2'
	
	make_current_crontab_file(tmp_crontab_file)
	with open(tmp_crontab_file_2,'w') as wf:
		with open(tmp_crontab_file,'r') as rf:
			lines  = rf.readlines()
			for line in lines:
				if line.find(org_str) == -1:
					wf.write(line)
	apply_crontab_file(tmp_crontab_file_2)

def post_test_weather_message(arg_list):
	slack_channels = ','.join(g_registered_slack_channel)
	for region in g_registered_region_list:
		ws = parse_weather(region['key'])
		make_weather_image(ws)
		upload_file(slack_channels,g_registered_slack_key,'test.png','날씨정보','맑을까?')
	return None

ALARM_CMD_LIST = [
    {'display' : '시간등록', 'sub':register_time,'args':None},
    {'display' : '시간삭제', 'sub':get_crontab_info, 'args':None}
]

ROOT_CMD_LIST = [
    {'display' : '지역등록', 'sub' :get_cmd_list_by_find_search_area_sido, 'args' : None },
    {'display' : '지역삭제', 'sub' : unregister_region , 'args' : None },
    {'display' : '알림시간 설정', 'sub' : ALARM_CMD_LIST, 'args' : None },
    {'display' : '슬랙 키등록', 'sub' : register_slack_key , 'args' : None },
    {'display' : '채널등록', 'sub' : register_channel , 'args' : None},
    {'display' : '채널삭제', 'sub' : unregister_channel , 'args' : None},
    {'display' : '테스트보내기', 'sub' : post_test_weather_message  , 'args' : None}
] 

def print_cmd(current_cmd_list):
    i = 0
    for current_cmd in current_cmd_list:
        print str(i)+'. ' + current_cmd['display']
        i = i + 1
    if current_cmd_list == ROOT_CMD_LIST:
        print str(i)+'. '+'프로그램 종료'
    else:
        print str(i)+'. ' + '뒤로가기'

def test_func():
    pass


class CmdContext(object):

    def __init__(self):
        self.clear()

    def clear(self):
        self.cmd_stack =[]
        self.cmd_arg_stack = []
        self.current_cmd_list = ROOT_CMD_LIST
        self.current_cmd_list_arg = None

    def pop(self):
        self.current_cmd_list  =  self.cmd_stack.pop()
        self.current_cmd_list_arg = self.cmd_arg_stack.pop()

    def push(self):
        self.cmd_stack.append(self.current_cmd_list)
        self.cmd_arg_stack.append(self.current_cmd_list_arg)




if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-b')
	args = parser.parse_args()
	global g_program_name
	global g_registered_region_list
	global g_registered_slack_key
	global g_registered_slack_channel

	g_program_name = os.path.abspath(sys.argv[0])
	g_registered_region_list = []
	g_registered_slack_key = ""
	g_registered_slack_channel = []
	
	load_region()
	load_channel()
	load_slack_key()
	if args.b is not None:
		post_test_weather_message(None)
		exit(0)

	cc = CmdContext()

	while True:
		if type(cc.current_cmd_list) is type(test_func):
			cc.current_cmd_list = cc.current_cmd_list(cc.current_cmd_list_arg)
			if cc.current_cmd_list is None:
				cc.clear()
		print_cmd(cc.current_cmd_list)
		 
		n = input('명령어를 입력하세요:')
		 
		if len(cc.current_cmd_list) < n or n < 0:
		 	continue
		if len(cc.current_cmd_list) == n:
			if cc.current_cmd_list == ROOT_CMD_LIST:
				print '프로그램을 종료합니다.'
				exit(0)
			else:
				cc.pop()
				continue
		cc.push()
		cc.current_cmd_list_arg = cc.current_cmd_list[n]['args']
		cc.current_cmd_list = cc.current_cmd_list[n]['sub']
		if cc.current_cmd_list is None:
			cc.clear()

