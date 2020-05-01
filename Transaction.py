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
        # Todo
        pass

    def get_inputs(self):
        """
            Go To Sender, Greedily Select Transaction Inputs from Unspent Transaction Outputs Pool
            * Add UTXO to Transaction Inputs
            * Remove from UTXO Pool - Eliminates 'Double Spend' Problem
            * Check If We're Done Adding Transaction Inputs
            return inputs, length of inputs
        """
        # Todo
        pass

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
        # Todo
        pass

