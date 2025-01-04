To re-generate the Python code from the protocol buffer file, run the following command:

```bash
python -m grpc_tools.protoc -I=protos/ --python_out=services/proto --grpc_python_out=services/proto protos/epidemic_replication.proto
```

To run the whole system, run the following commands:

```bash
python main.py
```
```bash
python monitor.py
```
```bash
python webapp/app.py
```

To connect a client to the system, run the following command:

```bash
python client.py
```

