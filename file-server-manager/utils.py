def first_by_property(array, property_name, value):
    element = None
    for x in array:
        if x[property_name] == value:
            element = x
            break
    return element
