#!/usr/bin/env python
# encoding: utf-8

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET



def parse_weather( region_code ):
    url = 'http://www.kma.go.kr/wid/queryDFSRSS.jsp?zone=%s' % region_code 
    source_code  = requests.get(url)
    weather_soup = BeautifulSoup(source_code.text,'lxml')
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

	print url
	source_code = requests.get(url)
	plain_text = source_code.text

	soup = BeautifulSoup(plain_text,'lxml')
#	print soup.find(id=search_type)
	search_area_soup = soup.find(id=search_type).option

	if search_area_soup == None:
		return None
	area = [] 
	while True:
		search_area_soup = search_area_soup.find_next_sibling()
		if search_area_soup == None:
			break
		area.append({'value':search_area_soup['value'],'text':search_area_soup.find(text=True),'next':None})
	return area

def find_search_area_sido():
	return find_search_area("search_area")

def find_search_area_gugun(sido_code):
	return find_search_area("search_area2",sido_code)

def find_search_area_dong(sido_code , gugun_code):
	return find_search_area("search_area3",sido_code,gugun_code)

#def find_search_area_dong(sido_code , gugun_code, dong_code ):
#	return find_search_area("search_area3",sido_code ,gugun_code ,dong_code)

def crawling():
	url = 'http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnld=108'
	source_code = requests.get(url)
	plain_text = source_code.text
	soup = BeautifulSoup(plain_text,'lxml')

def show_register_list(cmd_stack):
    pass


ROOT_CMD_LIST =[
    {'display' : '1. 지역등록', 'sub' :show_register_list},
    {'display' : '2. 지역삭제', 'sub' : None},
    {'display' : '3. 알림시간 설정', 'sub' : None},
    {'display' : '4. 키등록', 'sub' : None},
    {'display' : '5. 채널등록', 'sub' : None}
] 

def print_cmd(current_cmd_list):
    for current_cmd in current_cmd_list:
        print current_cmd['display']

def print_sido_list():
	sido_area = find_search_area_sido()
	i = 0
	for sido in sido_area:
		print str(i)+'.' +  sido['text']
		i = i + 1

if __name__ == "__main__":
    cmd_stack = []
    current_cmd_list = ROOT_CMD_LIST
    while True:
        if type(current_cmd_list) is function:
            current_cmd_list()
        elif type(current_cmd_list) is list:
            print_cmd(current_cmd_list)
        n = input('명령어를 입력하세요:')
        if len(current_cmd_list) <= n or n < 0:
            continue
        cmd_stack.append(current_cmd_list)
        current_cmd_list = current_cmd_list[i]['sub']
        if current_cmd_list is None:
            break


#    ww = parse_weather('1156054000')
#    for w in ww:
#        print w

#	print_sido_list()
#	sido_area = find_search_area()
#	for sido in sido_area:
#		sido['next'] = find_search_area_gugun(sido['value'])
#		for gugun in sido['next']:
#			gugun['next'] = find_search_area_dong(sido['value'] ,gugun['value'] )
#			for dong in gugun['next']:
#				print dong['value']
#				print dong['text']


