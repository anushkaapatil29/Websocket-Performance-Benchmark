import asyncio
import json
import logging
import argparse
from datetime import datetime
import websockets
from websockets.exceptions import InvalidHandshake, ConnectionClosedOK

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebSocketServer:
    """WebSocket server that handles incoming messages and responds with status and payload."""

    def __init__(self, host: str = "localhost", port: int = 8765) -> None:
        self.host = host
        self.port = port
        # self.active_connections = set()

    async def handler(self, websocket: websockets.WebSocketServerProtocol) -> None:
        """Handle incoming WebSocket connections and messages."""
        addr = websocket.remote_address
        logger.info(f"New connection established: {addr}")

        try:
            async for message in websocket:
                # Prepare a structured JSON response
                payload = {
                    "status": "success",
                    "data": message,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                }
                await websocket.send(json.dumps(payload))
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed by client: {addr}")
        except Exception as e:
            logger.error(f"Error handling client {addr}: {e}")

    async def start(self):
        """Starts the WebSocket server."""
        async with websockets.serve(self.handler, self.host, self.port):
            logger.info(f"🚀 Server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebSocket Performance Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=8765, help="Port number")
    args = parser.parse_args()

    server = WebSocketServer(args.host, args.port)
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("Server stopped by administrator.")