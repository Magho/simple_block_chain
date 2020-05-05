# MINER
"""
miner functionalities:
add new transaction
send chain
send peers
add/register peer
"""
import json
import time

import requests
from flask import Flask, request

from Block import Block
from Blockchain import Blockchain
from Miner import Miner
from Transaction import Transaction
from utils import *
import jsonpickle

app = Flask(__name__)

blockchain = Blockchain()
miner = Miner("special miner", 0)
# Address format : http://IP:port
peers = set()
if miner.name != "special miner":
    node_address = "http://special miner:5000"#TODO specify IP
    if not node_address:
        print("ERROR!")
        raise Exception("Node address is not specified!")

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}
    response = requests.post(node_address + "/register_node", data=json.dumps(data), headers=headers)

    chain_dump = response.json()['chain']
    threshold = response.json()['threshold']
    difficulty = response.json()['difficulty']

    blockchain = create_chain_from_dump(chain_dump)

    peers.update(response.json()['peers'])

    miner.set_peers(peers)

    blockchain = consensus(blockchain, peers)

    if blockchain is None:
        print("ERROR, block chain is none!")
        raise Exception("None blockchain!")
else:
    blockchain.create_genesis_block()

miner.set_blockchain(blockchain)


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    print(tx_data)
    required_fields = ["transaction"]
    if not all(k in tx_data for k in required_fields):
        return 'Invalid transaction data', 404

    transaction = jsonpickle.encode(tx_data["transaction"])
    miner.add_new_transaction(transaction)

    return "Success", 200

@app.route('/chain_peers', methods=['GET'])
def get_chain_peers():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(jsonpickle.encode(block.__dict__))
    return json.dumps({"length": len(chain_data), "chain": chain_data, "peers": list(peers), "threshold": blockchain.threshold, "difficulty" : blockchain.difficulty}), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = jsonpickle.encode(blockchain.chain)
    return json.dumps({"length": len(chain_data), "chain": chain_data, "threshold": blockchain.threshold, "difficulty" : blockchain.difficulty}), 200


@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    peers.add(node_address)
    miner.set_peers(peers)
    return get_chain_peers()


@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"], block_data["transactions"], block_data["timestamp"], block_data["previous_hash"], nonce=block_data["nonce"])
    proof = block_data["hash"]
    added = blockchain.add_block(block, proof)
    if not added:
        return "The block was discarded by the node", 400
    miner.get_notified(block)
    return "Block added to the chain", 201

@app.route('/pending_tx')
def get_pending_tx():
    return jsonpickle.encode(miner.unconfirmed_transactions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

