# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

import io
import json
import os
import urllib2
import sys

BASE_URL = 'https://mojim.com'

MALE_ROOT_URL = 'https://mojim.com/twza1.htm'
FEMALE_ROOT_URL = 'https://mojim.com/twzb1.htm'
GROUP_ROOT_URL = 'https://mojim.com/twzc1.htm'

ROOT_URLS = [MALE_ROOT_URL, FEMALE_ROOT_URL, GROUP_ROOT_URL]

REMOVE_LYRICS_LINE = '更多更詳盡歌詞 在'.decode('utf-8')


def write_data_to_file(filename, data):
    with io.open(filename, 'w', encoding='utf-8') as json_file:
        json_data = json.dumps(data, ensure_ascii=False, indent=4, separators=(',', ': '))
        json_file.write(unicode(json_data))


def read_data_from_file(filename):
    with io.open(filename, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        return data


def add_checkpoint(checkpoint_type, checkpoint_content):
    checkpoint_json_filename = 'checkpoint.json'

    if os.path.isfile(checkpoint_json_filename):
        checkpoint_data = read_data_from_file(checkpoint_json_filename)
        checkpoint_data[checkpoint_type] = checkpoint_content

        os.remove(checkpoint_json_filename)
    else:
        checkpoint_data = {}
        checkpoint_data['singer'] = ''
        checkpoint_data['album'] = ''
        checkpoint_data['song'] = ''
        checkpoint_data[checkpoint_type] = checkpoint_content

    write_data_to_file(checkpoint_json_filename, checkpoint_data)

def add_song_checkpoint(song_name):
    add_checkpoint('song', song_name)

def add_album_checkpoint(album_name):
    add_checkpoint('album', album_name)

def add_singer_checkpoint(singer_name):
    add_checkpoint('singer', singer_name)


def scrap_song(song_name, song_url):
    print 'Scraping song %s from %s' % (song_name, song_url)
    page = urllib2.urlopen(song_url, timeout=5)
    soup = BeautifulSoup(page.read(), 'lxml')

    lyrics_section = soup.find('dd', {'id' : 'fsZx3'})

    lyrics = ''
    for lyrics_section_element in lyrics_section.contents:
        if '[' in lyrics_section_element:
            break
        else:
            if isinstance(lyrics_section_element, basestring) and not REMOVE_LYRICS_LINE in lyrics_section_element:
                lyrics += lyrics_section_element
            else:
                lyrics += '\n'

    add_song_checkpoint(song_name)

    return lyrics


def scrap_singer(singer_name, singer_url):
    print 'Scraping singer %s from %s' % (singer_name, singer_url)
    page = urllib2.urlopen(singer_url, timeout=5)
    soup = BeautifulSoup(page.read(), 'lxml')

    albums = {}

    div_section = soup.find('div', {'id' : 'inS'})
    
    dd_sections = div_section.find_all('dd', {'class' : ['hb2', 'hb3']})
    
    for dd_section in dd_sections:

        album_span = dd_section.find('span', {'class' : 'hc1'})
        album_name = album_span.getText()
        album_hyperlink = album_span.get('href')
       
        song_spans = dd_section.find_all('span', {'class' : ['hc3', 'hc4']})

        song_links = []
        for song_span in song_spans:
            song_links += song_span.find_all('a')

        songs = []

        for song_link in song_links:
            song_name = song_link.getText()
            song_hyperlink = song_link.get('href')
            
            songs.append({song_name : scrap_song(song_name, BASE_URL + song_hyperlink)})
            
        albums[album_name] = songs

        add_album_checkpoint(album_name)

        # TODO: Remove the break
        # break

    add_singer_checkpoint(singer_name)

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
        
        singers[singer_name] = scrap_singer(singer_name, BASE_URL + singer_hyperlink)

        # TODO: Remove the break
        break

    return singers


def run_scraper():
    for root_url in ROOT_URLS:
        data = scrap_url(root_url)
        write_data_to_file('data.json', data)

        # TODO: Remove the break
        break
    

if __name__ == "__main__":
    run_scraper()
