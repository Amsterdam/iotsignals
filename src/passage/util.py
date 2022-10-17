def keymap(callable, dictionary):
    """
    Recursively map the keys of ``dictionary`` using ``callable``. When the
    value of an item is a dictionary, it's keys will also be mapped.

    :param callable: Function to call on each key.
    :param dictionary: Dictionary to map

    :return: New dictionary with the keys mapped using the given callable
             (recursively, so keys of nested dictionaries are also mapped).
    """
    return {
        callable(key): keymap(callable, value) if isinstance(value, dict) else value
        for key, value in dictionary.items()
    }


def keyfilter(callable, dictionary):
    """
    Recursively filters ``dictionary`` using the keys of items passed to
    ``callable``. This callable should return True if the item should remain in
    the dictionary, otherwise False. When the value of an item is a dictionary,
    it will also be filtered recursively using callable.

    :param callable: Function to call for each key to determine if the item
                     should be filtered or not (True retains the item, False
                     filters it).
    :param dictionary: The dictionary to filter.

    :return: New dictionary with the keys mapped using the given callable.
    """
    return {
        key: keyfilter(callable, value) if isinstance(value, dict) else value
        for key, value in dictionary.items()
        if callable(key)
    }
