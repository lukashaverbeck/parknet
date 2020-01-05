# This module contains entities that handle the communication and interaction between agents
# as well as the coordination of their actions.
# Therefore it defines a communication interface that allows to subscribe to, send and 
# receive messages in a local network.
# It handles coordination by exchanging information about the arrangement of vehicles in
# a parking lot as well as their intention to take certain actions in order to ensure permission
# to take an action without one central decision maker.
#
# author: @LukasGra
# author: @lukashaverbeck
# version: 2.0 (29.12.2019)

import json
import time
import vehicle
import requests
import constants as const
from threading import Thread
from http.server import HTTPServer
from util import Singleton, threaded
from vision import FrontAgentScanner
from connection import get_local_ip, check_if_up,  Server


@Singleton
class Communication:
    """ handles the communication between multiple agents by assigning callback functions to certain events  """

    def __init__(self):
        """ initializes a communication object and starts a local HTTP Server """

        # intitialize and start web server
        Server.communication = self
        self.local_ip = "127.0.0.1"
        self.connection_status = True
        self.server = HTTPServer((self.local_ip, 80), Server)
        print(f"Starting Webserver on {self.local_ip}")
        server_thread = Thread(target=self.server.serve_forever)
        server_thread.start()

        self.subscriptions = []
        self.agent = vehicle.Agent.instance()

    def set_local_ip(self , ip_address):
        self.local_ip = ip_address
        self.connection_status = True
        print(f"Restarting Webserver on {self.local_ip}")

        try:
            self.server = HTTPServer((ip_address, 80), Server)
            server_thread = Thread(target=self.server.serve_forever)
            server_thread.start()
        except OSError:
            print("Already connected to this address or address blocked")

    def lost_connection(self):
        self.connection_status = False

    def scan_ips_from_network(self):
        """ determines the used ip addresses in the network

            Returns:
                list: list of used ips in the network
        """

        ips = []
        local_ip = self.local_ip
        ip_parts = local_ip.split(".")

        try:
            ip_network = ip_parts[0] + "." + ip_parts[1] + "." + ip_parts[2] + "."
        except IndexError:
            raise IndexError("local IP address is invalid")
        else:
            for i in range(2, 158):
                ip = ip_network + str(i)
                result = check_if_up(ip)
                if result: ips.append(ip)

            if local_ip in ips:
                ips.remove(local_ip)

            return ips

    def subscribe(self, topic, callback):
        """ subscribes to a topic by defining a callback function that is triggered when the event occours

            Args:
                topic (str): topic of the event
                callback (function): the method to run when the event occours
        """

        self.subscriptions.append({
            "topic": topic,
            "callback": callback
        })

    def send(self, topic, content):
        """ sends a message to all agents in the network

            Args:
                topic (str): topic of the message
                content (object): JSON compatible object to be transferred
        """

        # get JSON representation of the message to be sent
        message = Message(self.agent, topic, content)
        json_message = message.dumps()

        # send message to every agent in the network
        if self.connection_status:
            for ip in self.scan_ips_from_network():
                requests.post("http://" + ip, data=json_message)
            requests.post("http://" + self.local_ip, data=json_message)



    def trigger(self, message):
        """ triggers every callback with the topic transmitted by the message
            NOTE if a callback function is triggered the function is provided with the transmitted message

            Args:
                message (str): JSON encoded message that triggered an event
        """

        message = Message.loads(message)

        # check every subscription and trigger the callback if the topics match
        for subscription in self.subscriptions:
            if subscription["topic"] == message.topic:
                try:
                    subscription["callback"](message)
                except TypeError:
                    raise TypeError("A triggered callback was not callable.")


