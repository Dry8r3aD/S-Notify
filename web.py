#!/usr/bin/env python
# encoding: utf-8

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET



def find_search_area(search_type , sido_code=None , gugun_code=None, dong_code=None ):

	base_url = 'http://www.kma.go.kr/weather/lifenindustry/sevice_rss.jsp'

	if sido_code != None or gugun_code != None or dong_code != None:
		url = base_url + '?'
	else:
		url = base_url

	if sido_code != None:
		url = url + ( 'search_area=%s' % sido_code)
	if gugun_code != None:
		url = url + ( 'search_area2=%s' % gugun_code)
	if dong_code !=None:
		url = url + ( 'search_area3=%s' % dong_code)

	source_code = requests.get(url)
	plain_text = source_code.text
	soup = BeautifulSoup(plain_text,'lxml')
	search_area_soup = soup.find(id=search_type).option

	if search_area_soup == None:
		return None
	while True:
		search_area_soup = search_area_soup.find_next_sibling()
		print search_area_soup
		if search_area_soup == None:
			break

def find_search_area_sido(sido_code):
	return find_search_area("search_area",sido_code)

def find_search_area_gugun():
	return find_search_area("search_area2",sido_code,gugun_code)

def find_search_area_dong():
	return find_search_area("search_area3",sido_code ,gugun_code ,dong_code)

def crawling():
	url = 'http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnld=108'
	source_code = requests.get(url)
	plain_text = source_code.text
	soup = BeautifulSoup(plain_text,'lxml')
	print soup


if __name__ == "__main__":
	find_search_area_sido()

