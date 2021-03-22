import attributes


def test_attributes() -> None:
    """ Tests whether the main agent's attributes are set correctly.

    Setup:
        One agent. Run the test.

    Expected Results:
        Prints the agent's correct delta, signature and steering parameters in the terminal.
    """

    print(f"Delta is {attributes.DELTA}.")
    print(f"Signature is {attributes.SIGNATURE}.")
    print(f"Steering parameters are {attributes.STEERING_PARAMETERS}.")
