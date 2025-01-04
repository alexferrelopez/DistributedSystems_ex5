import asyncio
import logging
import sys

import grpc
from websockets.asyncio.server import serve

from services.addrs import ADDRS
from services.proto import epidemic_replication_pb2
from services.proto import epidemic_replication_pb2_grpc
from services.utils import logging_level

logging.basicConfig(level=logging_level, format="%(message)s")
logger = logging.getLogger(__name__)

connected_clients = set()


def get_stubs():
    stubs = {}
    for key, layer_socket_pair in ADDRS.items():
        try:
            channel = grpc.insecure_channel(layer_socket_pair[1])
            stub = epidemic_replication_pb2_grpc.NodeServiceStub(channel)
            grpc.channel_ready_future(channel).result(timeout=2)
            stubs[key] = stub
        except grpc.FutureTimeoutError:
            logger.error("Failed to connect to the server.")
            sys.exit(1)
    return stubs


async def send_node_data(websocket):
    try:
        while True:
            for stub in stubs.values():
                response = stub.nodeGetData(epidemic_replication_pb2.Empty())
                await websocket.send(f"{response.sender} :{response.data}")
            await asyncio.sleep(0.2)
    except Exception as e:
        logger.error(e)


async def main():
    async with serve(send_node_data, "localhost", 5678):
        await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":
    stubs = get_stubs()
    asyncio.run(main())
