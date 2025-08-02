# P2P Blockchain Simulation

This project simulates a peer-to-peer (P2P) blockchain network using Python and Flask. Multiple nodes maintain independent blockchain copies and communicate to sync blocks, register peers, and resolve conflicts using a consensus algorithm.

## Features
- Simple blockchain with transaction, block, and chain structures
- Mining logic with basic proof-of-work (PoW)
- Multiple nodes simulated via Flask (each node runs on a separate port)
- Node registration and discovery
- Consensus algorithm (longest chain wins)
- Blockchain syncing from peers
- (Bonus) Simple HTML dashboard for chain and peer status

## Requirements
- Python 3.x
- Flask
- requests

## Installation
1. Clone this repository or download the source code.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Nodes
Each node runs as a separate process on a different port. For example:
```bash
python node.py --port 5000
python node.py --port 5001
python node.py --port 5002
python node.py --port 5003
```

## API Endpoints
- `POST /transactions/new` - Add a new transaction
- `GET /mine` - Mine a new block
- `GET /chain` - Get the full blockchain
- `POST /nodes/register` - Register new peer nodes
- `GET /nodes/resolve` - Run consensus algorithm
- `GET /nodes/peers` - List all known peers

## Bonus: Dashboard
Visit `/dashboard` to view the blockchain and peer status in a simple HTML page.

## Screenshots/Logs
Include screenshots or logs of nodes syncing and resolving conflicts as part of your submission.

## License
MIT 