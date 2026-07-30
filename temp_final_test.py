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

        # Step 1: Click autowalk label
        print("=== Step 1: Click 漫游 ===")
        await eval_js(ws, "document.getElementById('autowalk-label').click()", mid); mid += 1
        await asyncio.sleep(0.5)

        # Step 2: Select speed
        print("=== Step 2: Click 中速 ===")
        await eval_js(ws, """
        var btns = document.querySelectorAll('.speed-btn');
        for (var i = 0; i < btns.length; i++) {
            if (btns[i].textContent.indexOf('中速') >= 0) btns[i].click();
        }
        """, mid); mid += 1
        await asyncio.sleep(0.3)

        # Step 3: Click start
        print("=== Step 3: Click 开始 ===")
        await eval_js(ws, "document.getElementById('btn-autowalk-start').click()", mid); mid += 1
        await asyncio.sleep(2)

        # Step 4: Check button state after start
        r = await eval_js(ws, """
        (function() {
            var btn = document.getElementById('btn-autowalk-start');
            return {disabled: btn.disabled, active: autowalkState.active, markerExists: autowalkState.marker !== null};
        })()
        """, mid); mid += 1
        print(f"  After start: btnDisabled={r['disabled']} active={r['active']} marker={r['markerExists']}")

        # Step 5: Click speed selector again (trying to re-enable)
        print("\n=== Step 4: Click 快速 (trying to re-enable button) ===")
        await eval_js(ws, """
        var btns = document.querySelectorAll('.speed-btn');
        for (var i = 0; i < btns.length; i++) {
            if (btns[i].textContent.indexOf('快速') >= 0) btns[i].click();
        }
        """, mid); mid += 1
        await asyncio.sleep(0.3)

        # Step 6: Check button state - should still be disabled!
        r = await eval_js(ws, """
        (function() {
            var btn = document.getElementById('btn-autowalk-start');
            return {disabled: btn.disabled, active: autowalkState.active};
        })()
        """, mid); mid += 1
        print(f"  After speed re-select: btnDisabled={r['disabled']} active={r['active']}")

        # Step 7: Try to force start again via JS (to test cleanup)
        print("\n=== Step 5: Force startAutowalk() again ===")
        await eval_js(ws, "startAutowalk()", mid); mid += 1
        await asyncio.sleep(2)

        # Count autowalk markers
        r = await eval_js(ws, """
        (function() {
            var cnt = 0;
            for (var k in map.instance._layers) {
                var ly = map.instance._layers[k];
                if (ly instanceof L.Marker && ly.options && ly.options.icon && 
                    ly.options.icon.options && ly.options.icon.options.html &&
                    ly.options.icon.options.html.indexOf('autowalk') >= 0) {
                    cnt++;
                }
            }
            return {autowalkMarkers: cnt, active: autowalkState.active, btnDisabled: document.getElementById('btn-autowalk-start').disabled};
        })()
        """, mid); mid += 1
        if r:
            print(f"  autowalkMarkers={r['autowalkMarkers']} active={r['active']} btnDisabled={r['btnDisabled']}")
            if r['autowalkMarkers'] <= 1:
                print("  >>> PASS: No duplicate markers")
            else:
                print("  >>> FAIL: Duplicate markers detected!")

asyncio.run(main())
