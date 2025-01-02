import json
import logging
import threading

import epidemic_replication_pb2
from addrs import Layer
from node import NodeService
from utils import logging_level

logging.basicConfig(level=logging_level, format="%(message)s")
logger = logging.getLogger(__name__)


class CoreNodeService(NodeService):
    def __init__(self, layer: Layer, server_name: str):
        self._num_updates = 0
        self._num_updates_lock = threading.Lock()
        self._num_lock_t1 = threading.Lock()
        self._num_lock_t2 = threading.Lock()
        self._num_lock_t1.acquire()
        self._num_lock_t2.acquire()

        super().__init__(layer, server_name)

    def update_lower_layer(self):
        while True:
            with self._num_lock_t1:
                self._send_data_to_nodes(self._lower_layer_stubs)
            self._num_lock_t2.release()
            self._num_lock_t1.acquire()

    def processTransaction(self, request, context):
        try:
            with self._data_lock:
                answer, is_read_only = self._parse_client_transaction(request.transaction, self._layer)
                self._debug_log(f"Transaction: {request.transaction} Answer: {answer}")
                if not is_read_only:
                    # Update layer nodes
                   """ 
                   for node in self._layer_nodes:
                   s = self.connect_to_server(node[1])
                   s.nodeUpdate(epidemic_replication_pb2.NodeDataUpdate(sender=self._server_name,data=json.dumps(self._data)))
                   """
                   self._send_data_to_nodes(self._layer_stubs)
                   self.increment_num_updates()
            return epidemic_replication_pb2.TransactionResponse(status=0, answer=answer)
        except Exception as e:
            return epidemic_replication_pb2.TransactionResponse(status=-1, answer=str(e))

    def increment_num_updates(self):
        with self._num_updates_lock:
            self._num_updates += 1
            if self._num_updates == 10:
                self._num_updates = 0
                while not self._num_lock_t1.locked():
                    pass
                self._num_lock_t1.release()
                self._num_lock_t2.acquire()

    def nodeUpdate(self, request, context):
        try:
            self._debug_log(f"Received data from {request.sender}: {request.data}")
            with self._data_lock:
                self._data = json.loads(request.data)
                self.increment_num_updates()
            return epidemic_replication_pb2.StatusResponse(status=0, status_message="Data updated successfully")
        except Exception as e:
            return epidemic_replication_pb2.StatusResponse(status=-1, status_message=self._server_name + ": " + str(e))
