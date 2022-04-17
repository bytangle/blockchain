from crypt import methods
import sys

import json
import hashlib

from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

import requests
from urllib.parse import urlparse

class Blockchain(object):
    difficulty_target = "0000"

    def hash_block(self, block):
        block_encoded = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_encoded).hexdigest()

    def __init__(self):
        # stores all blocks in the blockchain
        self.chain = []
        
        # temporarily store transactions for the current block
        self.current_transactions = []

        # genesis block
        genesis_hash = self.hash_block("genesis_block")
        self.append_block(
            hash_of_previous_block = genesis_hash,
            nonce = self.proof_of_work(0, genesis_hash, [])
        )
    
    def proof_of_work(self, index, hash_of_previous_block, transactions):
        nonce = 0

        while self.valid_proof(index, hash_of_previous_block, transactions, nonce) is False:
            nonce += 1
        
        return nonce
    
    def valid_proof(self, index, hash_of_previous_block, transactions, nonce):
        content = f'{index}{hash_of_previous_block}{transactions}{nonce}'

        content_hash = hashlib.sha256(content.encode()).hexdigest()

        return content_hash[:len(self.difficulty_target)] == self.difficulty_target
    
    def append_block(self, hash_of_previous_block : str, nonce : int) -> dict[str, any]:
        block = {
            'index': len(self.chain),
            'timestamp': time(),
            'transactions': self.current_transactions,
            'nonce': nonce,
            'hash_of_previous_block': hash_of_previous_block
        }

        self.current_transactions = []
        self.chain.append(block)
        
        return block
    
    def addTransaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'amount': amount,
            'recipient': recipient,
            'sender': sender
        })

        return self.last_block['index'] + 1
    
    @property
    def last_block(self):
        return self.chain[-1]


# REST API
app = Flask(__name__)
# globally identified identifier for this node
node_identifier = str(uuid4()).replace("-","")

# blockchain
blockchain = Blockchain()

# get full blockchain
@app.route("/blockchain", methods = ['GET'])
def fun_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200

# mining
@app.route("/mine", methods = ['GET'])
def mine_block():
    blockchain.addTransaction(
        sender = "O",
        recipient = node_identifier,
        amount = 1
    )

    last_block_hash = blockchain.hash_block(blockchain.last_block)

    index = len(blockchain.chain)
    nonce = blockchain.proof_of_work(index, last_block_hash, blockchain.current_transactions)

    block = blockchain.append_block(last_block_hash, nonce)

    response = {
        'index': block['index'],
        'message': 'New block mined',
        'hash_of_previous_block': block['hash_of_previous_block'],
        'nonce': block['nonce'],
        'transactions': block['transactions']
    }

    return jsonify(response), 200


# adding transactions
@app.route('/transactions/new', methods = ['GET'])
def new_transction():
    # value from client
    values = request.get_json()

    required_fields = ['sender', 'recipient', 'amount']

    if not all(k in values for k in required_fields):
        return ('Missing fields', 200)
    
    index = blockchain.addTransaction(
        sender = values['sender'],
        recipient = values['recipient'],
        amount = values['amount']
    )

    response = {'message' : f'transaction will be added to block {index}'}

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = int(sys.argv[1]))