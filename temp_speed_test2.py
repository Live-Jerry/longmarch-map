import asyncio, json, websockets, sys
sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)

TID = 'B53F6AB13D00D81D126D0273957AE88D'
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

        # Start walk
        await ev(ws, "document.getElementById('autowalk-label').click()", m); m += 1
        await asyncio.sleep(0.5)
        await ev(ws, "document.querySelectorAll('.speed-btn')[1].click()", m); m += 1
        await asyncio.sleep(0.3)
        await ev(ws, "document.getElementById('btn-autowalk-start').click()", m); m += 1
        await asyncio.sleep(2)

        # Test 1: Change speed during active walk -> BLOCKED
        r = await ev(ws, "(function(){var b=document.querySelectorAll('.speed-btn');return{'beforeSpeed':autowalkSpeed,'s1active':b[1].classList.contains('active')}})()", m); m += 1
        print('=== Active walk: try change speed ===')
        print('Before:', r)

        await ev(ws, "document.querySelectorAll('.speed-btn')[0].click()", m); m += 1
        await asyncio.sleep(0.3)
        r = await ev(ws, "(function(){var b=document.querySelectorAll('.speed-btn');return{'speed':autowalkSpeed,'s0active':b[0].classList.contains('active'),'s1active':b[1].classList.contains('active')}})()", m); m += 1
        print('After trying speed change:', r, '>>> BLOCKED' if r and r.get('s1active') else '>>> CHANGED!')

        # Test 2: Pause then change speed -> ALLOWED
        print('\n=== Pause then change speed ===')
        await ev(ws, "document.getElementById('btn-play-pause').click()", m); m += 1
        await asyncio.sleep(0.5)
        r = await ev(ws, "autowalkState.paused", m); m += 1
        print('Paused:', r)

        # Now change speed
        await ev(ws, "document.querySelectorAll('.speed-btn')[2].click()", m); m += 1
        await asyncio.sleep(0.3)
        r = await ev(ws, "(function(){var b=document.querySelectorAll('.speed-btn');return{'speed':autowalkSpeed,'s2active':b[2].classList.contains('active')}})()", m); m += 1
        print('After pause+speed change:', r, '>>> ALLOWED' if r and r.get('s2active') else '>>> BLOCKED!')

asyncio.run(main())
