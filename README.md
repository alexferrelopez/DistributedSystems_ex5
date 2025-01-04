To re-generate the Python code from the protocol buffer file, run the following command:

```bash
python -m grpc_tools.protoc -I=protos/ --python_out=services/proto --grpc_python_out=services/proto protos/epidemic_replication.proto
```

To run the whole system, run the following commands:

For the whole distributed system:
```bash
python main.py
```

For the websocket server:
```bash
python monitor.py
```

For the webapp checking the websocket server:
```bash
python webapp/app.py
```

To connect a client to the system, run the following command:
```bash
python client.py
```

