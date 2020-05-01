from Block import Block


class Blockchain:

    def __init__(self, difficulty):
        """
            it contain
            * list for blocks
            * difficulty
            * create genesis_block
        """
        # Todo
        pass

    def create_genesis_block(self):
        """
            A function to generate genesis block and appends it to
            the chain. The block has index 0, previous_hash as 0, and
            a valid hash.
            return the starter block
        """
        # Todo
        pass

    def add_block(self, block, proof):
        """
            A function that adds the block to the chain after verification.
            Verification includes:
            * Checking if the proof is valid.
            * The previous_hash referred in the block and the hash of latest block
              in the chain match.
            * verify transactions
            return True if valid or False if not valid
        """
        # Todo
        pass

    def get_last_block(self):
        """
            return last block of the chain
        """
        # Todo
        pass

