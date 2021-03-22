import interaction


def test_messaging():
    """ Tests whether subscribing, sending and receiving messages works properly.

    Setup:
        One agent. Run test.

    Expected Results:
        Five messages with the topic ``should-receive-this`` are printed in the terminal.
        No messages with the topic ``should-not-receive-this`` are printed.
    """

    communication = interaction.Communication()
    communication.subscribe("should-receive-this", print, True)
    communication.subscribe("should-not-receive-this", print, False)

    for _ in range(5):
        communication.send("should-receive-this", "This message should be displayed.")
        communication.send("should-not-receive-this", "This message should not be displayed.")
