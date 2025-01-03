import logging
import sys
from time import sleep

import grpc

import epidemic_replication_pb2
import epidemic_replication_pb2_grpc
from addrs import ADDRS, Layer
from utils import logging_level

logging.basicConfig(level=logging_level, format="%(message)s")
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Connect to the server
    try:
        channel = grpc.insecure_channel(ADDRS["A1"][1])
        core_stub = epidemic_replication_pb2_grpc.NodeServiceStub(channel)
        grpc.channel_ready_future(channel).result(timeout=2)
    except grpc.FutureTimeoutError:
        logger.error("Failed to connect to the server.")
        sys.exit(1)

    try:
        channel = grpc.insecure_channel(ADDRS["B1"][1])
        l1_stub = epidemic_replication_pb2_grpc.NodeServiceStub(channel)
        grpc.channel_ready_future(channel).result(timeout=2)
    except grpc.FutureTimeoutError:
        logger.error("Failed to connect to the server.")
        sys.exit(1)

    try:
        channel = grpc.insecure_channel(ADDRS["C1"][1])
        l2_stub = epidemic_replication_pb2_grpc.NodeServiceStub(channel)
        grpc.channel_ready_future(channel).result(timeout=2)
    except grpc.FutureTimeoutError:
        logger.error("Failed to connect to the server.")
        sys.exit(1)

    file_path = "data.txt"

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            stub = core_stub
            line = line.strip()
            logger.info(f"Sending transaction: {line}")
            begin = line.split(",", 1)[0].strip()
            if begin != "b":
                # Is not read-only transaction
                layer = int(begin[1])

                match layer:
                    case Layer.LAYER_1.value:
                        stub = l1_stub
                    case Layer.LAYER_2.value:
                        stub = l2_stub
                    case Layer.CORE.value:
                        stub = core_stub
                    case _:
                        logger.error(f"Invalid layer in transaction: {line}")

            request = epidemic_replication_pb2.TransactionRequest(transaction=line.strip())
            response = stub.processTransaction(request)

            if response.status < 0:
                logger.warning(f"Failed to send transaction: {response.answer}")
            else:
                logger.info(f"Transaction sent successfully: {response.answer}")
            sleep(0.1)
