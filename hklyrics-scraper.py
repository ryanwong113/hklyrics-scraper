from bs4 import BeautifulSoup

import io
import urllib2
import StringIO
import sys

MALE_ROOT_URL = 'http://lyric.musichk.org/male.htm'
FEMALE_ROOT_URL = 'http://lyric.musichk.org/female.htm'
GROUP_ROOT_URL = 'http://lyric.musichk.org/group.htm'

ROOT_URLS = [MALE_ROOT_URL, FEMALE_ROOT_URL, GROUP_ROOT_URL]


def scrap_url(url):
	page = urllib2.urlopen(url)
	soup = BeautifulSoup(page, 'html.parser')
	print soup.prettify(encoding='unicode')


def run_scraper():
	scrap_url(MALE_ROOT_URL)
	# for root_url in ROOT_URLS:
	# 	scrap_url(root_url)
	

if __name__ == "__main__":
	run_scraper()
