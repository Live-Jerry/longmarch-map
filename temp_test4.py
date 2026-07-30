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

        # First click 漫游 if not already
        await eval_js(ws, "document.getElementById('autowalk-label').click()", mid); mid += 1
        await asyncio.sleep(0.3)

        # Click 开始 button
        print("=== Step 3: Click 开始 ===")
        r = await eval_js(ws, """
        (function() {
            var btn = document.getElementById('btn-autowalk-start');
            btn.click();
            return 'clicked: disabled=' + btn.disabled;
        })()
        """, mid); mid += 1
        print(f"  {r}")
        await asyncio.sleep(1)

        # Check state after clicking start
        print("\n=== Step 4: State after start ===")
        r = await eval_js(ws, """
        (function() {
            var r = {};
            var btn = document.getElementById('btn-autowalk-start');
            r.btnDisabled = btn ? btn.disabled : 'no-btn';
            
            var ss = document.getElementById('speed-selector');
            r.speedSelVisible = ss ? ss.classList.contains('visible') : 'no-ss';
            
            var wl = document.getElementById('autowalk-label');
            r.walkLabel = wl ? wl.textContent.trim() : 'no-label';
            
            r.markerCount = typeof map !== 'undefined' && map.instance ? 
                Object.keys(map.instance._layers).length + ' total layers' : 'no map';
            
            // Check for autowalk marker specifically
            var am = document.querySelector('.autowalk-marker') ? 'exists' : 'not found';
            r.autowalkMarker = am;
            
            return r;
        })()
        """, mid); mid += 1
        if r:
            for k, v in r.items():
                print(f"  {k}: {v}")

        # Try clicking 开始 again (this should NOT create a second marker)
        print("\n=== Step 5: Try clicking 开始 again ===")
        r = await eval_js(ws, """
        (function() {
            var btn = document.getElementById('btn-autowalk-start');
            if (!btn.disabled) {
                btn.click();
                return 'clicked again';
            }
            return 'button disabled, cannot click';
        })()
        """, mid); mid += 1
        print(f"  {r}")

        # Count autowalk markers (divIcon markers)
        print("\n=== Step 6: Count markers ===")
        r = await eval_js(ws, """
        (function() {
            var count = 0;
            if (typeof map !== 'undefined' && map.instance) {
                var layers = map.instance._layers;
                for (var key in layers) {
                    if (layers[key] instanceof L.Marker && layers[key].options && 
                        layers[key].options.icon && layers[key].options.icon.options &&
                        layers[key].options.icon.options.html &&
                        layers[key].options.icon.options.html.indexOf('autowalk') >= 0) {
                        count++;
                    }
                }
            }
            return count;
        })()
        """, mid); mid += 1
        print(f"  Autowalk markers on map: {r}")

asyncio.run(main())
