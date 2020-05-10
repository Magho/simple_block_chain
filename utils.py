import os
import sys

import jsonpickle
import logging

from Crypto import Random
from Crypto.PublicKey import RSA

logging.addLevelName(logging.DEBUG, 'D')
logging.addLevelName(logging.WARNING, 'W')
logging.addLevelName(logging.ERROR, 'E')
logging.basicConfig(format='%(levelname)s:[%(threadName)s,%(name)s] %(message)s', level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout)])





def transactions_difference(transactions1, transactions2):
    result = []
    for transaction1 in transactions1:
        found = False
        for transaction2 in transactions2:
            found = transaction2.hash == transaction1.hash
            if found:
                break
        if not found:
            result.append(transaction1)
    return result


def contains_in_list(list, object):
    list_encoding = jsonpickle.encode(list)
    object_encoding = jsonpickle.encode(object)
    return object_encoding in list_encoding


def delete(list, object):
    object_encoding = jsonpickle.encode(object)
    for e in list:
        element_encoding = jsonpickle.encode(e)
        if element_encoding == object_encoding:
            list.remove(e)
    return list


def index(list, object):
    object_encoding = jsonpickle.encode(object)
    for i, e in enumerate(list):
        element_encoding = jsonpickle.encode(e)
        if element_encoding == object_encoding:
            return i
    return -1


def log(function_name, message, message_type="debug"):
    logger = logging.getLogger(function_name)
    if message_type == "debug":
        logger.debug(message)
    elif message_type == "warning":
        logger.warning(message)
    elif message_type == "error":
        logger.error(message)
    else:
        logger.error("message type is not clear!")

def generate_malicious_chain(chain):
    random_generator = Random.new().read
    key = RSA.generate(1024, random_generator)
    public_key = key.publickey()
    for block in chain:
        for transaction in block.transactions:
            transaction.recipients[0] = public_key
    return chain