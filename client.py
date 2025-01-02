import logging
import logging
import sys

import grpc

import epidemic_replication_pb2
import epidemic_replication_pb2_grpc
from addrs import ADDRS
from utils import logging_level

logging.basicConfig(level=logging_level, format="%(message)s")
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Connect to the server
    try:
        channel = grpc.insecure_channel(ADDRS["A1"][1])
        stub = epidemic_replication_pb2_grpc.NodeServiceStub(channel)
        grpc.channel_ready_future(channel).result(timeout=2)
    except grpc.FutureTimeoutError:
        logger.error("Failed to connect to the server.")
        sys.exit(1)

    file_path = "data.txt"

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            logger.info(f"Sending transaction: {line.strip()}")
            request = epidemic_replication_pb2.TransactionRequest(transaction=line.strip())
            response = stub.processTransaction(request)
            if response.status < 0:
                logger.warning(f"Failed to send transaction: {response.answer}")
            else:
                logger.info(f"Transaction sent successfully: {response.answer}")
