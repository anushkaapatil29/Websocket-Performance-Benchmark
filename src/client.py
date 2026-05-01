import asyncio
import websockets
import json
import argparse
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def interactive_client(uri: str):
    """Connects to server and allows real-time manual messaging."""
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"✅ Connected to {uri}")
            print("Type a message and press Enter (or 'exit' to quit):")

            while True:
                # Use executor to prevent blocking the async loop during input
                message = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                message = message.strip()

                if message.lower() == 'exit':
                    break
                if not message:
                    continue

                await websocket.send(message)
                response = await websocket.recv()
                data = json.loads(response)
                
                print(f"📩 [Server {data['timestamp']}]: {data['data']}")

    except Exception as e:
        logger.error(f"❌ Connection error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebSocket Interactive Client")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    try:
        asyncio.run(interactive_client(f"ws://{args.host}:{args.port}"))
    except KeyboardInterrupt:
        pass