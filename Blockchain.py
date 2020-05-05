from Block import Block


class Blockchain:

    def __init__(self, difficulty=2, threshold=400):
        """
            it contain
            * difficulty
            * threshold
            * list for blocks
        """
        self.difficulty = difficulty
        self.threshold = threshold
        self.chain = []

    def create_genesis_block(self):
        """
            A function to generate genesis block and appends it to
            the chain. The block has index 0, previous_hash as 0, and
            a valid hash.
        """
        genesis_block = Block(0, [], 0, "0")
        genesis_block.nonce = 0
        computed_hash = genesis_block.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            genesis_block.nonce += 1
            computed_hash = genesis_block.compute_hash()
        genesis_block.hash = computed_hash
        self.chain.append(genesis_block)

    def is_valid_proof(self, block, block_hash):
        """
            * Check if block_hash is valid hash of block and satisfies the difficulty criteria.
            return true or false
        """
        return (block_hash.startswith('0' * self.difficulty) and
                block_hash == block.compute_hash())

    def add_block(self, block, proof):
        """
            A function that adds the block to the chain after verification.
            Verification includes:
            * The previous_hash referred in the block and the hash of latest block
              in the chain match.
            * check if block contain threshold transactions
            * Checking if the proof is valid.
            * verify transactions
            return True if valid or False if not valid
        """
        previous_hash = self.get_last_block().hash
        if previous_hash != block.previous_hash:
            return False

        if block.transactions_length != self.threshold:
            return False

        if not self.is_valid_proof(block, proof):
            return False

        # TODO verify transactions

        block.hash = proof
        self.chain.append(block)
        return True

    def get_last_block(self):
        """
            return last block of the chain
        """
        return self.chain[-1]

    def change_difficulty(self, difficulty):
        self.difficulty = difficulty
