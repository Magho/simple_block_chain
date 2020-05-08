import json
from hashlib import sha256

import jsonpickle


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        """
            Block header should contain
            * time stamp
            * prev block hash
            * merkle tree hash
            * nonce
            * index
            Block body should contain
            * transactions
            * transactions length
            * block index
        """
        # Block header
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.merkle_tree_hash = self.get_merkle_tree_hash(transactions)
        self.nonce = nonce
        self.index = index
        # Block body
        self.transactions = transactions
        self.transactions_length = len(transactions)

    def compute_hash(self):
        dict_to_be_hashed = jsonpickle.encode((self.transactions, self.merkle_tree_hash, self.previous_hash))
        return sha256(dict_to_be_hashed.encode()).hexdigest()

    def get_merkle_tree_hash(self, transactions):
        if len(transactions) == 0:
            return False
        # get hash of each transaction
        transactions_hashes = []
        for transaction in transactions:
            transactions_hashes.append(transaction.hash)

        transactions_hashes.append("Marker")
        while True:
            t1 = transactions_hashes.pop(0)
            if str(t1) == "Marker":
                t1 = transactions_hashes.pop(0)
                if len(transactions_hashes) == 0:
                    return t1
                transactions_hashes.append("Marker")
            t2 = transactions_hashes.pop(0)
            if str(t2) == "Marker":
                if len(transactions_hashes) == 0:
                    return t1
                t2 = t1
                transactions_hashes.insert(0, "Marker")
            combine_t1_t2_hash = sha256(str(t1).encode() + str(t2).encode()).hexdigest()
            transactions_hashes.append(combine_t1_t2_hash)


