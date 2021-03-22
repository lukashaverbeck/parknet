from typing import List, Hashable, Dict


def assert_keys_exist(keys: List[Hashable], dictionary: Dict) -> None:
    """ Ensures that that a given dictionary contains the given keys.

    This function only asserts that every key of ``keys`` exists in ``dictionary``. It does not check whether the
    assigned values are ``None``.

    Args:
        keys: List of keys to be contained in the dictionary.
        dictionary: Dictionary to check whether it contains the keys.

    Raises:
        AssertionError: If ``dictionary`` does not contain at least one key of ``keys``.
    """

    # iterate over every key and ensure that it is contained in the dictionary
    for key in keys:
        assert key in dictionary, f"Missing key {key} in {dictionary}."
