import asyncio, json, websockets, sys
sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)

TID = 'DCAFD9123E3903432E02F0144F1728DD'
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
    if r:
        exc = r.get('result', {}).get('exceptionDetails')
        if exc: print('JS ERROR:', exc)
        return r.get('result', {}).get('result', {}).get('value')
    return None

async def main():
    async with websockets.connect(WS, ping_interval=None, max_size=5000000) as ws:
        await ws.send(json.dumps({'id': 1, 'method': 'Runtime.enable'}))
        for _ in range(5):
            try: await asyncio.wait_for(ws.recv(), timeout=0.5)
            except: pass
        m = 10

        # Click 中速
        print("=== Testing on DEV server ===")
        await ev(ws, "document.querySelectorAll('.speed-btn')[1].click()", m); m += 1
        await asyncio.sleep(0.3)

        # Click 开始
        await ev(ws, "document.getElementById('btn-autowalk-start').click()", m); m += 1
        await asyncio.sleep(2)

        r = await ev(ws, "(function(){var b=document.getElementById('btn-autowalk-start');return{'btnDisabled':b.disabled,'active':autowalkState.active,'paused':autowalkState.paused,'hasMarker':autowalkState.marker!==null}})()", m); m += 1
        print('After start:', r)

        # Try changing speed during walk
        await ev(ws, "document.querySelectorAll('.speed-btn')[0].click()", m); m += 1
        await asyncio.sleep(0.3)
        r = await ev(ws, "(function(){var b=document.querySelectorAll('.speed-btn');return{'speed':autowalkSpeed,'s0active':b[0].classList.contains('active'),'s1active':b[1].classList.contains('active'),'btnDisabled':document.getElementById('btn-autowalk-start').disabled}})()", m); m += 1
        print('Speed change during walk:', r)

        # Pause then change speed
        await ev(ws, "document.getElementById('btn-play-pause').click()", m); m += 1
        await asyncio.sleep(0.5)
        r = await ev(ws, "autowalkState.paused", m); m += 1
        print('Paused:', r)

        await ev(ws, "document.querySelectorAll('.speed-btn')[2].click()", m); m += 1
        await asyncio.sleep(0.3)
        r = await ev(ws, "(function(){var b=document.querySelectorAll('.speed-btn');return{'speed':autowalkSpeed,'s2active':b[2].classList.contains('active'),'btnDisabled':document.getElementById('btn-autowalk-start').disabled}})()", m); m += 1
        print('Speed change after pause:', r)

        print("\n>>> DEV SERVER TEST PASSED <<<" if r and r.get('s2active') else "\n>>> TEST FAILED <<<")

asyncio.run(main())
