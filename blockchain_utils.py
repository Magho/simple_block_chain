import json

import jsonpickle
import requests

from Block import Block
from Blockchain import Blockchain
from utils import log


def create_chain_from_dump(chain_dump, threshold=400, difficulty=2):
    generated_blockchain = Blockchain(threshold, difficulty)
    generated_blockchain.create_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data["index"], block_data["transactions"], block_data["timestamp"], block_data["previous_hash"], nonce=block_data["nonce"])
        proof = block_data['hash']
        if idx > 0:
            added = generated_blockchain.add_block(block, proof)
            if not added:
                raise Exception("the chain dump is tempered!!")
        else:
            continue
    return generated_blockchain


def check_chain_validity(blockchain, chain):
    """
        A helper method to check if the entire blockchain is valid.
        Iterate through every block and check if it is valid
        return true if valid or false if not
    """
    result = True
    previous_hash = "0"

    for block in chain:
        block_hash = block.hash
        # remove the hash field to recompute the hash again
        # using `compute_hash` method.
        delattr(block, "hash")
        if not blockchain.is_valid_proof(block, block_hash) or previous_hash != block.previous_hash:

            result = False
            break

        block.hash, previous_hash = block_hash, block_hash

    return result


def consensus(blockchain, peers):
    """
    Our simple consensus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    log("consensus", "begin consensus")
    longest_chain = None
    current_len = len(blockchain.chain)
    for node in peers:
        log("consensus", f'ask node: {node}')
        response = requests.get(f'{node}/chain')# IP_peer:port/chain
        length = response.json()['length']
        chain = jsonpickle.decode(response.json()['chain'])
        log("consensus", f'chain got: {chain} from node {node}')
        if length > current_len and check_chain_validity(blockchain, chain):
            log("consensus", f'chain of node {node} is valid and longer chain. updating chain')
            current_len = length
            longest_chain = chain
    if longest_chain:
        blockchain.chain = longest_chain
        return blockchain
    return blockchain

def get_peers(peer):
    """
    get peer
    """
    response = requests.get(f'{peer}/peers')
    peers = jsonpickle.decode(response.json()['peers'])
    return peers


def announce_new_block(block, peers):
    headers = {'Content-Type': "application/json"}
    data = {"block": jsonpickle.encode(block)}
    for peer in peers:
        url = f'{peer}/add_block'
        requests.post(url, data=json.dumps(data), headers=headers)


def announce_new_transaction(transaction, peers):
    headers = {'Content-Type': "application/json"}
    data = {"transaction": jsonpickle.encode(transaction)}
    for peer in peers:
        log("announce_new_transaction", f"inform node {peer}")
        url = f'{peer}/new_transaction'
        requests.post(url, data=json.dumps(data), headers=headers)





