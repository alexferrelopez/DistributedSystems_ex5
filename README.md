To re-generate the Python code from the protocol buffer file, run the following command:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./epidemic_replication.proto
```