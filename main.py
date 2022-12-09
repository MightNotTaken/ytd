from pytube import Playlist, YouTube
import os
import shutil
from threading import Thread
from time import sleep


INDIVIDUAL_VIDEO = 1
PLAY_LIST        = 2
INVALID_URL      = 3

def get_playlist(url: str) -> Playlist:
    try:
        return Playlist(url)
    except Exception as e:
        print(e)
    return None

directory = ''
current_video = {
    'path': '',
    'title': '',
    'length': 0,
    'downloaded': True,
    'progress': 0,
    'index': 0,
    'remaining': 100
}

def video_progress_callback(stream, bytes, remaining_length):
    current_video['remaining'] = remaining_length
    if remaining_length > 0:
        percentage = (current_video['length'] - remaining_length) * 100 / current_video['length']
        while current_video['progress'] < percentage:
            current_video['progress'] += 2
            print('-', end='')


def video_complete_callback(stream, filename):
    while current_video['progress'] < 100:
        current_video['progress'] += 2
        print('-', end='')
    current_video['path'] = filename
    current_video['downloaded'] = True
    print('>')
    
def remove_special_characters(filename: str):
    special_chars = ['~', '#', '%', '&', '*', '{', '}', '\\', ':', '<', '>', '?', '/', '+', '|', '.']
    for char in special_chars:
        filename = filename.replace(char, '_')
    return filename

def download(url_data):
    url = url_data['url']
    try:
        video = YouTube(url, video_progress_callback, video_complete_callback)
        current_video['length'] = video.streams.get_highest_resolution().filesize
        current_video['title'] = remove_special_characters(video.title)
        current_video['progress'] = 0
        current_video['remaining'] = 100
        current_video['index'] += 1
        print(current_video['title'], end='')

        extension = video.streams.get_highest_resolution().mime_type.split('/')[-1]
        print(', {} MB\n{} <'.format(
            (current_video['length'] / 1024 / 1024) * 100 // 1 / 100,
            current_video['index']),
            end=''
        )
        current_video['downloaded'] = False
        if directory:
            video.streams.get_highest_resolution().download(
                directory,
                '{}-{}.{}'.format(url_data['index'], current_video['title'], extension)
            )
        else:
            video.streams.get_highest_resolution().download()
        while not current_video['downloaded']:
            sleep(.5)
            pass
        return True
    except Exception as e:
        print(e)
        return False

def create_directory(directory: str):
    try:
        os.mkdir(directory)
        return True
    except:
        return False

def get_URL_type(url: str):
    if url.startswith('https://www.youtube.com/watch?'):
        url_parts = url.split('?')
        url_type = INDIVIDUAL_VIDEO
        if len(url_parts) > 1:
            query = url_parts[1]
            params = query.split('&')
            for param in params:
                if param.startswith('list='):
                    url_type = PLAY_LIST
        return url_type
    return INVALID_URL

if __name__ == '__main__':
    url = input('Enter playlist link : ')
    url_type = get_URL_type(url)

    if url_type != INVALID_URL:
        if url_type == PLAY_LIST:
            playlist = get_playlist(url)
            directory = remove_special_characters(playlist.title)
            create_directory(directory)
            
            if playlist:
                index = 0
                urls = []
                for url in playlist.video_urls:
                    urls.append({
                        'url': url,
                        'index': 'V-' + str(index).zfill(4),
                        'attempts': 3
                    })
                    index += 1
                while urls:
                    url = urls.pop(0)
                    if not download(url):
                        url['attempts'] -= 1
                        if url['attempts'] > 0:
                            urls.append(url)
                        print('failed to download {}'.format(current_video['title']))
            else:
                print('unable to get playlist')
        else:
            if not download({'url': url}):
                print('unable to download')
    else:
        print('invalid URL')