class Message:
    """ helper class wrapping a transferrable message """

    def __init__(self, sender, topic, content, timestamp = time.time()):
        """ initializes the message

            Args:
                sender (Agent or str): sending agent or the agent's ID
                topic (str): concern of the message
                content (object): JSON compatible object to be transmited via the message
                timestamp (float): UNIX timestamp of the creation of the message
        """

        if type(sender).__name__ == "Agent": sender = sender.id

        self.sender = sender
        self.topic = topic
        self.content = content
        self.timestamp = timestamp

        # assert that the timestamp is valid
        assert self.timestamp <= time.time(), "invalid future timestamp"

    def __repr__(self):
        return f"Message - #{self.sender} : {self.topic} : {self.content} ({self.timestamp})"

    def dumps(self):
        """ creates a JSON representation of the message

            Returns:
                str: JSON string containing the encoded information about the message
        """

        return json.dumps({
            "sender": self.sender,
            "topic": self.topic,
            "content": self.content,
            "timestamp": self.timestamp
        })

    @staticmethod
    def loads(json_data):
        """ creates the Message object of its JSON representation

            Args:
                json_data (str): JSON representation of the message

            Returns:
                Message: Message object correpsonding to the JSON string
        """

        try:
            # extract data from JSON string if it has been provided
            data = json.loads(json_data)
            sender = data["sender"]
            topic = data["topic"]
            content = data["content"]
            timestamp = data["timestamp"]

            return Message(sender, topic, content, timestamp)
        except json.JSONDecodeError:
            raise TypeError("Tried to decode a message with an invalid JSON representation.")
        except KeyError:
            raise KeyError("Tried to decode a message with a missing attribute.")


@Singleton
class ActionManager:
    """ coordinates the interactive behaviour of multiple agents by
        determining which agent is allowed to execute which action at what time
    """

    WAIT_ACT = 1
    WAIT_SEND_GLOBAL = 0.5
    WAIT_FIRST_IN_QUEUE = WAIT_SEND_GLOBAL * 4
    WAIT_CHECK_PERMISSION = 0.5

    def __init__(self):
        """ initializes the ActionManager by initializing its attributes and starting continuous tasks """

        self.agent = vehicle.Agent.instance()
        self.global_action = None
        self.local_actions = []
        self.global_verification = False
        self.communication = Communication.instance()
        self.formation = Formation.instance()
        self.driver = vehicle.Driver.instance()

        # map modes to the driver methods that are proactive and
        # require coordniation to execute the corresponding actions
        self.PROACTIVAE_ACTIONS = {
            const.Mode.AUTONOMOUS: self.driver.follow_road,
            const.Mode.ENTER: self.driver.enter_parking_lot,
            const.Mode.LEAVE: self.driver.leave_parking_lot,
            const.Mode.MANUAL: self.driver.manual_driving
        }

        # ensure that the functions for executing an action exist
        for mode, action in self.PROACTIVAE_ACTIONS.items():
            assert callable(action), f"driver cannot execute action {action} for {mode}"

        # start executing continuous tasks
        self.update()
        self.check_global_permission()
        self.act()

        # subscribe to completion and global action messages
        self.communication.subscribe(const.Topic.GLOBAL_ACTION_COMPLETED, self.receive_completion)
        self.communication.subscribe(const.Topic.GLOBAL_ACTION_ACTIVE, self.receive_global_action)

    def __iter__(self):
        yield from self.local_actions

    @threaded
    def update(self):
        """ continuously checks if the agent is currently taking an
            action and in this case sends it to every agent in the network
        """

        while True:
            # share current global action if it is the agent's current action
            if self.global_action is not None: 
                if self.global_action.is_owner(self.agent): 
                    self.send_global_action()

            time.sleep(self.WAIT_SEND_GLOBAL)

    @threaded
    def check_global_permission(self):
        """ continuously checks if the agent is allowed to make its local 
            agent it intents to take global and in this case executes this action
        """

        while True:
            local_action = self.local_actions[0] if len(self.local_actions) > 0 else None

            # skip the loop if the local action cannot be made global
            if local_action is None:  # check if there is a local action
                time.sleep(self.WAIT_CHECK_PERMISSION)
                continue
            if self.global_action is not None:  # check if there is already a global action
                time.sleep(self.WAIT_CHECK_PERMISSION)
                continue
            if local_action.mode not in self.PROACTIVAE_ACTIONS:  # check if the action does not require coordination
                time.sleep(self.WAIT_CHECK_PERMISSION)
                continue

            # share the agent's action and wait in order to determine whether it is actually the foremost
            self.global_action = local_action
            time.sleep(self.WAIT_FIRST_IN_QUEUE) 
            if self.global_action.is_owner(self.agent):
                self.global_verification = True
                self.local_actions.pop(0)

    @threaded
    def act(self):
        """ continuously determines which actions to execute and executes them by addressing the driver """

        # continuously determine and take allowed actions
        while True:
            # special cases : searching a parking lot and autonomous driving does not require coordination
            if len(self.local_actions) > 0:
                local_action = self.local_actions[0]
                if local_action == const.Mode.SEARCH:
                    self.driver.search_parking_lot()
                    self.local_actions.pop(0)
                    continue
                if local_action == const.Mode.AUTONOMOUS:
                    self.driver.search_parking_lot()
                    self.local_actions.pop(0)
                    continue

            if self.global_verification:  # permission for every action
                try:
                    self.PROACTIVAE_ACTIONS[self.global_action.mode]()
                    self.global_verification = False
                    self.send_completion()
                except KeyError:
                    raise KeyError("Tried to execute an action that is not declared to be proactive in a proactive context.")
            elif self.global_action is not None:  # autonomous reaction to the global action
                # ensure that an agent does not react to an action it is 
                # trying to execute itself while waiting for permission
                if self.global_action.is_owner(self.agent):
                    time.sleep(self.WAIT_ACT)
                    continue
                
                # determine which reaction corresponds to the current global action
                # most global actions require other agents not to act at all
                if self.global_action.mode == const.Mode.LEAVE:  # create space
                    self.driver.create_space(self.global_action.agent)
                else:  # do not act
                    time.sleep(self.WAIT_ACT)
                    continue

    def append(self, mode):
        """ appends a new action to the list of local action

            Args:
                mode (str): type of the action
        """

        assert mode in const.Mode.ALL, "tried to append an unknown mode"
        action = Action(self.agent, mode)
        self.local_actions.append(action)

    def remove(self, mode):
        """ removes every action with a certain mode from the list of local actions
            NOTE this method does not effect global actions

            Args:
                mode (str): mode of actions to be removed
        """

        self.local_actions = [action for action in self if action.mode != mode]

    def send_global_action(self):
        """ sends the current global action to every agent in the nework """

        action_data = self.global_action.dumps()
        self.communication.send(const.Topic.GLOBAL_ACTION_ACTIVE, action_data)

    def receive_global_action(self, message):
        """ handles the receivement of the currently globally executed action

            Args:
                message (Message): message wrapping the information about the current global action
        """

        action = Action.loads(message.content)
        self.global_action = Action.choose(self.global_action, action)

    def send_completion(self):
        """ informs every agent in the network that the global action the agent was taking has terminated """

        self.global_action = None
        self.communication.send(const.Topic.GLOBAL_ACTION_COMPLETED, None)

    def receive_completion(self, message):
        """ handles the receivement of the information that the global action has terminated

            Args:
                message (Message): message wrapping the information
        """

        self.global_action = None


