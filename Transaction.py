import hashlib
from UTXO import UTXO


class Transaction:

    def __init__(self, timestamp_in, value_in, size_in, sender_in, recipient_in):
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
        self.size = size_in

        # Transaction's Unique ID (Double Hashed) ("TXID")
        self.hash = hashlib.sha256(str(hashlib.sha256(str(timestamp_in).encode() + \
                                   str(value_in).encode() + str(size_in).encode()).hexdigest()).encode())

        # For Transaction Verification
        self.sender = sender_in
        self.recipient = recipient_in

        # Transaction Linkages
        self.inputs, self.input_count = self.get_inputs()
        self.outputs, self.output_count = self.create_outputs()

    def get_inputs(self):
        """
            Go To Sender, Greedily Select Transaction Inputs from Unspent Transaction Outputs Pool
            * Add UTXO to Transaction Inputs
            * Remove from UTXO Pool - Eliminates 'Double Spend' Problem
            * Check If We're Done Adding Transaction Inputs
            return inputs, length of inputs
        """
        inputs = []
        inputs_sum = 0
        for u in self.sender.utxo_pool:

            # Add UTXO to Transaction Inputs
            i = UTXO(u)
            inputs.append(i)
            inputs_sum += u.value

            # Remove from UTXO Pool - Eliminates 'Double Spend' Problem
            self.sender.utxo_pool.remove(u)

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
        transaction_val_uxto = UTXO(self.hash, 0, self.value)
        self.sender.sign_utxo(self.recipient, transaction_val_uxto)
        outputs.append(transaction_val_uxto)

        # Recipient Accepts Output
        # Recipient Uses Public Key of Sender to Verify The Sender's Signature (To Verify Chain of Ownership!)
        if self.recipient.verify_utxo(self.sender, transaction_val_uxto):
            self.recipient.utxo_pool.append(transaction_val_uxto)

        # (If Necessary) Return Change to Sender
        if input_sum - self.value > 0:
            remainder_uxto = UTXO(self.hash, 1, input_sum - self.value)
            outputs.append(remainder_uxto)
            self.sender.utxo_pool.append(remainder_uxto)

        return outputs, len(outputs)
