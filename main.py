import sys
import xbmc
import routing
import SimpleDownloader
import requests
import json

from xbmcgui import ListItem, Dialog
from xbmcplugin import setContent, addDirectoryItem, endOfDirectory, setResolvedUrl
from urllib import quote, unquote

plugin = routing.Plugin()
downloader = SimpleDownloader.SimpleDownloader()
downloader.dbg = True
setContent(plugin.handle, 'videos')

@plugin.route('/')
def series_route():
    search_query = Dialog().input('Search for Animation by Name')
    response = requests.get('https://kisscartoonapi.herokuapp.com/api/search?s={}'.format(search_query), timeout=15)
    series = json.loads(response.text)
    for siri in series:
        addDirectoryItem(plugin.handle, plugin.url_for(episodes_route, quote(siri['url'])), ListItem(siri['title']), True)
    endOfDirectory(plugin.handle)

@plugin.route('/series/<path:series_url>')
def episodes_route(series_url):
    response = requests.get('https://kisscartoonapi.herokuapp.com/api/episodes?url={}'.format(unquote(series_url)), timeout=15)
    episodes = json.loads(response.text)
    for episode in episodes:
        list_item = ListItem(episode['title'])
        list_item.setArt(
                {
                    'thumb': episode['img'],
                    'icon': episode['img'],
                    'fanart': episode['img']
                }
            )
        list_item.setInfo(
            'video',
            {
                'title': episode['title'],
                'genre': episode['title'],
                'mediatype': 'video'
            }
        )
        list_item.setProperty('IsPlayable', 'true')
        addDirectoryItem(plugin.handle, plugin.url_for(play_route, quote(episode['url'])), list_item, False)
    endOfDirectory(plugin.handle)

@plugin.route('/episode/<path:episode_url>')
def play_route(episode_url):
    m3u8Link = requests.get('https://kisscartoonapi.herokuapp.com/api/play?url={}'.format(unquote(episode_url)), timeout=15)
    downloader.download('kisscartoon.m3u8', { "url": m3u8Link.text, "download_path": "/tmp" })
    setResolvedUrl(plugin.handle, True, listitem=ListItem(path="/tmp/kisscartoon.m3u8"))

if __name__ == '__main__':
    plugin.run()