class Action:
    """ helper class representing the state of an agent's behaviour """

    def __init__(self, agent, mode, timestamp = time.time()):
        """ initializes the action

            Args:
                agent (Agent or str): agent taking the action or the agent's ID
                mode (str): type of the action 
                timestamp (float): UNIX timestamp of the moment the action was registered
        """

        if type(agent).__name__ == "Agent": agent = agent.id

        self.agent = agent
        self.mode = mode
        self.timestamp = timestamp

        # assert that the timestamp is valid
        assert self.timestamp <= time.time(), "invalid future timestamp"

    def __repr__(self):
        return f"Action[#{self.agent} : {self.mode} ({self.timestamp})]"

    def dumps(self):
        """ creates a JSON representation of the action

            Returns:
                str: JSON string containing the encoded information about the message
        """

        return json.dumps({
            "mode": self.mode,
            "agent": self.agent,
            "timestamp": self.timestamp
        })

    def is_owner(self, agent):
        """ checks if the action is taken by a particular agent
        
            Args:
                agent (Agent or str): agent or agent ID to be checked
            
            Returns:
                bool: True if the agent takes the action - otherwhise False
        """

        if type(agent).__name__ == "Agent": agent = agent.id
        return agent == self.agent

    @staticmethod
    def loads(json_data):
        """ creates the Action object of its JSON representation
            NOTE if an action attribute is not provided by the JSON string it will be set to None

            Args:
                json_data (str): JSON representation of the action

            Returns:
                Action: Action object correpsonding to the JSON string
        """

        try:
            # extract data from JSON string if it has been provided
            data = json.loads(json_data)
            mode = data["mode"] if "mode" in data else None
            agent = data["agent"] if "agent" in data else None
            timestamp = data["timestamp"] if "timestamp" in data else None

            return Action(agent, mode, timestamp)
        except json.JSONDecodeError:
            raise TypeError("Tried to decode a message with an invalid JSON representation.")
        except KeyError:
            raise KeyError("Tried to decode a message with a missing attribute.")

    @staticmethod
    def choose(a, b):
        """ determines which one to choose out of two actions

            Args:
                a (Action): first action to be compared to the other
                b (Action): second action to be compared to the other

            Returns:
                Action: the foremost action out of the two - if the actions have the exact same timestamp the action 
                        with alphabetically lower agent ID is returned

                NOTE if one of the actions is None, the other action is returned in every case
        """

        if a is None: return b
        if b is None: return a

        try:
            if a.timestamp < b.timestamp: return a
            if b.timestamp > a.timestamp: return b
            if a.agent < b.agent: return a
            return b
        except AttributeError:
            raise AttributeError("Tried to compare actions with missing attributes.")


