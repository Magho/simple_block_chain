import jsonpickle


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