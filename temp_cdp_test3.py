import asyncio, json, websockets

TARGET_ID = "C5D87CC112B37217A6863D9467C64112"
WS_URL = "ws://127.0.0.1:18800/devtools/page/" + TARGET_ID

async def main():
    async with websockets.connect(WS_URL, ping_interval=None, max_size=5000000) as ws:
        # Send Runtime.enable first
        await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        # Consume init messages
        for _ in range(3):
            try:
                await asyncio.wait_for(ws.recv(), timeout=1)
            except:
                pass

        # Now evaluate
        js = """
        (function() {
            var r = {};
            r.title = document.title;
            r.hasMap = typeof map !== 'undefined' && map !== null;
            r.btnStart = document.getElementById('btn-autowalk-start') ? 
                document.getElementById('btn-autowalk-start').disabled : 'no-btn';
            r.speedSel = document.getElementById('speed-selector') ? 
                document.getElementById('speed-selector').classList.contains('visible') : 'no-ss';
            r.hasStartFn = typeof startAutowalk === 'function';
            return r;
        })()
        """
        await ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate", "params": {
            "expression": js,
            "returnByValue": True
        }}))
        
        # Collect all responses until we get id=2
        for _ in range(10):
            resp = json.loads(await ws.recv())
            if resp.get("id") == 2:
                result = resp.get("result", {}).get("result", {}).get("value", {})
                for k, v in result.items():
                    print(f"  {k}: {v}")
                break

asyncio.run(main())
