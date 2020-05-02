class UTXO:

    def __init__(self, transaction_hash_in, output_index_in, value_in):
        """
            UTXO contain
            * Hash of Transaction Where This UTXO Came From
            * Which Output Was This
            * Amount of the UTXO
            * signature
        """
        self.transaction_hash = transaction_hash_in
        self.output_index = output_index_in
        self.value = value_in
        self.signature = None
