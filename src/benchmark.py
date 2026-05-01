import asyncio
import time
import argparse
import logging
import websockets

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class BenchmarkSuite:
    def __init__(self, host, port, clients, messages):
        self.uri = f"ws://{host}:{port}"
        self.num_clients = clients
        self.num_messages = messages
        self.total_responses = 0
        self.counter_lock = asyncio.Lock()  # Ensures thread-safe counting

    async def run_client(self, client_id):
        """Simulates a single load-testing client."""
        try:
            async with websockets.connect(self.uri) as ws:
                for i in range(self.num_messages):
                    await ws.send(f"msg_{i}_from_{client_id}")
                    await ws.recv()
                    async with self.counter_lock:
                        self.total_responses += 1
        except Exception as e:
            logger.error(f"Client {client_id} failed: {e}")

    async def start(self):
        logger.info(f"🔥 Stress Test: {self.num_clients} clients | {self.num_messages} msgs/client")
        start_time = time.perf_counter()

        tasks = [self.run_client(i) for i in range(self.num_clients)]
        await asyncio.gather(*tasks)

        duration = time.perf_counter() - start_time
        throughput = self.total_responses / duration

        print("\n" + "="*30)
        print(f"📊 RESULTS")
        print("="*30)
        print(f"Total Messages: {self.total_responses}")
        print(f"Total Duration: {duration:.2f}s")
        print(f"Throughput:     {throughput:.2f} msgs/sec")
        print("="*30)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebSocket Load Tester")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--clients", type=int, default=50)
    parser.add_argument("--messages", type=int, default=100)
    args = parser.parse_args()

    suite = BenchmarkSuite(args.host, args.port, args.clients, args.messages)
    asyncio.run(suite.start())