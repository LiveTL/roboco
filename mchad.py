from urllib.parse import urlparse
import sseclient
import json
import requests

MCHAD = 'https://repo.mchatx.org'

def video_id(value: str):
    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = urlparse(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None

def getRoomList():
    return requests.get(f'{MCHAD}/Room/').json()

def getRoom(id, idonly = True):
    if idonly:
        id = 'YT_' + id
    try:
        return requests.get(f'{MCHAD}/Room/?link={id}').json()[0]
    except IndexError:
        return None

def getRoomByName(name):
    return requests.get(f'{MCHAD}/Room/?name={name}').json()[0]

def getListenerByName(name):
    return sseclient.SSEClient(f'{MCHAD}/Listener/?room={name}')

def getListnerByID(id):
    return getListenerByName(getRoom(id)['Nick'])

def roomGeneratorbyID(id):
    for x in getListnerByID(id):
        data = json.loads(x.data)
        if data == {}:
            continue
        elif data['flag'] == 'insert':
            yield data['content']['Stext']

if __name__ == "__main__":
    print('mchad test')
    print(video_id('https://youtu.be/dQw4w9WgXcQ'))
    print(getRoomList())
    print(getRoom('0BBfB9N_VFs'))
    print(getRoomByName('Translator Vee'))