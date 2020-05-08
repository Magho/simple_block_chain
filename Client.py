import hashlib
import time

import jsonpickle
from Crypto.PublicKey import RSA
from Crypto import Random

from Blockchain import Blockchain
from Transaction import Transaction
from UTXO import UTXO
from blockchain_utils import consensus
from utils import contains_in_list, delete, index

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

    def make_transaction(self, value_in, recipient_in):
        """
        :param value_in:
        :param recipient_in:
        :return:
        """
        self.get_utxo_pool()

        print(f'value of transaction: {value_in}, {self.utxo_pool}')
        transaction = Transaction(time.time(), value_in, self.public_key, recipient_in, self.utxo_pool, is_original=self.original)
        to_sign = hashlib.sha256(str(transaction.hash).encode() + jsonpickle.encode(transaction.recipients).encode()).hexdigest().encode()
        print(f'-make_transaction: transaction hash = {transaction.hash}, recipients = {transaction.recipients}')
        print(f'sign transaction: {to_sign}')
        print(f'sender key {self.public_key.e}, {self.public_key.n}')
        signature = self.key.sign(to_sign, '')
        transaction.set_signature(signature)
        return transaction


    def get_utxo_pool(self):
        """
        get chain
        loop transaction
        get output transactions that has public key of client
        :return:
        """
        if self.name == 0:
            # return as it is original client has no pool and no check
            return
        blockchain = Blockchain()
        blockchain = consensus(blockchain, self.peers)
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
