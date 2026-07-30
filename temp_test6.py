import asyncio, json, websockets, sys
sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)

TARGET_ID = "EAD00A39ED254830420A7ED37C904B56"
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
        "awaitPromise": True,
    }}))
    resp = await recv_until(ws, cmd_id, timeout=15)
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

        # Full test: start, stop, restart
        print("=== Round 1: Start autowalk ===")
        await eval_js(ws, "document.getElementById('autowalk-label').click()", mid); mid += 1
        await asyncio.sleep(0.3)
        await eval_js(ws, "document.querySelector('.speed-btn').click()", mid); mid += 1
        await asyncio.sleep(0.2)
        await eval_js(ws, "document.getElementById('btn-autowalk-start').click()", mid); mid += 1
        await asyncio.sleep(2)

        # Check markers after first start
        r = await eval_js(ws, """
        (function() {
            var r = {};
            r.active = autowalkState.active;
            r.hasMarker = autowalkState.marker !== null;
            // Count all autowalk divIcon markers
            var cnt = 0;
            for (var k in map.instance._layers) {
                var ly = map.instance._layers[k];
                if (ly instanceof L.Marker && ly.options && ly.options.icon) {
                    cnt++;
                }
            }
            r.allMarkers = cnt;
            return r;
        })()
        """, mid); mid += 1
        print(f"  active={r['active']}, hasMarker={r['hasMarker']}, allMarkers={r['allMarkers']}")

        # Force-click start again via JS (simulate bypassing disabled button)
        print("\n=== Round 2: Force call startAutowalk() again ===")
        r = await eval_js(ws, """
        (function() {
            // Simulate re-clicking by directly calling startAutowalk
            var preCount = 0;
            for (var k in map.instance._layers) {
                var ly = map.instance._layers[k];
                if (ly instanceof L.Marker && ly.options && ly.options.icon) preCount++;
            }
            startAutowalk();
            return 'pre=' + preCount + ' (cleanup should remove old markers)';
        })()
        """, mid); mid += 1
        print(f"  {r}")
        await asyncio.sleep(3)

        # Check for duplicate markers
        r = await eval_js(ws, """
        (function() {
            // Count only autowalk markers (divIcon with autowalk class)
            var cnt = 0;
            for (var k in map.instance._layers) {
                var ly = map.instance._layers[k];
                if (ly instanceof L.Marker && ly.options && ly.options.icon && 
                    ly.options.icon.options && ly.options.icon.options.html &&
                    ly.options.icon.options.html.indexOf('autowalk') >= 0) {
                    cnt++;
                }
            }
            return {autowalkMarkers: cnt, hasMarker: autowalkState.marker !== null, active: autowalkState.active};
        })()
        """, mid); mid += 1
        if r:
            print(f"  autowalkMarkers={r['autowalkMarkers']}, hasMarker={r['hasMarker']}, active={r['active']}")

asyncio.run(main())
