import hashlib
import json
from time import time
from urllib.parse import urlparse

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        # Create the genesis block
        self.new_block(previous_hash='1', nonce=100)

    def register_node(self, address):
        """Add a new node to the list of nodes."""
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """Determine if a given blockchain is valid."""
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            # Check that the PoW is correct
            if not self.valid_proof(last_block['nonce'], block['nonce'], last_block['previous_hash'], block['transactions']):
                return False
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self, get_chains_from_peers):
        """Consensus algorithm: resolves conflicts by replacing our chain with the longest one in the network."""
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        for node in neighbours:
            response = get_chains_from_peers(node)
            if response and response['length'] > max_length and self.valid_chain(response['chain']):
                max_length = response['length']
                new_chain = response['chain']
        if new_chain:
            self.chain = new_chain
            return True
        return False

    def new_block(self, nonce, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'nonce': nonce,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_nonce, previous_hash, transactions):
        nonce = 0
        while not self.valid_proof(last_nonce, nonce, previous_hash, transactions):
            nonce += 1
        return nonce

    @staticmethod
    def valid_proof(last_nonce, nonce, previous_hash, transactions, difficulty=4):
        guess = f'{last_nonce}{nonce}{previous_hash}{json.dumps(transactions, sort_keys=True)}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == '0' * difficulty 