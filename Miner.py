import hashlib
import time
from Crypto.PublicKey import RSA
from Crypto import Random
from Block import Block
from Blockchain import Blockchain
from UTXO import UTXO
import threading

from blockchain_utils import consensus, announce_new_block
from utils import transactions_difference, contains_in_list, delete, index, log


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
        self.peers = set()
        # Unspent Transaction Outputs (UXTO's); Starts w/ Initial Value In
        # self.utxo_pool = [UTXO(None, 0, initial_value_in, None)]

        # Generate Key Pair (Public, Private)
        random_generator = Random.new().read
        self.key = RSA.generate(1024, random_generator)  # Both Public & Private Keys
        self.public_key = self.key.publickey()  # For External Access
        self.state = "idle"
        self.lock = threading.Lock()
        self.got_notified = False

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
        while not computed_hash.startswith('0' * self.blockchain.difficulty) and not self.got_notified:
            block.nonce += 1
            computed_hash = block.compute_hash()
        if self.got_notified:
            self.got_notified = False
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
        log("add_new_transaction", f"New transaction is being added: {transaction.__dict__}")
        if not self.verify_transaction(transaction):
            log("add_new_transaction", "transaction verification fails", "warning")
            return False
        self.unconfirmed_transactions.append(transaction)
        log("add_new_transaction", f'miner has {len(self.unconfirmed_transactions)} unconfirmed transactions')
        self.lock.acquire()
        log("add_new_transaction", f'Mining condition: #transactions >= threshold ? {len(self.unconfirmed_transactions) >= self.blockchain.threshold} , is mining ? {self.state == "mining"}' )
        if len(self.unconfirmed_transactions) >= self.blockchain.threshold and not self.state == "mining":
            log("add_new_transaction", "Create mining thread")
            thread = threading.Thread(target=self.mine)
            self.state = "mining"
            self.mining_task = thread.start()
            log("add_new_transaction", f"mining task: {self.mining_task}")
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
            log("mine", "the block is not added even the miner mine it. the block chain last block may have been changed", "error")
            if len(self.unconfirmed_transactions) >= self.blockchain.threshold:
                log("mine", f'mine new block')
                self.mine()
            self.state = "idle"
            return
        log("mine", f'block {new_block.__dict__} is mined and added locally successfully!')
        chain_length = len(self.blockchain.chain)
        self.blockchain = consensus(self.blockchain, self.peers)
        if chain_length == len(self.blockchain.chain):
            announce_new_block(self.blockchain.get_last_block(), self.peers)
            log("mine", f'block {new_block.__dict__} is announced successfully!')
            if len(self.unconfirmed_transactions) >= self.blockchain.threshold:
                log("mine", f'mine new block')
                self.mine()
        log("mine", f'no enough transaction to mine convert to idle state')
        self.state = "idle"


    def get_notified(self, block):
        if self.state == "mining":
            self.got_notified = True
            self.state = "idle"

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
        log("verify_transaction", f'transaction verified? {verified}')
        if not verified:
            return False
        log("verify_transaction", "sender is verified successfully!")
        log("verify_transaction", f"is original transaction? {transaction.is_original}")
        if transaction.is_original:
            return True

        input_sum = 0
        log("verify_transaction", f"getting utxo pool to sender {transaction.sender.e}, {transaction.sender.n}")
        utxo_pool = self.get_utxo_pool(transaction.sender)
        log("verify_transaction", f"check utxo inputs")
        for input_utxo in transaction.inputs:
            log("verify_transaction", f"check input {input_utxo.__dict__}")
            input_sum += input_utxo.value
            log("verify_transaction", f"is input in utxo pool? {contains_in_list(utxo_pool, input_utxo)}")
            if not contains_in_list(utxo_pool, input_utxo):
                return False
        log("verify_transaction", f"input sum used: {input_sum}")
        output_sum = 0
        log("verify_transaction", f"check utxo outputs")
        for output_utxo in transaction.outputs:
            log("verify_transaction", f"check output {output_utxo.__dict__}")
            output_sum += output_utxo.value
        log("verify_transaction", f"output sum: {output_sum}")
        if output_sum > input_sum:
            return False
        return True

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
                log("get_utxo_pool", f"checking transaction {tx.__dict__}")
                log("get_utxo_pool", f"is sender in recipients list? {contains_in_list(tx.recipients, sender)}")
                if contains_in_list(tx.recipients, sender):
                    i = index(tx.recipients, sender)
                    if i == -1:
                        raise Exception("public key is not found!!")
                    log("get_utxo_pool", f"index of sender is found at {i}")
                    new_UTXO = UTXO(tx.hash, i, tx.values[i], tx.recipients[i])
                    utxo_pool.append(new_UTXO)
                inputs = tx.inputs
                log("get_utxo_pool", f"check transaction input")
                for utxo_input in inputs:
                    log("get_utxo_pool", f"check utxo input {utxo_input.__dict__}")
                    log("get_utxo_pool", f"is input in utxo pool? {contains_in_list(utxo_pool, utxo_input)}")
                    if contains_in_list(utxo_pool, utxo_input):
                        log("get_utxo_pool", f"remove input utxo from utxo pool")
                        utxo_pool = delete(utxo_pool, utxo_input)
        log("get_utxo_pool", f"utxo pool resulted: {utxo_pool}")
        return utxo_pool
