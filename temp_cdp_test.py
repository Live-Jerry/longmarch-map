import asyncio, json, websockets

TARGET_ID = "C5D87CC112B37217A6863D9467C64112"
WS_URL = "ws://127.0.0.1:18800/devtools/page/" + TARGET_ID

async def cdp_send(ws, cmd_id, method, params=None):
    msg = {"id": cmd_id, "method": method}
    if params:
        msg["params"] = params
    await ws.send(json.dumps(msg))
    resp = await ws.recv()
    return json.loads(resp)

async def main():
    async with websockets.connect(WS_URL, ping_interval=None) as ws:
        idx = 0
        
        # Enable Runtime and DOM
        await cdp_send(ws, idx, "Runtime.enable"); idx += 1
        await cdp_send(ws, idx, "DOM.enable"); idx += 1

        # Evaluate JS on page
        js_code = """
        (function() {
            var result = {};
            
            // Check controls.js is loaded
            result.controlsLoaded = typeof startAutowalk === 'function';
            result.controlsExported = typeof window.startAutowalk === 'function';
            
            // Check autowalk button
            var btn = document.getElementById('btn-autowalk-start');
            result.startBtnExists = !!btn;
            result.startBtnDisabled = btn ? btn.disabled : null;
            result.startBtnText = btn ? btn.textContent : null;
            
            // Check speed selector
            var ss = document.getElementById('speed-selector');
            result.speedSelectorExists = !!ss;
            result.speedSelectorVisible = ss ? ss.classList.contains('visible') : null;
            
            // Check map exists
            result.mapExists = typeof map !== 'undefined' && map !== null;
            
            return result;
        })()
        """
        
        resp = await cdp_send(ws, idx, "Runtime.evaluate", {
            "expression": js_code,
            "returnByValue": True
        }); idx += 1
        
        result = resp.get("result", {}).get("result", {}).get("value", {})
        for k, v in result.items():
            print(f"{k}: {v}")

asyncio.run(main())
