import json
import logging
import threading

from services.addrs import Layer
from services.node import NodeService
from . import epidemic_replication_pb2
from . import logging_level

logging.basicConfig(level=logging_level, format="%(message)s")
logger = logging.getLogger(__name__)


class CoreNodeService(NodeService):
    def __init__(self, layer: Layer, server_name: str):
        self._num_updates = 0
        self._num_updates_lock = threading.Lock()
        self._event = threading.Event()

        super().__init__(layer, server_name)

    def update_lower_layer(self):
        while True:
            self._event.wait()
            self._send_data_to_nodes(self._lower_layer_stubs)
            self._event.clear()

    def processTransaction(self, request, context):
        try:
            with self._data_lock:
                answer, is_read_only = self._parse_client_transaction(request.transaction, self._layer)
                self._debug_log(f"Transaction: {request.transaction} Answer: {answer}")
                if not is_read_only:
                    self._log_data(json.dumps(self._data))
                    # Update layer nodes
                    self._debug_log("Sending data to layer nodes")
                    self._send_data_to_nodes(self._layer_stubs)
                    # Update lower layer nodes if num_updates == 10
                    self.increment_num_updates()
            return epidemic_replication_pb2.TransactionResponse(status=0, answer=answer)
        except Exception as e:
            return epidemic_replication_pb2.TransactionResponse(status=-1, answer=str(e))

    def increment_num_updates(self):
        with self._num_updates_lock:
            self._num_updates += 1
            if self._num_updates == 10:
                self._debug_log("Sending data to lower layer nodes")
                self._num_updates = 0
                self._event.set()

    def nodeUpdate(self, request, context):
        try:
            self._debug_log(f"Received data from {request.sender}: {request.data}")
            with self._data_lock:
                self._data = json.loads(request.data)
                self.increment_num_updates()
                self._log_data(request.data)
            return epidemic_replication_pb2.StatusResponse(status=0, status_message="Data updated successfully")
        except Exception as e:
            return epidemic_replication_pb2.StatusResponse(status=-1, status_message=self._server_name + ": " + str(e))
