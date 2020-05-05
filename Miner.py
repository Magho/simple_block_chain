import hashlib
import time
from Crypto.PublicKey import RSA
from Crypto import Random
from Block import Block
from Blockchain import Blockchain
from UTXO import UTXO
import threading

from blockchain_utils import consensus, announce_new_block, transactions_difference, contains_in_list, delete, index


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
        self.unconfirmed_transactions = []
        self.unconfirmed_transactions_in_progress = []
        self.blockchain = None
        self.name = name_in
        self.peers = []
        # Unspent Transaction Outputs (UXTO's); Starts w/ Initial Value In
        # self.utxo_pool = [UTXO(None, None, initial_value_in)]

        # Generate Key Pair (Public, Private)
        random_generator = Random.new().read
        self.key = RSA.generate(1024, random_generator)  # Both Public & Private Keys
        self.public_key = self.key.publickey()  # For External Access
        self.state = "idle"
        self.mining_task = None
        self.lock = threading.Lock()

    def set_blockchain(self, blockchain):
        self.blockchain = blockchain

    def proof_of_work(self, block):
        """
            Function that tries different values of the nonce to get a hash
            that satisfies our difficulty criteria.
            return computed hash
        """
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.blockchain.difficulty):
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
        if not self.verify_transaction(transaction):
            return False
        self.unconfirmed_transactions.append(transaction)
        self.lock.acquire()
        if len(self.unconfirmed_transactions) >= self.blockchain.threshold and not self.state == "mining":
                thread = threading.Thread(target=self.mine)
                self.state = "mining"
                self.mining_task = thread.start()
        self.lock.release()


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

            if not self.blockchain.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    #TODO check BFT
    def mine(self):
        """
            This function serves as an interface to add the pending
            transactions to the blockchain by adding them to the block
            and figuring out Proof Of Work or BFT.
            return true if done (pow or bft) or false if not
        """
        if not self.unconfirmed_transactions:
            return False
        last_block = self.blockchain.get_last_block()
        self.unconfirmed_transactions_in_progress, self.unconfirmed_transactions = self.get_transactions_tobe_mined()
        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions_in_progress,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)
        proof = self.proof_of_work(new_block)
        added = self.blockchain.add_block(new_block, proof)
        if not added:
            raise Exception("Mining Failed!!")
        chain_length = len(self.blockchain.chain)
        self.blockchain = consensus(self.blockchain, self.peers)
        if chain_length == len(self.blockchain.chain):
            announce_new_block(self.blockchain.get_last_block(), self.peers)
            if len(self.unconfirmed_transactions) >= self.blockchain.threshold:
                self.mine()
        self.state = "idle"
        self.mining_task = None


    def get_notified(self, block):
        if self.state == "mining":
            self.state = "idle"
            self.mining_task.stop()
        self.unconfirmed_transactions = transactions_difference(self.unconfirmed_transactions, block.transactions)
        self.unconfirmed_transactions = self.unconfirmed_transactions + transactions_difference(self.unconfirmed_transactions_in_progress, block.transactions)
        self.unconfirmed_transactions_in_progress = []
        self.lock.acquire()
        if len(self.unconfirmed_transactions) >= self.blockchain.threshold and not self.state == "mining":
            thread = threading.Thread(target=self.mine)
            self.state = "mining"
            self.mining_task = thread.start()
        self.lock.release()



    def get_transactions_tobe_mined(self):
        """
            Filter the unconfirmed_transactions and select a subset to mine
        :return:
            transactions_tobe_mined
        """
        length = len(self.unconfirmed_transactions)
        thr = self.blockchain.threshold
        if length > thr:
            return self.unconfirmed_transactions[0:thr], self.unconfirmed_transactions[thr:length]
        return self.unconfirmed_transactions, []

    # Transaction Verification Methods
    def sign_utxo(self, recipient_in, utxo_in):
        """
            From Satoshi's White Paper:
                - Each owner transfers the coin to the next by digitally signing
                a hash of the previous transaction and the public key of the next owner
            * create (utxo, receipent) to sign
            * sign
        """
        to_sign = hashlib.sha256(str(utxo_in.transaction_hash.hexdigest()).encode('utf-8') + \
                                 str(recipient_in.public_key).encode('utf-8'))

        utxo_in.signature = self.key.sign(str(to_sign.hexdigest()).encode('utf-8'), '')

    def verify_utxo(self, sender_in, utxo_in):
        """
            From Satoshi's White Paper:
            - A payee can verify the signatures to verify the chain of ownership.
            * create (utxo, receipent) to vertify
            *  verify using public key
            return true if valid signature or false if not
        """
        to_verify = hashlib.sha256(str(utxo_in.transaction_hash.hexdigest()).encode('utf-8') + \
                                   str(self.public_key).encode('utf-8'))

        return sender_in.public_key.verify(str(to_verify.hexdigest()), utxo_in.signature)

    def set_peers(self, peers):
        self.peers = peers

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
        for block in self.blockchain.chain:
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
