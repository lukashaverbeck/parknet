from __future__ import annotations

import json
from datetime import datetime
from typing import TypeVar, Generic, Callable, Any

import util

MessageContent = TypeVar("MessageContent")


class _Keys:
    SENDER: str = "sender"
    CONTENT: str = "content"
    TOPIC: str = "topic"
    DATE: str = "date"


class Message(Generic[MessageContent]):
    def __init__(self, sender: str, topic: str, content: MessageContent, date: datetime):
        self.sender = sender
        self.topic = topic
        self.content = content
        self.date = date

    def encode(self) -> str:
        """ Creates a JSON representation of the message.

        The JSON representation contains the message's sender, content, topic and UNIX timestamp.

        Returns:
            The JSON representation of the message.
        """

        return json.dumps({
            _Keys.SENDER: self.sender,
            _Keys.CONTENT: self.content,
            _Keys.TOPIC: self.topic,
            _Keys.DATE: self.date.timestamp()
        })

    @staticmethod
    def decode(json_message: str) -> Message[MessageContent]:
        """ Creates a message from a given json representation of that message.

        The JSON representation must contain the message's sender, topic, content and UNIX timestamp.

        Args:
            json_message: JSON representation of the message.

        Returns:
            The message represented by the JSON string.

        Raises:
            AssertionError: If the message does not contain the required message information.
        """

        # decode json data
        data = json.loads(json_message)

        # data must contain the message's sender, topic, content and date
        util.assert_keys_exist([_Keys.SENDER, _Keys.TOPIC, _Keys.CONTENT, _Keys.DATE], data)

        return Message(
            data[_Keys.SENDER],
            data[_Keys.TOPIC],
            data[_Keys.CONTENT],
            datetime.fromtimestamp(data[_Keys.DATE])
        )

    def __repr__(self):
        return f"Message[#{self.sender}: {self.topic}: {self.date}: {self.content}]"


Callback = Callable[[Message], Any]
