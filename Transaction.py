"""
client has: 
1) blockchain
2) his/her public & private key
3) public key of recipient
4) value he/she wants to send
5) client can get utxos pool from blockchain
6) time of transaction
"""
import hashlib
from UTXO import UTXO


class Transaction:

    def __init__(self, timestamp_in, value_in, sender_in, recipient_in, sender_utxo_pool):
        """
            transaction contain
            * timestamp
            * value
            * size
            * id --> get by hash transaction contents
            * sender
            * recipient
            * inputs
            * outputs
        """
        # Basic Transaction Data
        self.timestamp = int(timestamp_in)
        self.value = value_in
        # Transaction's Unique ID (Double Hashed) ("TXID")
        self.hash = hashlib.sha256(str(hashlib.sha256(str(timestamp_in).encode() + str(value_in).encode() + str(recipient_in).encode() + str(sender_in).encode()).hexdigest()).encode()).hexdigest()
        self.signature = None
        # For Transaction Verification
        self.sender = sender_in
        self.recipient = recipient_in

        # Transaction Linkages
        self.inputs, self.input_count = self.get_inputs(sender_utxo_pool)
        self.outputs, self.output_count = self.create_outputs()

    def get_inputs(self, utxo_pool):
        """
            Go To Sender, Greedily Select Transaction Inputs from Unspent Transaction Outputs Pool
            * Add UTXO to Transaction Inputs
            * Remove from UTXO Pool - Eliminates 'Double Spend' Problem
            * Check If We're Done Adding Transaction Inputs
            return inputs, length of inputs
        """
        inputs = []
        inputs_sum = 0
        for u in utxo_pool:

            # Add UTXO to Transaction Inputs
            inputs.append(u)
            inputs_sum += u.value

            # Remove from UTXO Pool - Eliminates 'Double Spend' Problem
            utxo_pool.remove(u)

            # Check If We're Done Adding Transaction Inputs
            if inputs_sum >= self.value:
                break

        return inputs, len(inputs)

    def create_outputs(self):
        """
            Go To Sender, Greedily Select Transaction Inputs from Unspent Transaction Outputs Pool
            * Deduct Inputs from Value
            * Send Value to Recipient --> Sender Signs Transaction with his Private Key
                (Ensures That Only The Private Key Owner Can Spend!)
            * Recipient Accepts Output --> Recipient Uses Public Key of Sender to Verify The Sender's Signature
                (To Verify Chain of Ownership!)
            return outputs, length of outputs
        """
        outputs = []

        # Deduct Inputs from Value
        input_sum = 0
        for i in self.inputs:
            input_sum += i.value

        # Send Value to Recipient
        # Sender Signs Transaction w/ Its Private Key (Ensures That Only The Private Key Owner Can Spend!)
        # transaction_val_uxto = UTXO(self.hash, 0, self.value)
        # self.sender.sign_utxo(self.recipient, transaction_val_uxto)
        # TODO list of recipient
        outputs.append({"value": self.value, "index": 0, "payee_public": self.recipient})

        # Recipient Accepts Output
        # Recipient Uses Public Key of Sender to Verify The Sender's Signature (To Verify Chain of Ownership!)


        # (If Necessary) Return Change to Sender
        if input_sum - self.value > 0:
            outputs.append({"value": input_sum - self.value, "index": 1, "payee_public": self.sender})

        return outputs, len(outputs)

    def set_signature(self, signature):
        self.signature = signature

    def verify(self, sender):
        to_verify = hashlib.sha256(str(self.hash).encode('utf-8') + str(self.recipient).encode('utf-8')).hexdigest()
        return sender.verify(str(to_verify), self.signature)

