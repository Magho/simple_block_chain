from Blockchain import Blockchain


class Miner:

    def __init__(self, name_in, initial_value_in):
        """
            it contain
            * empty list of received transactions
            * block_chain
            * name
            * initial_value
            * public key
            * private key
        """
        # Todo
        self.unconfirmed_transactions = []

    def proof_of_work(self, block):
        """
            Function that tries different values of the nonce to get a hash
            that satisfies our difficulty criteria.
            return computed hash
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def bft(self, block):
        """
            Function that get votes from all members on block validity
            return valid or not (majority vote)
        """
        # Todo
        pass

    def add_new_transaction(self, transaction):
        """
            add received transaction to the list of received transactions
        """
        self.unconfirmed_transactions.append(transaction)

    def check_chain_validity(self, chain):
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

            if not Blockchain.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self):
        """
            This function serves as an interface to add the pending
            transactions to the blockchain by adding them to the block
            and figuring out Proof Of Work or BFT.
            return true if done (pow or bft) or false if not
        """
        # Todo
        pass

    # Transaction Verification Methods
    def sign_utxo(self, recipient_in, utxo_in):
        """
            From Satoshi's White Paper:
                - Each owner transfers the coin to the next by digitally signing
                a hash of the previous transaction and the public key of the next owner
            * create (utxo, receipent) to sign
            * sign
        """
        # Todo
        pass

    def verify_utxo(self, sender_in, utxo_in):
        """
            From Satoshi's White Paper:
            - A payee can verify the signatures to verify the chain of ownership.
            * create (utxo, receipent) to vertify
            *  verify using public key
            return true if valid signature or false if not
        """
        # TODO
        pass
