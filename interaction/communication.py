from __future__ import annotations

from datetime import datetime
from typing import Dict

import paho.mqtt.client as mqtt
from paho.mqtt import publish

import attributes
import interaction
import util

_BROKER_URL: str = "test.mosquitto.org"
_BROKER_PORT: int = 1883
_TIMEOUT: int = 15

_TOPIC_PREFIX: str = "parknet-21/communication/"


class _Subscription:
    def __init__(self, callback: interaction.Callback, receive_own: bool):
        self.callback: interaction.Callback = callback
        self.receive_own: bool = receive_own

    def handle(self, message: interaction.Message) -> None:
        """ Calls the callback function if the message applies to the subscription.

        The message applies to the subscription exactly if it was sent by another agent or if the subscription
        specifies to react to the agent's own messages.
        The callback function gets the message as its own argument.

        Args:
            message: Received message linked to the subscription.
        """

        # check if message was sent by another agent or subscription applies to the agent's own messages
        if message.sender != attributes.SIGNATURE or self.receive_own:
            self.callback(message)


@util.Singleton
class _Connection:
    def __init__(self):
        self.subscriptions: Dict[str, _Subscription] = {}
        self.client: mqtt.Client = mqtt.Client()
        self.client.on_message = self.react
        self.client.connect(_BROKER_URL, _BROKER_PORT, _TIMEOUT)

        # start listening for messages
        self.client.loop_start()

    def subscribe(self, topic: str, callback: interaction.Callback, receive_own: bool) -> None:
        """ Adds a communication subscription for a given topic.

        As there can only be one subscription per topic, prior subscriptions for the same topic are overwritten.

        Args:
            topic: Topic to subscribe to.
            callback: Callback function to be triggered when a message for the subscribed topic is received.
            receive_own: Boolean whether the sender shall receive his own messages.
        """

        # _add subscription
        self.subscriptions[topic] = _Subscription(callback, receive_own)

        # subscribe to communication broker
        self.client.subscribe(_TOPIC_PREFIX + topic, qos=1)

    @staticmethod
    def send(message: interaction.Message) -> None:
        """ Publishes an encoded message.

        Args:
            message: Message to be published.
        """

        # encode message
        json_message = message.encode()

        # publish message to broker
        publish.single(_TOPIC_PREFIX + message.topic, json_message, hostname=_BROKER_URL)

    def react(self, _client, _user, data: mqtt.MQTTMessage) -> None:
        """ Handles an incoming message by triggering the corresponding callback function (if existent).

        Args:
            _client: Client data.
            _user: User data.
            data: Encoded MQTT message.
        """

        # decode message
        message = interaction.Message.decode(data.payload.decode())

        # trigger subscription if existent
        if message.topic in self.subscriptions:
            self.subscriptions[message.topic].handle(message)


class Communication:
    class Topics:
        FORMATION = "formation"
        PROCESS_FINISHED = "process-finished"

    def __init__(self):
        self._connection: _Connection = _Connection()

    def subscribe(self, topic: str, callback: interaction.Callback, receive_own: bool = False) -> None:
        """ Adds a communication subscription to the connection.

        See Also:
            - ``def Connection.subscribe(...)``

        Args:
            topic: Topic to subscribe to.
            callback: Callback function to be triggered when a message for the subscribed topic is received.
            receive_own: Boolean whether the sender shall receive his own messages.
        """

        self._connection.subscribe(topic, callback, receive_own)

    def send(self, topic: str, content: interaction.MessageContent) -> None:
        """ Publishes a message sent by the main agent.

        Args:
            topic: Topic of the message.
            content: Content of the message (JSON compatible).
        """

        self._connection.send(interaction.Message(attributes.SIGNATURE, topic, content, datetime.now()))
