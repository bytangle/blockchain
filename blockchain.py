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
        genesis_hash = self.hash_block("genesis block")
        self.append_block(
            hash_of_previous_block = genesis_hash,
            nonce = self.proof_of_work(0, genesis_hash, [])
        )
    
    def proof_of_work(self, index, hash_of_previous_block, transactions):
        nonce = 0

        while self.valid_proof(index, hash_of_previous_block, transactions, nonce)is False:
            nonce += 1
        
        return nonce
    
    def valid_proof(self, index, hash_of_previous_block, transactions, nonce):
        content = f'{index}{hash_of_previous_block}{transactions}{nonce}'

        content_hash = hashlib.sha256(content).hexdigest()

        return content_hash[:len(self.difficulty_target)] == self.difficulty_target
    
    def append_block(self, hash_of_previous_block, nonce):
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
    
    