from bs4 import BeautifulSoup

import io
import urllib2
import StringIO
import sys

BASE_URL = 'http://lyric.musichk.org/'

MALE_ROOT_URL = 'http://lyric.musichk.org/male.htm'
FEMALE_ROOT_URL = 'http://lyric.musichk.org/female.htm'
GROUP_ROOT_URL = 'http://lyric.musichk.org/group.htm'

ROOT_URLS = [MALE_ROOT_URL, FEMALE_ROOT_URL, GROUP_ROOT_URL]


def scrap_song(song_url):
    print 'Scraping song...'


def scrap_album(album_url):
    print 'Scraping album...'


def scrap_singer(singer_url):
    print 'Scraping singer {}'.format(singer_url)
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())

    albums = {}
    links = soup.find_all('a')
    for link in links:
        album_name = link.getText()
        album_hyperlink = link.get('href')
        if album_name and 'main1' in album_hyperlink:
            albums[album_name] = scrap_album(BASE_URL + album_hyperlink)

    return albums


def scrap_url(url):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())

    singers = {}
    links = soup.find_all('a')
    for link in links:
        singer_name = link.getText()
        singer_hyperlink = link.get('href')
        if singer_name and 'main1' in singer_hyperlink:
            singers[singer_name] = scrap_singer(BASE_URL + singer_hyperlink)

    return singers


def run_scraper():
    scrap_url(MALE_ROOT_URL)
    # for root_url in ROOT_URLS:
    # 	scrap_url(root_url)
	

if __name__ == "__main__":
    run_scraper()
