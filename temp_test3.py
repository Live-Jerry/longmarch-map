import asyncio, json, websockets, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TARGET_ID = "C5D87CC112B37217A6863D9467C64112"
WS_URL = "ws://127.0.0.1:18800/devtools/page/" + TARGET_ID

async def recv_until(ws, target_id, timeout=10):
    start = asyncio.get_event_loop().time()
    while True:
        remaining = timeout - (asyncio.get_event_loop().time() - start)
        if remaining <= 0:
            return None
        try:
            resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=remaining))
            if resp.get("id") == target_id:
                return resp
        except:
            pass

async def eval_js(ws, js, cmd_id):
    await ws.send(json.dumps({"id": cmd_id, "method": "Runtime.evaluate", "params": {
        "expression": js,
        "returnByValue": True,
        "awaitPromise": False,
    }}))
    resp = await recv_until(ws, cmd_id)
    if resp:
        return resp.get("result", {}).get("result", {}).get("value")
    return None

async def main():
    async with websockets.connect(WS_URL, ping_interval=None, max_size=5000000) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        for _ in range(5):
            try:
                await asyncio.wait_for(ws.recv(), timeout=0.5)
            except:
                pass

        mid = 10

        # Step 1: Click the 漫游 label
        print("=== Step 1: Click 漫游 ===")
        r = await eval_js(ws, """
        (function() {
            var el = document.getElementById('autowalk-label');
            if (!el) return 'no autowalk-label';
            el.click();
            return 'clicked';
        })()
        """, mid); mid += 1
        print(f"  Click result: {r}")
        await asyncio.sleep(0.5)

        # Step 2: Check speed selector appeared
        print("\n=== Step 2: Check speed selector ===")
        r = await eval_js(ws, """
        (function() {
            var r = {};
            var ss = document.getElementById('speed-selector');
            r.selector = ss ? (ss.classList.contains('visible') ? 'visible' : 'hidden') : 'not found';
            
            // Find all speed buttons
            var btns = [];
            document.querySelectorAll('.speed-btn').forEach(function(b) {
                btns.push(b.textContent.trim() + ' (active:' + b.classList.contains('active') + ')');
            });
            r.speedBtns = btns;
            
            // Check start button
            var sb = document.getElementById('btn-autowalk-start');
            r.startBtn = sb ? ('disabled=' + sb.disabled + ' text=' + sb.textContent.trim()) : 'not found';
            
            // Check play controls
            var pc = document.getElementById('play-controls');
            r.playControls = pc ? (pc.classList.contains('visible') ? 'visible' : 'hidden') : 'not found';
            
            return r;
        })()
        """, mid); mid += 1
        if r:
            for k, v in r.items():
                if isinstance(v, list):
                    print(f"  {k}: {', '.join(str(x) for x in v)}")
                else:
                    print(f"  {k}: {v}")

asyncio.run(main())
