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

        # Test: try to change speed during walk
        r = await ev(ws, "(function(){var b=document.querySelectorAll('.speed-btn');var s=document.getElementById('autowalkSpeed')||{};return {'before':parseInt(b[0].dataset.speed)+':'+b[0].classList.contains('active'),'mid':parseInt(b[1].dataset.speed)+':'+b[1].classList.contains('active')}})()", m); m += 1
        print('Before speed change:', r)

        # Try clicking a different speed
        await ev(ws, "document.querySelectorAll('.speed-btn')[0].click()", m); m += 1
        await asyncio.sleep(0.3)
        r = await ev(ws, "(function(){var b=document.querySelectorAll('.speed-btn');return {'s0':parseInt(b[0].dataset.speed)+':'+b[0].classList.contains('active'),'s1':parseInt(b[1].dataset.speed)+':'+b[1].classList.contains('active'),'s2':parseInt(b[2].dataset.speed)+':'+b[2].classList.contains('active')}})()", m); m += 1
        print('After trying to change speed:', r)
        
        # Now pause
        await ev(ws, "(function(){var pb=document.querySelector('#play-controls .pause-btn')||document.querySelector('#btn-pause');if(pb)pb.click()})()", m); m += 1
        await asyncio.sleep(0.5)
        r = await ev(ws, "autowalkState.paused", m); m += 1
        print('Paused:', r)

        # Now change speed (should work)
        await ev(ws, "document.querySelectorAll('.speed-btn')[2].click()", m); m += 1
        await asyncio.sleep(0.3)
        r = await ev(ws, "(function(){var b=document.querySelectorAll('.speed-btn');return {'s0':parseInt(b[0].dataset.speed)+':'+b[0].classList.contains('active'),'s1':parseInt(b[1].dataset.speed)+':'+b[1].classList.contains('active'),'s2':parseInt(b[2].dataset.speed)+':'+b[2].classList.contains('active'),'speed':autowalkSpeed}})()", m); m += 1
        print('After pause + speed change:', r)

asyncio.run(main())
