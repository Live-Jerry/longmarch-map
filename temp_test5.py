import asyncio, json, websockets, sys
sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)

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
        "awaitPromise": True,   # Wait for async
    }}))
    resp = await recv_until(ws, cmd_id, timeout=15)
    if resp:
        exc = resp.get("result", {}).get("exceptionDetails")
        if exc:
            print(f"  JS ERROR: {exc}")
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

        # Click 漫游
        print("=== Step 1: Click 漫游 ===")
        r = await eval_js(ws, "document.getElementById('autowalk-label').click(); 'clicked'", mid); mid += 1
        print(f"  {r}")
        await asyncio.sleep(0.5)

        print("=== Step 2: Click 中速 2s ===")
        r = await eval_js(ws, """
        (function() {
            var btns = document.querySelectorAll('.speed-btn');
            for (var i = 0; i < btns.length; i++) {
                if (btns[i].textContent.indexOf('中速') >= 0) {
                    btns[i].click();
                    return 'clicked: ' + btns[i].textContent.trim();
                }
            }
            return 'no speed button found';
        })()
        """, mid); mid += 1
        print(f"  {r}")
        await asyncio.sleep(0.3)

        print("=== Step 3: Click 开始 ===")
        r = await eval_js(ws, """
        (function() {
            var btn = document.getElementById('btn-autowalk-start');
            if (btn.disabled) return 'button disabled already';
            btn.click();
            return 'clicked, now disabled=' + btn.disabled;
        })()
        """, mid); mid += 1
        print(f"  {r}")
        await asyncio.sleep(2)  # Wait for async autowalk to start

        print("=== Step 4: Post-start state ===")
        r = await eval_js(ws, """
        (function() {
            var r = {};
            var btn = document.getElementById('btn-autowalk-start');
            r.btnDisabled = btn ? btn.disabled : false;
            
            var ss = document.getElementById('speed-selector');
            r.speedSelDisplay = ss ? getComputedStyle(ss).display : 'no-ss';
            r.speedSelVisible = ss ? ss.classList.contains('visible') : false;
            
            var wl = document.getElementById('autowalk-label');
            r.walkLabel = wl ? wl.textContent.trim() : '';
            
            // Check autowalkState
            if (typeof autowalkState !== 'undefined' && autowalkState) {
                r.hasMarker = autowalkState.marker !== null && autowalkState.marker !== undefined;
                r.active = autowalkState.active;
                r.walking = true;
            } else {
                r.walking = false;
            }
            
            return r;
        })()
        """, mid); mid += 1
        if r:
            for k, v in r.items():
                print(f"  {k}: {v}")

        print("\n=== Step 5: Try clicking 开始 again ===")
        r = await eval_js(ws, """
        (function() {
            var btn = document.getElementById('btn-autowalk-start');
            if (btn && !btn.disabled) {
                btn.click();
                return 'clicked again';
            }
            return 'button is disabled, blocked';
        })()
        """, mid); mid += 1
        print(f"  {r}")

asyncio.run(main())
