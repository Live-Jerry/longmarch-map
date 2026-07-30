import asyncio, json, websockets, sys
sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)

TID = 'FB7763C2F733EEEC6FD1B0BB4733B2DD'
WS = 'ws://127.0.0.1:18800/devtools/page/' + TID

async def rcv(ws, sid, timeout=10):
    start = asyncio.get_event_loop().time()
    while True:
        rem = timeout - (asyncio.get_event_loop().time() - start)
        if rem <= 0: return None
        try:
            r = json.loads(await asyncio.wait_for(ws.recv(), timeout=rem))
            if r.get('id') == sid: return r
        except: pass

async def ev(ws, js, sid):
    await ws.send(json.dumps({'id': sid, 'method': 'Runtime.evaluate', 'params': {
        'expression': js, 'returnByValue': True, 'awaitPromise': True
    }}))
    r = await rcv(ws, sid, 15)
    if r: return r.get('result', {}).get('result', {}).get('value')
    return None

async def main():
    async with websockets.connect(WS, ping_interval=None, max_size=5000000) as ws:
        await ws.send(json.dumps({'id': 1, 'method': 'Runtime.enable'}))
        for _ in range(5):
            try: await asyncio.wait_for(ws.recv(), timeout=0.5)
            except: pass
        m = 10

        # Click walk
        await ev(ws, "document.getElementById('autowalk-label').click()", m); m += 1
        await asyncio.sleep(0.5)
        # Select speed
        await ev(ws, "document.querySelectorAll('.speed-btn')[1].click()", m); m += 1
        await asyncio.sleep(0.3)
        # Click start
        await ev(ws, "document.getElementById('btn-autowalk-start').click()", m); m += 1
        await asyncio.sleep(2)

        r = await ev(ws, "(function(){var b=document.getElementById('btn-autowalk-start');return{b:b.disabled,a:autowalkState.active,m:autowalkState.marker!==null}})()", m); m += 1
        print('=== After start ===')
        print('  btnDisabled:', r.get('b'), 'active:', r.get('a'), 'marker:', r.get('m'))

        # Re-select speed (should NOT re-enable)
        await ev(ws, "document.querySelectorAll('.speed-btn')[2].click()", m); m += 1
        await asyncio.sleep(0.3)
        r = await ev(ws, "(function(){var b=document.getElementById('btn-autowalk-start');return{a:autowalkState.active,b:b.disabled}})()", m); m += 1
        print('\n=== After speed re-select ===')
        print('  btnDisabled:', r.get('b'), 'active:', r.get('a'))

        # Force startAutowalk() to test cleanup
        await ev(ws, "startAutowalk()", m); m += 1
        await asyncio.sleep(2)
        r = await ev(ws, "(function(){var c=0;for(var k in map.instance._layers){var l=map.instance._layers[k];if(l instanceof L.Marker&&l.options&&l.options.icon&&l.options.icon.options&&l.options.icon.options.html&&l.options.icon.options.html.indexOf('autowalk')>=0)c++}return{c:c,b:document.getElementById('btn-autowalk-start').disabled}})()", m); m += 1
        print('\n=== After force restart ===')
        if r:
            print('  autowalkMarkers:', r.get('c'), 'btnDisabled:', r.get('b'))
            print('  RESULT: PASS' if r.get('c', 99) <= 1 else '  RESULT: FAIL')

asyncio.run(main())
