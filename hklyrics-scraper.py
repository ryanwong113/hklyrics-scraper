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


def append_data_to_file(filename, data):
    if os.path.isfile(filename):
        json_data_from_file = read_data_from_file(filename)

        os.remove(filename)
    else:
        json_data_from_file = {}

    for singer_name, albums_and_songs in data.iteritems():
        json_data_from_file[singer_name] = albums_and_songs

    write_data_to_file(filename, json_data_from_file)


def add_checkpoint(filename, checkpoint_type, checkpoint_content):
    checkpoint_json_filename = filename

    if os.path.isfile(checkpoint_json_filename):
        checkpoint_data = read_data_from_file(checkpoint_json_filename)
        checkpoint_data[checkpoint_type].append(checkpoint_content)

        os.remove(checkpoint_json_filename)
    else:
        checkpoint_data = {}
        checkpoint_data[checkpoint_type] = [checkpoint_content]

    write_data_to_file(checkpoint_json_filename, checkpoint_data)


def add_singer_checkpoint(singer_name):
    add_checkpoint('checkpoint.json', 'singer', singer_name)


def add_failed_song(song_name):
    add_checkpoint('failures.json', 'song', song_name)


def add_hyperlinks(hyperlinks):
    append_data_to_file('hyperlinks.json', hyperlinks)


def get_lyrics(song_name, url):
    try:
        page = urllib2.urlopen(url, timeout=5)
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

        return lyrics

    except Exception as ex:
        print 'Exception when scraping song %s' % ex
        add_failed_song(song_name)


def get_albums_and_songs(url):
    try:
        page = urllib2.urlopen(url, timeout=5)
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
                
                songs.append({song_name : song_hyperlink})
                
            albums[album_name] = songs

        return albums

    except Exception as ex:
        print 'Exception when scraping singer: %s' % ex


def get_singers(url):
    try:
        page = urllib2.urlopen(url, timeout=5)
        soup = BeautifulSoup(page.read(), 'lxml')

        singers = {}

        ul_section = soup.find('ul', {'class' : 's_listA'})
        links = ul_section.find_all('a')
        for link in links:
            singer_name = link.getText()
            singer_hyperlink = link.get('href')
            
            singers[singer_name] = singer_hyperlink

        return singers
    except Exception as ex:
        print 'Exception when scraping singer: %s' % ex


def run_scraper():
    checkpoint_data = read_data_from_file('checkpoint.json')
    singers_checkpoint = checkpoint_data['singer']

    for root_url in ROOT_URLS:
        singers = get_singers(root_url)

        for singer_name, singer_hyperlink in singers.iteritems():
            if singer_name in singers_checkpoint:
                print 'Singer %s has already been scraped, skipping...' % singer_name
            else:
                print 'Scraping singer %s...' % singer_name
                albums_and_songs = get_albums_and_songs(BASE_URL + singer_hyperlink)

                print 'Retrived %d albums.' % len(albums_and_songs)

                albums_and_songs_with_lyrics = {}
                for index, (album_name, songs) in enumerate(albums_and_songs.iteritems(), 1):
                    print '%d: Album %s has %d songs' % (index, album_name, len(songs))

                    songs_with_lyrics = []
                    for song in songs:
                        for song_name, song_hyperlink in song.iteritems():
                            print 'Getting lyrics for song %s' % song_name
                            lyrics = get_lyrics(song_name, BASE_URL + song_hyperlink)
                            songs_with_lyrics.append({song_name : lyrics})

                    albums_and_songs_with_lyrics[album_name] = songs_with_lyrics

                print 'Finished scraping for %s. Appending data to file...' % singer_name
                append_data_to_file('data.json', {singer_name: albums_and_songs_with_lyrics})

                print 'Adding %s to checkpoint...' % singer_name
                add_singer_checkpoint(singer_name)

                exit(0)
    

if __name__ == "__main__":
    run_scraper()
