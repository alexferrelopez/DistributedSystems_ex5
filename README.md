
# Epidemic Replication Distributed System

## Overview
This project involves the creation of a multi-layered distributed system using **gRPC**, with three tiers of nodes: the **core**, **layer 1**, and **layer 2**. The system allows for real-time monitoring of data across nodes through WebSocket connections and a Flask-based web server. The system is designed to handle transactions and data replication with strong and casual consistency to ensure reliability and scalability.

## Features
- **Flask-hosted Web Server**: Provides a user-friendly interface that updates and highlights changes across nodes in real time.
- **WebSocket Server**: Periodically polls nodes to retrieve data and updates the web UI.
- **Expandable Network**: New nodes can be added seamlessly without disrupting the system.
- **Modifiable Node Functionality**: The system supports flexible node capabilities using **gRPC** for communication.
- **Data Logging**: Captures and stores logs for each node for debugging and tracking purposes.
- **Transaction Verification**: Ensures that transactions are correctly formatted and validated at each node.
- **Data Replication**: Implements strong consistency for core nodes and casual consistency for lower-layer nodes.

## Development Journal

### Initial Implementation & Distributed Design
The initial stages of the project were marked by concerns over the design of node connections. After evaluating the diagram, we chose to connect nodes in a way that avoided performance issues due to message overhead. We structured the nodes into **Core Nodes** and regular **Nodes**, leveraging **inheritance** and **composition** for efficient class design.

### WebSockets & Flask
After establishing the basic distributed network, I encountered challenges with WebSockets, as Python does not natively support WebSockets. A third-party library was required to implement WebSockets, and I used **Flask** to host the web server. Flask’s simplicity made it a good choice for this project, which involved a single-page application with minimal routing.

### Finishing Touches
The final step involved enhancing the visual aspect of the project to display real-time node updates. The web UI refreshes every 200ms unless the content remains unchanged. Different updates are color-coded for easy recognition:
- **New Key Insertions**: Green highlight.
- **Value Updates**: Blue highlight.
- **Unchanged Key-Value Pairs**: No highlight.

## Screenshots
### Web Application:
- **Real-Time Monitoring**: Demonstrates how nodes are updated and synchronized across layers.
  ![Web Application Screenshot](https://github.com/user-attachments/assets/cf8d924c-6dc6-43e0-af9f-082595bc98d0)


## Setup Instructions
1. **Install Dependencies**: Ensure Python and Flask are installed, along with the necessary WebSocket library.
2. **Run the Flask Web Server**: Launch the web server using the provided Flask application.
3. **Start WebSocket Server**: Begin polling the nodes to retrieve and display data on the UI.
4. **Extend the Network**: New nodes can be added by modifying the configuration file and integrating them into the system.


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

