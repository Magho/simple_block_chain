import hashlib
import time

from Crypto.PublicKey import RSA
from Crypto import Random

from Transaction import Transaction


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

    def make_transaction(self, value_in, recipient_in):
        transaction = Transaction(time.time(), value_in, self.public_key, recipient_in, self.utxo_pool)
        to_sign = hashlib.sha256(str(transaction.hash).encode('utf-8') + str(transaction.recipients).encode('utf-8')).hexdigest()
        signature = self.key.sign(to_sign)
        transaction.set_signature(signature)
        return transaction


    def get_utxo_pool(self):
        """
        get chain
        loop transaction
        get output transactions that has public key of client
        :return:
        """

        pass