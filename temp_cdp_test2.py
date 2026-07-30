import asyncio, json, websockets, sys

TARGET_ID = "C5D87CC112B37217A6863D9467C64112"
WS_URL = "ws://127.0.0.1:18800/devtools/page/" + TARGET_ID

async def main():
    print(f"Connecting to {WS_URL}...", flush=True)
    try:
        async with websockets.connect(WS_URL, ping_interval=None, max_size=10000000) as ws:
            print("Connected!", flush=True)
            
            # Enable Runtime
            await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
            resp = await ws.recv()
            print("Runtime.enable:", resp[:100], flush=True)
            
            # Evaluate
            js = "document.title"
            await ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate", "params": {
                "expression": js,
                "returnByValue": True
            }}))
            resp = await ws.recv()
            data = json.loads(resp)
            print("Title result:", json.dumps(data, indent=2, ensure_ascii=False)[:300], flush=True)
            
    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()

asyncio.run(main())