@Singleton
class Formation:
    """ keeps track of the relative position of multiple agents within an agent network """
    
    UPDATE_INTERVAL = 1  # seconds to wait after sending checking for being the first agent
    AWAIT_CONFIRMATION = 1  # seconds to wait for the confirmation of the receivement of a backpass

    def __init__(self):
        """ initializes the Formation and starts to update its agents """

        self.agent = vehicle.Agent.instance()
        self.agents = []
        self.tmp_agents = []
        self.max_length = 0.0
        self.tmp_max_length = 0.0
        self.communication = Communication.instance()
        self.backpass_confirmed = False
        self.latest_update = 0.0

        self.update()

    def __len__(self):
        return len(self.agents)

    def __repr__(self):
        agent_ids = "#" + ", #".join(self.agents) if len(self.agents) > 0 else ""
        return f"Formation[{agent_ids}] (max length: {self.max_length}cm)"

    def __iter__(self):
        yield from self.agents

    def calc_gap(self):
        """ calculates the minimal gap between two agents so that the longest vehicle can still leave the parking lot
            NOTE the calculated gap already includes the safety distance that must be kept in any case

            Returns:
                float: length of minimal gap
        """

        number_of_agents = len(self)        
        needed_space = self.max_length * const.Driving.LEAVE_PARKING_LOT_PROPORTION
        needed_space += number_of_agents * const.Driving.SAFETY_DISTANCE

        try:
            return needed_space / number_of_agents + const.Driving.SAFETY_DISTANCE
        except ZeroDivisionError:
            return 0

    @threaded
    def update(self):
        """ constantly updates the current formation by exchanging data with other agents within a network """

        # subscribe to the relevant event topics
        self.communication.subscribe(const.Topic.FORMATION_BACKWARD_PASS, self.receive_backward_pass)
        self.communication.subscribe(const.Topic.FORMATION_FORWARD_PASS, self.receive_forward_pass)
        self.communication.subscribe(const.Topic.FORMATION_CONFIRMATION, self.receive_confirmation)

        with FrontAgentScanner.instance() as front_agent_scanner:
            while True:
                if front_agent_scanner.id is None:
                    # start sending the formation backwards
                    self.reset_tmp()
                    self.append()
                    self.send_backward_pass()

                time.sleep(self.UPDATE_INTERVAL)

    def send_backward_pass(self):
        """ sends an agent list backwards to other agents within the network """

        # send the message in a separate thread
        thread = Thread(target=lambda: self.communication.send(const.Topic.FORMATION_BACKWARD_PASS, self.data()))
        thread.start()

        time.sleep(self.AWAIT_CONFIRMATION)  # wait for a possible receiver to confirm the backpass

        if not self.backpass_confirmed:
            # last in line -> formation complete -> send forwards
            self.backpass_confirmed = False
            self.accept_tmp()
            self.send_forward_pass()

    def receive_backward_pass(self, message):
        """ callback function handling a formation that was sent backwards
        
            Args:
                message (Message): message containing the formation's agent list
        """

        if message.timestamp <= self.latest_update: return

        # check if the formation was sent to this specific agent
        with FrontAgentScanner.instance() as front_agent_scanner:
            if front_agent_scanner.id == message.sender:
                self.latest_update = message.timestamp
                self.send_confirmation(message.sender)
                
                # update the delivered formation and send it further backwards
                self.tmp_agents = message.content["agents"]
                self.tmp_max_length = message.content["longest"]
                self.append()
                self.send_backward_pass()

    def send_forward_pass(self):
        """ sends an agent list forwards to other agents within the network """

        # send the message in a separate thread
        thread = Thread(target=lambda: self.communication.send(const.Topic.FORMATION_FORWARD_PASS, self.data()))
        thread.start()

    def receive_forward_pass(self, message):
        """ callback function handling a formation that was sent forwards as valid formation

            Args:
                message (Message): message containing the formation's agent list
        """

        agents = message.content["agents"]
        max_length = message.content["longest"]

        # ensure that the formation contains the agent and that it is up to date
        if self.agent.id not in message.content["agents"]: return
        if message.timestamp <= self.latest_update: return

        self.latest_update = message.timestamp
        self.tmp_agents = agents
        self.tmp_max_length = max_length
        self.accept_tmp()

    def send_confirmation(self, receiver_id):
        """ sends a confirmation that a backpass was received

            Args:
                receiver_id (str): ID of the agent that sent the backpass
        """

        # send the message in a separate thread
        thread = Thread(target=lambda: self.communication.send(const.Topic.FORMATION_CONFIRMATION, receiver_id))
        thread.start()

    def receive_confirmation(self, message):
        """ callback function handling a message confirming that a backpass was received by the addressee

            Args:
                message (Message): message confirming a backpass
        """

        self.backpass_confirmed = message.content == self.agent.id

    def append(self):
        """ appends the agent to the temporary formation """

        self.tmp_agents.append(self.agent.id)
        if self.tmp_max_length < self.agent.length:
            self.tmp_max_length = self.agent.length

    def accept_tmp(self):
        """ makes the temporary formation the current 'official' formation and resets the temporary """

        self.agents = [agent for agent in self.tmp_agents]
        self.max_length = self.tmp_max_length
        self.reset_tmp()

    def data(self):
        """ creates a dictionary of the current temporary formation to be sent within the agent network

            Returns:
                dict: current temporry formation data (agent IDs and length of the longest vehicle)
        """

        return {
            "agents": self.tmp_agents,
            "longest": self.tmp_max_length,
        }

    def reset_tmp(self):
        """ sets the temporary formation to its default values """

        self.tmp_agents = []
        self.tmp_max_length = 0.0

    def comes_before(self, a, b):
        """ determines whether an agent is located further ahead within the formation

            Args:
                a (Agent or str): agent or agent ID to check if it is located ahead of b
                b (Agent or str): agent or agent ID to check if it is located behind a

            Returns:
                bool: True if a is located ahead of b - otherwhise False
                NOTE if neither of the both agents exist in the formation False is returned
        """

        if type(a).__name__ == "Agent": a = a.id
        if type(b).__name__ == "Agent": b = b.id

        for agent in self.agents:
            if agent in [a, b]: return agent == a

        return False

    def distance(self, a, b):
        """ determines the distance distance between two agents in a formation
            in terms of how many vehicles stand between them

            Args:
                a (Agent or str): agent or agent ID to determine the distance to b
                b (Agent or str): agent or agent ID to determine the distance to a

            Returns:
                int: number of vehicles between a and b

            Raises:
                ValueError: if at least one of the given agents is not part of the formation
        """

        if type(a).__name__ == "Agent": a = a.id
        if type(b).__name__ == "Agent": b = b.id

        return abs(self.agents.index(a) - self.agents.index(b)) - 1
