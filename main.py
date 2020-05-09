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
from blockchain_utils import *
import jsonpickle

from utils import log

app = Flask(__name__)

blockchain = Blockchain()
test_names = ["special miner", "a miner"]
test_ips = ["http://197.55.175.10:5000", "http://192.168.1.108:5001"]#["http://192.168.1.108:5000", "http://192.168.1.108:5001"]
test_ports = [5000, 5001]
test = 0
miner = Miner(test_names[test], 0)
my_node_address = test_ips[test]#"http://192.168.1.108:5001"#"http://197.55.175.10:5000"
# Address format : http://IP:port
peers = set()
if miner.name != "special miner":
    node_address = "http://197.55.175.10:5000"#"http://192.168.1.108:5000"#"http://197.160.27.226:5000"#"http://102.40.55.128:5000" # Special miner
    peers.add(node_address)
    if not node_address:
        log("main_miner", "Special miner address is not specified!", "error")
        raise Exception("Node address is not specified!")

    data = {"node_address": my_node_address}
    headers = {'Content-Type': "application/json"}
    response = requests.post(node_address + "/register_node", data=json.dumps(data), headers=headers)
    log("main_miner", f"response of special miner: {response.__dict__}")
    log("main_miner", f"response of special miner(json): {response.json()}")
    chain = jsonpickle.decode(response.json()['chain'])
    threshold = response.json()['threshold']
    difficulty = response.json()['difficulty']
    blockchain.chain = chain

    peers.update(response.json()['peers'])
    peers.remove(my_node_address) # TODO should remove your address
    for peer in peers:
        response = requests.post(peer + "/register_node", data=json.dumps(data), headers=headers)

    miner.set_peers(peers)

    blockchain = consensus(blockchain, peers)

    if blockchain is None:
        log("main_miner", "Blockchain of consensus is None!", "error")
        raise Exception("None blockchain!")
else:
    blockchain.create_genesis_block()

miner.set_blockchain(blockchain)


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    log("new_transaction", f"request data: {tx_data}")
    required_fields = ["transaction"]
    if not all(k in tx_data for k in required_fields):
        return 'Invalid transaction data', 404

    transaction = jsonpickle.decode(tx_data["transaction"])
    miner.add_new_transaction(transaction)

    return "Success", 200

@app.route('/chain_peers', methods=['GET'])
def get_chain_peers():
    chain_data = jsonpickle.encode(blockchain.chain)
    return json.dumps({"length": len(blockchain.chain), "chain": chain_data, "peers": list(peers), "threshold": blockchain.threshold, "difficulty" : blockchain.difficulty}), 200

@app.route('/peers', methods=['GET'])
def get_peers():
    peers_data = jsonpickle.encode(peers)
    return json.dumps({"peers": peers_data}), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = jsonpickle.encode(blockchain.chain)
    return json.dumps({"length": len(blockchain.chain), "chain": chain_data, "threshold": blockchain.threshold, "difficulty" : blockchain.difficulty}), 200


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
    block_data = jsonpickle.decode(request.get_json()["block"]).__dict__
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
    app.run(host='0.0.0.0', port=test_ports[test], threaded=True)

