import logging
from concurrent import futures
from multiprocessing.context import Process

import grpc

import addrs
import epidemic_replication_pb2_grpc
from core_node import CoreNodeService
from node import NodeService
from utils import logging_level

logging.basicConfig(level=logging_level, format="%(message)s")
logger = logging.getLogger(__name__)


def serve(server_name, layer, socket):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    if layer == addrs.Layer.CORE:
        epidemic_replication_pb2_grpc.add_NodeServiceServicer_to_server(
            CoreNodeService(layer=layer, server_name=server_name), server)
    else:
        epidemic_replication_pb2_grpc.add_NodeServiceServicer_to_server(
            NodeService(layer=layer, server_name=server_name), server)

    server.add_insecure_port(socket)
    logger.info("Server %s on %s started on %s", server_name, layer, socket)
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    nodes = []
    for server_name, layer_socket_pair in addrs.ADDRS.items():
        p = Process(target=serve, args=(server_name, layer_socket_pair[0], layer_socket_pair[1],))
        p.start()
        nodes.append(p)

    for p in nodes:
        p.join()
