with open(r'D:\长征文化\_idx_check.html', encoding='utf-8') as f:
    html = f.read()

ids_js = ['btn-tts', 'btn-autowalk', 'btn-play-pause', 'btn-skip', 'btn-restart', 
          'btn-army', 'btn-spark-main', 'btn-exit-autowalk', 'btn-message',
          'btn-basemap', 'btn-close-panel', 'btn-read', 'btn-spark',
          'speed-selector', 'play-controls', 'btn-autowalk-start']

for idv in sorted(set(ids_js)):
    pat = f'id="{idv}"'
    if pat in html:
        print(f'  OK    {idv}')
    else:
        # also check with single quotes
        pat2 = f"id='{idv}'"
        if pat2 in html:
            print(f'  OK(sq) {idv}')
        else:
            print(f'  MISS  {idv}')
