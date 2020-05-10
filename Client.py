import hashlib
import time

import jsonpickle
from Crypto.PublicKey import RSA
from Crypto import Random

from Blockchain import Blockchain
from Transaction import Transaction
from UTXO import UTXO
from blockchain_utils import consensus
from utils import contains_in_list, delete, index, log


class Client:
    def __init__(self, name_in, peers):
        """
            new client should have
            * name
            * initial_value
            * public key
            * private key
        """

        random_generator = Random.new().read
        self.key = RSA.generate(1024, random_generator)
        self.public_key = self.key.publickey()
        self.name = name_in
        self.peers = peers
        self.utxo_pool = []
        self.chain = None
        self.original = name_in == 0
        self.total_number_messages = 0

    def make_transaction(self, value_in, recipient_in, mode="pow"):
        """
        :param value_in:
        :param recipient_in:
        :return:
        """
        self.get_utxo_pool(mode)
        log("make_transaction", f"value of transaction {value_in}, current utxo pool {self.utxo_pool}")
        transaction = Transaction(time.time(), value_in, self.public_key, recipient_in, self.utxo_pool, is_original=self.original)
        to_sign = hashlib.sha256(str(transaction.hash).encode() + jsonpickle.encode(transaction.recipients).encode()).hexdigest().encode()
        log("make_transaction", f"transaction hash: {transaction.hash}, transaction recipients: {transaction.recipients}")
        log("make_transaction", f"sign transaction, string to sign: {to_sign}")
        log("make_transaction", f"sender key: e: {self.public_key.e}, n: {self.public_key.n}")
        signature = self.key.sign(to_sign, '')
        transaction.set_signature(signature)
        return transaction


    def get_utxo_pool(self, mode="pow"):
        """
        get chain
        loop transaction
        get output transactions that has public key of client
        :return:
        """
        self.total_number_messages += len(self.peers)

        if self.name == 0:
            # return as it is original client has no pool and no check
            log("PERFORMANCE", f'Original client total number of message sent = {self.total_number_messages} messages')
            return
        blockchain = Blockchain()
        blockchain = consensus(blockchain, self.peers, mode=mode)
        self.total_number_messages += len(self.peers)
        log("PERFORMANCE", f'Average number of message sent per block for client {self.name} = {self.total_number_messages / len(blockchain.chain)} messages/block')
        log("get_utxo_pool", f'blockchain chain: {blockchain.chain}')
        self.utxo_pool = []
        for block in blockchain.chain:
            for tx in block.transactions:
                if contains_in_list(tx.recipients, self.public_key):
                    i = index(tx.recipients, self.public_key)
                    new_UTXO = UTXO(tx.hash,  i, tx.values[i], tx.recipients[i])
                    self.utxo_pool.append(new_UTXO)
                inputs = tx.inputs
                for utxo_input in inputs:
                    if contains_in_list(self.utxo_pool, utxo_input):
                        self.utxo_pool = delete(self.utxo_pool, utxo_input)
