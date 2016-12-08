from bs4 import BeautifulSoup

import codecs
import io
import json
import urllib2
import StringIO
import sys

BASE_URL = 'https://mojim.com'

MALE_ROOT_URL = 'https://mojim.com/twza1.htm'
FEMALE_ROOT_URL = 'https://mojim.com/twzb1.htm'
GROUP_ROOT_URL = 'https://mojim.com/twzc1.htm'

ROOT_URLS = [MALE_ROOT_URL, FEMALE_ROOT_URL, GROUP_ROOT_URL]


def scrap_song(song_url):
    print 'Scraping song from {}'.format(song_url)
    page = urllib2.urlopen(song_url, timeout=5)
    soup = BeautifulSoup(page.read(), 'lxml')

    lyrics_section = soup.find('dd', {'id' : 'fsZx3'})

    print lyrics_section.contents

    lyrics_section_string = str(lyrics_section).decode('utf-8')
    lyrics_section_string.replace('<br/>', '\n')

    lyrics = ''
    for lyrics_line in lyrics_lines:
        lyrics += lyrics_line.getText() + '\n'

    return lyrics_lines




def scrap_singer(singer_url):
    print 'Scraping singer from {}'.format(singer_url)
    page = urllib2.urlopen(singer_url, timeout=5)
    soup = BeautifulSoup(page.read(), 'lxml')

    albums = {}

    div_section = soup.find('div', {'id' : 'inS'})
    
    dd_sections = div_section.find_all('dd', {'class' : ['hb2', 'hb3']})
    
    for dd_section in dd_sections:

        album_span = dd_section.find('span', {'class' : 'hc1'})
        album_name = album_span.getText()
        album_hyperlink = album_span.get('href')
       
        song_span = dd_section.find('span', {'class' : ['hc3', 'hc4']})
        song_links = song_span.find_all('a')
        
        songs = {}

        for song_link in song_links:
            song_name = song_link.getText()
            song_hyperlink = song_link.get('href')
            
            songs[song_name] = scrap_song(BASE_URL + song_hyperlink)
            
        albums[album_name] = songs

    return albums


def scrap_url(url):
    print 'Scraping from {}...'.format(url)
    page = urllib2.urlopen(url, timeout=5)
    soup = BeautifulSoup(page.read(), 'lxml')

    singers = {}

    ul_section = soup.find('ul', {'class' : 's_listA'})
    links = ul_section.find_all('a')
    for link in links:
        singer_name = link.getText()
        singer_hyperlink = link.get('href')
        
        write_data_to_file(singer_name)

        singers[singer_name] = scrap_singer(BASE_URL + singer_hyperlink)

        break

    return singers

    
def write_data_to_file(data):
    with io.open('data.json', 'w', encoding='utf-8') as json_file:
        json_data = json.dumps(data, ensure_ascii=False)
        json_file.write(unicode(json_data))


def run_scraper():
    data = scrap_url(MALE_ROOT_URL)
    #write_data_to_file(data)
    # for root_url in ROOT_URLS:
    # 	scrap_url(root_url)
	

if __name__ == "__main__":
    run_scraper()
