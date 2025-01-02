import json
import logging
import threading
from time import sleep

import grpc

import epidemic_replication_pb2
import epidemic_replication_pb2_grpc
from addrs import Layer, replicas
from epidemic_replication_pb2_grpc import NodeServiceServicer
from utils import logging_level

logging.basicConfig(level=logging_level, format="%(message)s")
logger = logging.getLogger(__name__)


class NodeService(NodeServiceServicer):
    def __init__(self, layer: Layer, server_name: str):
        # setting up the node exactly as described in diagram from the exercise statement
        self._layer_nodes: list = replicas[server_name][0]
        self._lower_layer_nodes: list = replicas[server_name][1]
        self._layer = layer
        self._data = {}
        self._data_lock = threading.Lock()
        self._lower_layer_stubs = []
        self._server_name = server_name
        self._setup_done = False
        self._layer_stubs = []

        if self._lower_layer_nodes:
            threading.Thread(target=self.update_lower_layer).start()

        threading.Thread(target=self.network_setup).start()

    def network_setup(self):
        for node in self._layer_nodes:
            s = self.connect_to_server(node[1])
            self._layer_stubs.append(s)

        for node in self._lower_layer_nodes:
            s = self.connect_to_server(node[1])
            self._lower_layer_stubs.append(s)

    def processTransaction(self, request, context):
        try:
            answer, _ = self._parse_client_transaction(request.transaction, self._layer)
            return epidemic_replication_pb2.TransactionResponse(status=0, answer=answer)
        except Exception as e:
            return epidemic_replication_pb2.TransactionResponse(status=-1, answer=str(e))

    def nodeUpdate(self, request, context):
        try:
            self._debug_log(f"Received data from {request.sender}: {request.data}")
            with self._data_lock:
                self._data = json.loads(request.data)
            return epidemic_replication_pb2.StatusResponse(status=0, status_message="Data updated successfully")
        except Exception as e:
            return epidemic_replication_pb2.StatusResponse(status=-1, status_message=self._server_name + ": " + str(e))

    def _send_data_to_nodes(self, node_stubs: list):
        for stub in node_stubs:
            response = stub.nodeUpdate(
                epidemic_replication_pb2.NodeDataUpdate(sender=self._server_name, data=json.dumps(self._data)))
            if response.status != 0:
                logger.warning(response.status_message)

    def update_lower_layer(self):
        while True:
            sleep(10)
            with self._data_lock:
                self._send_data_to_nodes(self._lower_layer_stubs)

    def connect_to_server(self, socket):
        try:
            channel = grpc.insecure_channel(socket)
            stub = epidemic_replication_pb2_grpc.NodeServiceStub(channel)
            grpc.channel_ready_future(channel).result(timeout=5)
            self._debug_log(f"Connected to the server {socket}")
            return stub
        except grpc.FutureTimeoutError:
            logger.error("Failed to connect to the server %s", socket)

    def _parse_client_transaction(self, transaction: str, layer: Layer) -> (str, bool):
        split = transaction.split(",")
        begin = split[0].strip()

        is_read_only = self._is_read_only(begin, layer)

        if self.is_not_read_only(begin, layer) or is_read_only:
            actions: list = split[1:-1]
            answer = ""
            for i, action in enumerate(actions):
                a: str = action.strip()

                if a.startswith("r"):
                    key = a.strip("r()")
                    answer += self._data.get(key, "0") + ","
                elif action.strip().startswith("w"):
                    if is_read_only:
                        raise ValueError("Invalid transaction")
                    key = a.strip("w(")
                    new_data = actions[i + 1].strip(")")
                    self._data.update({key: new_data})
                    answer += "ok,"
                else:
                    continue

            answer += " c"

            return answer, is_read_only
        else:
            raise ValueError("Invalid transaction")

    def _debug_log(self, message):
        logger.info(f"{self._server_name}: {message}")

    @staticmethod
    def is_not_read_only(begin, layer):
        return len(begin) == 1 and begin == "b" and layer == Layer.CORE

    @staticmethod
    def _is_read_only(begin, layer):
        return len(begin) == 2 and begin[0] == "b" and begin[1].isdecimal() and int(begin[1]) == layer.value
