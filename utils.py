import json

import requests

from Block import Block
from Blockchain import Blockchain


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


def consensus(blockchain, peers):
    """
    Our simple consensus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    longest_chain = None
    current_len = len(blockchain.chain)
    for node in peers:
        response = requests.get(f'{node}/register_node')# IP_peer:port/chain
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain
    if longest_chain:
        blockchain.chain = longest_chain
        return blockchain
    return blockchain


def announce_new_block(block, peers):
    for peer in peers:
        url = f'{peer}/add_block'
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))


def transactions_difference(transactions1, transactions2):
    result = []
    for transaction1 in transactions1:
        found = False
        for transactions2 in transactions2:
            found = transactions2.hash == transaction1.hash
            if found:
                break
        if not found:
            result.append(transaction1)
    return result




