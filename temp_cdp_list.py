import requests, json

r = requests.get('http://127.0.0.1:18800/json', timeout=5)
tabs = r.json()
for tab in tabs:
    title = tab.get('title', '')
    url = tab.get('url', '')
    if '5000' in url or 'longmarch' in title.lower():
        print('ID:', tab['id'])
        print('Title:', title)
        print('URL:', url)
        print('Type:', tab.get('type', ''))
        ws = tab.get('webSocketDebuggerUrl', tab.get('wsUrl', ''))
        print('WS:', ws)
        print()
