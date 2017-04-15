from math import ceil


def first_by_property(array, property_name, value):
    element = None
    for x in array:
        if x[property_name] == value:
            element = x
            break
    return element


def element_by_small_value(array, property_name):
    element = array[0]
    for x in array:
        if x[property_name] < element[property_name]:
            element = x
            break
    return element


def total_by_property(array, property_name):
    total = 0
    for x in array:
        total += x[property_name]
    return total


def sort_by_property(array, property_name, reverse):
    array.sort(key=lambda x: x[property_name], reverse=reverse)


def get_servers_to_balance(servers, current_balances):
    current_balances += 1
    servers_len = len(servers)
    if servers_len == 1:
        return

    total_files = total_by_property(servers, 'files')
    average = ceil(total_files / servers_len)

    servers_high = []
    servers_low = []

    for server in servers:
        if current_balances > 1:
            return
        elif server['files'] > average:
            servers_high.append(server)
        elif server['files'] < average:
            servers_low.append(server)

    if not servers_high:
        return

    return {
        'servers_low': servers_low,
        'servers_high': servers_high,
        'average': average
    }
