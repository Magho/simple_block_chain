from Block import Block
from UTXO import UTXO
from utils import contains_in_list, index, delete


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
        
        for transaction in block.transactions:
            verified = self.verify_transaction(transaction)
            if not verified:
                return False

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

    def verify_transaction(self, transaction):
        """
        verify transaction:
        * check sender signature
        * check value in >= value out
        * check there exists a transaction hash in a block containing the hash of the input transaction if not original
        * check that the index of utxo recipient corresponds to the sender
        * check no transaction mention this output before.(double spending)
        :param transaction:
        :return true if transaction is valid:
        """
        verified = transaction.verify(transaction.sender)
        if not verified:
            return False

        if transaction.is_original:
            return True

        input_sum = 0
        utxo_pool = self.get_utxo_pool(transaction.sender)
        for input_utxo in transaction.inputs:
            input_sum += input_utxo.value
            if not contains_in_list(utxo_pool, input_utxo):
                return False
        output_sum = 0
        for output_utxo in transaction.outputs:
            output_sum += output_utxo.value
        if output_sum > input_sum:
            return False

    def get_utxo_pool(self, sender):
        """
        get chain
        loop transaction
        get output transactions that has public key of client
        :return:
        """
        #TODO check race condition of all APIs
        utxo_pool = []
        for block in self.chain:
            for tx in block.transactions:
                if contains_in_list(tx.recipients, sender):
                    i = index(tx.recipients, sender)
                    if i == -1:
                        raise Exception("public key is not found!!")
                    new_UTXO = UTXO(tx.hash, tx.recipients[i], tx.values[i])
                    utxo_pool.append(new_UTXO)
                inputs = tx.inputs
                for utxo_input in inputs:
                    if contains_in_list(utxo_pool, utxo_input):
                        utxo_pool = delete(utxo_pool, utxo_input)
        return utxo_pool
