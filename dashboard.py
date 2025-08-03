import os
import sys
import time
import requests
import subprocess
import signal
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

NODES = [5000, 5001, 5002, 5003]
processes = []

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/start', methods=['POST'])
def start_nodes():
    """Start all blockchain nodes"""
    global processes
    
    if processes:
        return jsonify({"message": "Nodes already running"})
    
    try:
        for port in NODES:
            process = subprocess.Popen([
                sys.executable, 'node.py', '--port', str(port)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            processes.append(process)
        
        time.sleep(3)  # Wait for nodes to start
        
        # Register nodes with each other
        for i, port in enumerate(NODES):
            for j, other_port in enumerate(NODES):
                if i != j:
                    try:
                        requests.post(f'http://localhost:{port}/nodes/register', 
                                    json={'nodes': [f'http://localhost:{other_port}']})
                    except:
                        pass
        
        return jsonify({"message": "All nodes started successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/stop', methods=['POST'])
def stop_nodes():
    """Stop all blockchain nodes"""
    global processes
    
    for process in processes:
        process.terminate()
        process.wait()
    
    processes.clear()
    return jsonify({"message": "All nodes stopped!"})

@app.route('/api/status')
def get_status():
    """Get status of all nodes"""
    status = []
    
    for port in NODES:
        try:
            response = requests.get(f'http://localhost:{port}/chain', timeout=2)
            if response.status_code == 200:
                data = response.json()
                # Try to get pending transactions
                pending = 0
                try:
                    pending_response = requests.get(f'http://localhost:{port}/pending', timeout=1)
                    if pending_response.status_code == 200:
                        pending_data = pending_response.json()
                        pending = pending_data.get('pending', 0)
                except:
                    pass
                
                status.append({
                    'port': port,
                    'online': True,
                    'blocks': data.get('length', 0),
                    'pending': pending
                })
            else:
                status.append({
                    'port': port,
                    'online': False,
                    'blocks': 0,
                    'pending': 0
                })
        except:
            status.append({
                'port': port,
                'online': False,
                'blocks': 0,
                'pending': 0
            })
    
    return jsonify(status)

@app.route('/api/chain/<int:port>')
def api_chain(port):
    try:
        response = requests.get(f'http://localhost:{port}/chain', timeout=2)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to get blockchain'}), 500
    except Exception:
        return jsonify({'error': 'Node not accessible'}), 500

@app.route('/api/mine/<int:port>', methods=['POST'])
def api_mine(port):
    try:
        response = requests.get(f'http://localhost:{port}/mine', timeout=30)
        if response.status_code == 200:
            result = response.json()
            return jsonify({"message": f"Block mined! Block #{result.get('index', 'unknown')}"})
        else:
            return jsonify({'error': 'Mining failed'}), 500
    except Exception as e:
        return jsonify({'error': f'Mining failed: {str(e)}'}), 500

@app.route('/api/transaction', methods=['POST'])
def api_transaction():
    data = request.get_json()
    sender = data.get('sender', '')
    recipient = data.get('recipient', '')
    amount = data.get('amount', 0)
    port = data.get('port', 5000)
    if not all([sender, recipient, amount]):
        return jsonify({'error': 'Please fill all fields'}), 400
    try:
        response = requests.post(
            f'http://localhost:{port}/transactions/new',
            json={'sender': sender, 'recipient': recipient, 'amount': float(amount)},
            timeout=5
        )
        if response.status_code == 201:
            return jsonify({'message': 'Transaction created!'})
        else:
            return jsonify({'error': 'Transaction failed'}), 500
    except Exception as e:
        return jsonify({'error': f'Transaction failed: {str(e)}'}), 500

@app.route('/api/pending/<int:port>')
def api_pending(port):
    try:
        response = requests.get(f'http://localhost:{port}/pending', timeout=2)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'pending': 0})
    except Exception:
        return jsonify({'pending': 0})

@app.route('/node/<int:port>')
def node_detail(port):
    """Render detailed node view page"""
    return render_template('node_detail.html', port=port)

@app.route('/api/connections/<int:port>')
def api_connections(port):
    """Get peer connections for a specific node"""
    try:
        response = requests.get(f'http://localhost:{port}/nodes/peers', timeout=2)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'peers': []})
    except Exception:
        return jsonify({'peers': []})

if __name__ == '__main__':
    port=os.getenv('PORT', 8080)
    app.run(host='0.0.0.0', port=port, debug=False) 
