"""
1) read file
2) we need special client zero to have balance = the price of his/her all transaction
3) create client according to file mentioning new id
4) make transaction
"""
from Client import Client
from utils import announce_new_transaction

clients = {}
peers = set()
peers.add("http://localhost:5000")
clients[0] = Client(0, peers)
f = open("TxDataset/txdataset.txt", "r")
lines = f.readlines()
for line in lines:
    parameters = line.split("\t")
    print(parameters)
    sender = None
    recipients = []
    values = []
    for parameter in parameters:
        if 'intput' in parameter:
            sender_id = int(parameter[parameter.index(":") + 1:])
            if sender_id not in clients.keys():
                raise Exception("Sender doesn't exist")
            sender = clients[sender_id]
        if 'value' in parameter:
            values.append(float(parameter[parameter.index(":") + 1:]))
        if 'output' in parameter:
            recipient_id = int(parameter[parameter.index(":") + 1:])
            if recipient_id not in clients.keys():
                clients[recipient_id] = Client(recipient_id, peers)
            recipients.append(clients[recipient_id].public_key)
    transaction = sender.make_transaction(values, recipients)
    announce_new_transaction(transaction, peers)



