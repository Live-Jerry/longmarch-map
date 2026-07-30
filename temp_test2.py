import asyncio, json, websockets

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
    resp = await recv_until(ws, cmd_id)
    if resp:
        return resp.get("result", {}).get("result", {}).get("value")
    return None

async def main():
    async with websockets.connect(WS_URL, ping_interval=None, max_size=5000000) as ws:
        # Enable Runtime
        await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        for _ in range(5):
            try:
                await asyncio.wait_for(ws.recv(), timeout=1)
            except:
                pass

        mid = 10

        # Find the walk button
        print("=== 查找漫游按钮 ===")
        r = await eval_js(ws, """
        (function() {
            // Try various selectors
            var candidates = [];
            
            var labels = document.querySelectorAll('[id*=\"walk\"], [id*=\"auto\"], [id*=\"route\"], [class*=\"walk\"], [class*=\"auto\"]');
            labels.forEach(function(el) {
                candidates.push({
                    id: el.id || '',
                    tag: el.tagName,
                    text: (el.textContent || '').trim().slice(0, 20),
                    className: el.className || '',
                    onclick: (el.onclick ? 'yes' : (el.getAttribute('onclick') || '')),
                });
            });
            
            // Also check sidebar menu items
            var menu = document.querySelectorAll('.menu-item, [class*=\"menu\"] li, [class*=\"menu\"] div, .sidebar-item');
            menu.forEach(function(el) {
                candidates.push({
                    id: el.id || '',
                    tag: el.tagName,
                    text: (el.textContent || '').trim().slice(0, 20),
                    className: el.className || '',
                });
            });
            
            return candidates;
        })()
        """, mid); mid += 1
        
        if r:
            for item in r[:10]:
                print(f"  id={item.get('id','')} tag={item.get('tag','')} text={item.get('text','')} cls={item.get('className','')} oc={item.get('onclick','')}")

        # Also show the top elements around the info panel
        print("\n=== 一级查找 ===")
        r2 = await eval_js(ws, """
        (function() {
            var all = [];
            document.querySelectorAll('[id]').forEach(function(el) {
                if (el.id && el.id !== '') {
                    all.push({id: el.id, tag: el.tagName, text: (el.textContent||'').trim().slice(0,30)});
                }
            });
            return all;
        })()
        """, mid); mid += 1
        if r2:
            # Only show relevant ids
            relevant = ['walk', 'auto', 'route', 'speed', 'menu', 'sidebar', 'info', 'control', 'navi']
            for item in r2:
                id_lower = item.get('id','').lower()
                if any(k in id_lower for k in relevant):
                    print(f"  id={item.get('id','')} tag={item.get('tag','')} text={item.get('text','')}")

asyncio.run(main())
