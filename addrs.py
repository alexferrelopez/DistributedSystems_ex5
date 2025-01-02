from enum import Enum

_base_ip = "127.0.0.1"


class Layer(Enum):
    CORE = 0
    LAYER_1 = 1
    LAYER_2 = 2


ADDRS = {
    "A1": (Layer.CORE, _base_ip + ":50051"),
    "A2": (Layer.CORE, _base_ip + ":50052"),
    "A3": (Layer.CORE, _base_ip + ":50053"),
    "B1": (Layer.LAYER_1, _base_ip + ":50054"),
    "B2": (Layer.LAYER_1, _base_ip + ":50055"),
    "C1": (Layer.LAYER_2, _base_ip + ":50056"),
    "C2": (Layer.LAYER_2, _base_ip + ":50057"),
}

core_layer_replicas = [ADDRS["A1"], ADDRS["A2"], ADDRS["A3"]]

replicas = {
    # (layer replicas, lower layer replicas)
    "A1": ([ADDRS["A2"], ADDRS["A3"]], []),
    "A2": ([ADDRS["A1"], ADDRS["A3"]], [ADDRS["B1"]]),
    "A3": ([ADDRS["A1"], ADDRS["A2"]], [ADDRS["B2"]]),
    "B1": ([], []),
    "B2": ([], [ADDRS["C1"]], ADDRS["C2"]),
    "C1": ([], []),
    "C2": ([], []),
}
