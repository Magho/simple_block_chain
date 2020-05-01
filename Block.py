class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        """
            Block header should contain
            * time stamp
            * prev block hash
            * merkle tree hash
            * nonce
            Block body should contain
            * transactions
            * transactions length
            * block index
        """
        # Block header
        # Todo

        # Block body

        # Todo
        pass

    def compute_hash(self):
        """
            A function that return the hash of the block contents.
            return sha256 hash string
        """
        # Todo
        pass
