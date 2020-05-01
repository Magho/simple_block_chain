class Client:

    def __init__(self, name_in, initial_value_in):
        """
            new client should have
            * name
            * initial_value
            * public key
            * private key
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