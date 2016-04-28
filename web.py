#!/usr/bin/env python
# encoding: utf-8

import os
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

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
		w = {'시간':weather_data.hour.text,
			'기온':weather_data.temp.text,
			'강수확률%':weather_data.pop.text,
			'강수량 mm':weather_data.r12.text,
			'습도':weather_data.reh.text}
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


def save_channel():
	if g_registered_slack_channel.count == 0:
		return False
	with open('slack_channel','w') as f:
		for slack_channel in g_registered_slack_channel:
			f.write(slack_channel)
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
	
	
def register_day_of_the_week(arg_list):
	day_of_the_week = arg_list[0]
	g_registered_day_of_the_week.add(day_of_the_week)
	print '%s요일이 등록되었습니다.' % day_of_the_week
	return None

def unregister_day_of_the_week(arg_list):
	build_str = ''
	for day_of_the_week in g_registered_day_of_the_week:
		build_str = day_of_the_week+' '
	if len(g_registered_day_of_the_week) == 0:
		print '등록된 요일이 없습니다.'
		return None
	print build_str+' 요일이 등록되어 있습니다.'
	while True:
		n =  raw_input('삭제할 요일을 입력하세요 (월~일):')
		print n
		n = n.strip()
		if n == '월'\
			or n == '화'\
			or n == '수'\
			or n == '목'\
			or n == '금'\
			or n == '토'\
			or n == '일':
			break
	try:	
		g_registered_day_of_the_week.remove(n)
		print '요일이 삭제되었습니다.'
	except KeyError:
		print '요일이 등록되어 있지 않습니다.'
	return None

def register_time(arg_list):
	while True:
		n = input('등록할 시간을 입력하세요 (0 ~ 23):')
		if n < 0 or n >= 24:
			continue
		t_hour = n
		n = input('등록할 분을 입력하세요 (0 ~59):')
		if n < 0 or n >= 59:
			continue
		t_min = n

	#이전등록되어진것들중에 있는가?

	g_registered_time.append({'시간':t_hour , '분':t_min})
	return None

def unregister_time(arg_list):
	return None

ALARM_DAY_OF_THE_WEEK = [
	{'display' : '월요일' , 'sub':register_day_of_the_week,'args':['월']},
	{'display' : '화요일' , 'sub':register_day_of_the_week,'args':['화']},
	{'display' : '수요일' , 'sub':register_day_of_the_week,'args':['수']},
	{'display' : '목요일' , 'sub':register_day_of_the_week,'args':['목']},
	{'display' : '금요일' , 'sub':register_day_of_the_week,'args':['금']},
	{'display' : '토요일' , 'sub':register_day_of_the_week,'args':['토']},
	{'display' : '일요일' , 'sub':register_day_of_the_week,'args':['일']}
]
ALARM_CMD_LIST = [
	{'display' : '요일등록', 'sub':ALARM_DAY_OF_THE_WEEK,'args':None},
	{'display' : '요일삭제', 'sub':unregister_day_of_the_week,'args':None},
	{'display' : '시간등록', 'sub':register_time,'args':None},
	{'display' : '시간삭제', 'sub':unregister_time,'args':None}
]
ROOT_CMD_LIST = [
    {'display' : '지역등록', 'sub' :get_cmd_list_by_find_search_area_sido, 'args' : None },
    {'display' : '지역삭제', 'sub' : unregister_region , 'args' : None },
    {'display' : '알림시간 설정', 'sub' : ALARM_CMD_LIST, 'args' : None },
    {'display' : '슬랙 키등록', 'sub' : register_slack_key , 'args' : None },
    {'display' : '채널등록', 'sub' : register_channel , 'args' : None},
    {'display' : '채널삭제', 'sub' : unregister_channel , 'args' : None}
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
	global g_registered_day_of_the_week
	global g_registered_time
	global g_registered_region_list
	global g_registered_slack_key
	global g_registered_slack_channel

	g_registered_day_of_the_week =set()
	g_registered_time = []
	g_registered_region_list = []
	g_registered_slack_key = ""
	g_registered_slack_channel = []

	load_region()
	load_channel()
	load_slack_key()
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

