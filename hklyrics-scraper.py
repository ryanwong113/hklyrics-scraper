# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from sets import Set

import argparse
import codecs
import io
import json
import os
import urllib2
import sys

BASE_URL = 'https://mojim.com'
REMOVE_LYRICS_LINE = '更多更詳盡歌詞 在'.decode('utf-8')
PROVIDE_CONSTANT = '提供'.decode('utf-8')
LYRICIST_CONSTANT = '作詞'.decode('utf-8')
COMPOSER_CONSTANT = '作曲'.decode('utf-8')
ARRANGER_CONSTANT = '編曲'.decode('utf-8')
PRODUCER_CONSTANT = '監製'.decode('utf-8')
COLON_CONSTANT = '：'.decode('utf-8')

def read_data_from_file(filepath):
    with codecs.open(filepath, 'r', 'utf-8') as json_file:
        data = json.load(json_file, 'utf-8')
        return data


def write_data_to_file(filepath, data):
    with codecs.open(filepath, 'w', 'utf-8') as json_file:
        json_data = json.dumps(data, ensure_ascii=False, indent=4, separators=(',', ': '))
        json_file.write(unicode(json_data))


def write_song_data_to_file(singer_name, song_name, song_data):
    filepath = 'data/%s.json' % singer_name
    if os.path.isfile(filepath):
        data = read_data_from_file(filepath)
        data[song_name] = song_data
        write_data_to_file(filepath, data)
    else:
        write_data_to_file(filepath, {song_name: song_data})

def get_singer_url(singer_name):
    source_files = ['data/singers_male.json', 'data/singers_female.json', 'data/singers_group.json']
    for source_file in source_files:
        singers_data = read_data_from_file(source_file)
        if singer_name in singers_data:
            return singers_data[singer_name]

    raise Exception('Singer %s does not exist' % singer_name)


def load_scraped_songs_for_singer(singer_name):
    filepath = 'data/%s.json' % singer_name
    if os.path.isfile(filepath):
        return Set(read_data_from_file(filepath).keys())
    return Set()


def scrape_singer(singer_name):
    scraped_songs = load_scraped_songs_for_singer(singer_name)

    singer_url = get_singer_url(singer_name)
    singer_url = BASE_URL + singer_url[:len(singer_url)-4] + '-A1' + singer_url[len(singer_url)-4:]

    singer_page = urllib2.urlopen(singer_url, timeout=5)
    singer_soup = BeautifulSoup(singer_page.read(), 'lxml')

    div_section = singer_soup.find('div', {'id' : 'inS'})
    song_sections = div_section.find_all('dd', {'class' : ['hb2', 'hb3']})

    songs = {}
    for song_section in song_sections:
        song_span = song_section.find('span', {'class' : 'hc1'})

        song_name = song_span.getText().upper()

        if PROVIDE_CONSTANT in song_name or 'MEDLEY' in song_name:
            print 'Not scraping %s' % song_name
            continue

        if song_name in scraped_songs:
            print 'Already scraped %s' % song_name
            continue

        print 'Scraping %s' % song_name

        song_hyperlink = song_span.find('a')['href']

        song_url = BASE_URL + song_hyperlink
        song_page = urllib2.urlopen(song_url, timeout=5)
        song_soup = BeautifulSoup(song_page.read(), 'lxml')

        try:
            lyrics_section = song_soup.find('dd', {'id' : 'fsZx3'})

            lyricist = ''
            composer = ''
            arranger = ''
            producer = ''
            lyrics = ''
            for lyrics_section_element in lyrics_section.contents:
                if '<' not in lyrics_section_element and '[' not in lyrics_section_element:
                    if (isinstance(lyrics_section_element, basestring)) and (not REMOVE_LYRICS_LINE in lyrics_section_element):
                        if (LYRICIST_CONSTANT in lyrics_section_element):
                            lyricist = lyrics_section_element.split(COLON_CONSTANT)[1].strip()
                        elif (COMPOSER_CONSTANT in lyrics_section_element):
                            composer = lyrics_section_element.split(COLON_CONSTANT)[1].strip()
                        elif (ARRANGER_CONSTANT in lyrics_section_element):
                            arranger = lyrics_section_element.split(COLON_CONSTANT)[1].strip()
                        elif (PRODUCER_CONSTANT in lyrics_section_element):
                            producer = lyrics_section_element.split(COLON_CONSTANT)[1].strip()
                        else:
                            lyrics += lyrics_section_element
                    else:
                        lyrics += '\n'
            
            song = {
                'lyricist': lyricist,
                'composer': composer,
                'arranger': arranger,
                'producer': producer,
                'lyrics': lyrics
            }
            scraped_songs.add(song_name)
            write_song_data_to_file(singer_name, song_name, song)
        except Exception as e:
            print 'Exception when scraping %s, skipping: %s' % song_name, e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='To scrape Hong Kong lyrics.')
    parser.add_argument('--singer', nargs='?', help='singer name')
    
    args = parser.parse_args()
    if args.singer is not None:
        singer_name = unicode(args.singer, 'utf-8')
        print 'Scraping singer %s' % singer_name
        scrape_singer(singer_name)
    
        
