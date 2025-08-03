# P2P Blockchain Network Simulation

A simple peer-to-peer blockchain network simulation built with Python and Flask. Demonstrates blockchain fundamentals including consensus algorithms, node synchronization, and conflict resolution.

Check it out live on https://blockchain-p2p-simulation.onrender.com

## Features
- Complete blockchain implementation with PoW mining
- Multi-node P2P network simulation
- Consensus algorithm (longest chain wins)
- Web dashboard for real-time monitoring
- One-click node management (Start/Stop all nodes)
- Detailed node status view, along with all transactions (Reward of 1 for every mining)
- Conflict simulation and resolution

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the dashboard:**
   ```bash
   python dashboard.py
   ```

3. **Open browser:**
   Navigate to `http://localhost:8080`

4. **Start the network:**
   - Click "Start All Nodes" button
   - Create transactions and mine blocks
   - Watch real-time status updates

## Manual Setup (Alternative)

Start individual nodes:
```bash
python node.py --port 5000
python node.py --port 5001
python node.py --port 5002
python node.py --port 5003
```

## API Endpoints

### Node Endpoints
- `POST /transactions/new` - Create transaction
- `GET /mine` - Mine a block
- `GET /chain` - Get blockchain
- `POST /nodes/register` - Register peers
- `GET /nodes/resolve` - Run consensus

### Dashboard Endpoints
- `POST /api/start` - Start all nodes
- `POST /api/stop` - Stop all nodes
- `GET /api/status` - Get node status

## License
MIT 
