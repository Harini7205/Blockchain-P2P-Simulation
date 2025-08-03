from flask import Flask, jsonify, request, render_template, render_template_string
import requests
import sys
from uuid import uuid4
from blockchain import Blockchain
from flask_cors import CORS
import subprocess
import signal
import os

app = Flask(__name__)
CORS(app)

# Unique identifier for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

node_processes = {}

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_nonce = last_block['nonce']
    previous_hash = blockchain.hash(last_block)
    nonce = blockchain.proof_of_work(last_nonce, previous_hash, blockchain.current_transactions)
    # Reward for mining
    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)
    block = blockchain.new_block(nonce, previous_hash)
    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'nonce': block['nonce'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    def get_chain_from_peer(node):
        try:
            url = f'http://{node}/chain'
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                return r.json()
        except Exception:
            return None
    replaced = blockchain.resolve_conflicts(get_chain_from_peer)
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200

@app.route('/nodes/peers', methods=['GET'])
def peers():
    response = {
        'peers': list(blockchain.nodes)
    }
    return jsonify(response), 200

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/pending', methods=['GET'])
def pending():
    return jsonify({'pending': len(blockchain.current_transactions)})

@app.route('/start_node')
def start_node():
    port = int(request.args.get('port'))
    if port in node_processes and node_processes[port].poll() is None:
        return jsonify({'status': 'already running'})
    # Start a new node process
    proc = subprocess.Popen(['python', 'node.py', '--port', str(port)], creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
    node_processes[port] = proc
    return jsonify({'status': 'started'})

@app.route('/stop_node')
def stop_node():
    port = int(request.args.get('port'))
    proc = node_processes.get(port)
    if proc and proc.poll() is None:
        if os.name == 'nt':
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            proc.terminate()
        return jsonify({'status': 'stopped'})
    return jsonify({'status': 'not running'})

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--port', required=True, type=int, help='port to listen on')
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port) 
