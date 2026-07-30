import asyncio, json, websockets

TARGET_ID = "C5D87CC112B37217A6863D9467C64112"
WS_URL = "ws://127.0.0.1:18800/devtools/page/" + TARGET_ID

async def recv_until(ws, target_id, timeout=10):
    """Receive messages until we get a response with the target id."""
    start = asyncio.get_event_loop().time()
    while True:
        remaining = timeout - (asyncio.get_event_loop().time() - start)
        if remaining <= 0:
            return None
        try:
            resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=remaining))
            if resp.get("id") == target_id:
                return resp
        except asyncio.TimeoutError:
            return None
        except Exception:
            pass

async def eval_js(ws, js, cmd_id):
    """Evaluate JavaScript on the page."""
    await ws.send(json.dumps({"id": cmd_id, "method": "Runtime.evaluate", "params": {
        "expression": js,
        "returnByValue": True
    }}))
    resp = await recv_until(ws, cmd_id)
    if resp:
        return resp.get("result", {}).get("result", {}).get("value")
    return None

async def click_element(ws, selector, cmd_id):
    """Click an element by finding it and clicking via JS."""
    js = f"""
    (function() {{
        var el = document.querySelector({json.dumps(selector)});
        if (!el) return {{ok: false, err: 'not found'}};
        el.click();
        return {{ok: true, text: el.textContent.trim()}};
    }})()
    """
    return await eval_js(ws, js, cmd_id)

async def main():
    async with websockets.connect(WS_URL, ping_interval=None, max_size=5000000) as ws:
        # Enable Runtime and consume init
        await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        for _ in range(5):
            try:
                await asyncio.wait_for(ws.recv(), timeout=1)
            except:
                pass

        mid = 10  # message id counter

        # Step 1: Check initial state
        print("=== 初始状态 ===")
        r = await eval_js(ws, """
        (function() {
            var r = {};
            r.pageTitle = document.title;
            
            // Speed selector
            var ss = document.getElementById('speed-selector');
            r.speedSelExists = !!ss;
            r.speedSelVisible = ss ? ss.classList.contains('visible') : false;
            
            // Autowalk button
            var btn = document.getElementById('btn-autowalk-start');
            r.btnExists = !!btn;
            r.btnDisabled = btn ? btn.disabled : null;
            r.btnText = btn ? btn.textContent.trim() : '';
            
            // Map marker count
            r.markerCount = map && map.instance && map.instance._layers ? 
                Object.values(map.instance._layers).filter(function(l) { 
                    return l instanceof L.Marker; 
                }).length : -1;
            
            // Walk button
            r.hasWalkBtn = !!document.querySelector('[onclick*=\"showSpeed\"]') || 
                           !!document.getElementById('autowalk-label');
            var wl = document.getElementById('autowalk-label');
            r.walkLabel = wl ? wl.textContent.trim() : '';
            
            return r;
        })()
        """, mid); mid += 1
        if r:
            for k, v in r.items():
                print(f"  {k}: {v}")

asyncio.run(main())
