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
