import time
import threading

from Communication import Communication

TOPIC_CONFIRMATION = "formation/confirm-backward-pass"
TOPIC_FORWARD_PASS = "formation/forward-pass"
TOPIC_BACKWARD_PASS = "formation/backward-pass"


class Formation:
    """ keeps track of the relative position of multiple agents within an agent network """

    UPDATE_INTERVAL = 2
    AWAIT_CONFIRMATION = 3

    def __init__(self, agent):
        """ initializes an empty formation of agents

            Args:
                agent (Agent): agent owning the formation
        """

        self.__agents = []
        self.__longest = 0.0

        self.__agent = agent
        self.__tmp_agents = []
        self.__communication = Communication(self.__agent.get_id())
        self.__confirmed_backpass = False

        self.update()

    def calc_gap(self):
        """ calculates the minimal gap between two agents

            Returns:
                float: length of minimal gap rounded to 2 decimal places
        """
        
        number_of_agents = len(self.__agents)
        needed_space_proportion = 1.4
        needed_space = self.__longest * needed_space_proportion

        return round(needed_space / number_of_agents, 2)

    def add_agent(self, agent):
        """ adds an agent to the formation

            Args:
                agent (dict): dictionary with the agent's id and length
        """

        self.__agents.append(agent)

        if agent["length"] > self.__longest:
            self.__longest = agent["length"]

    def clear(self):
        """ resets the formation to its default values """

        self.__agents = []
        self.__longest = 0

    def update(self):
        """ constantly updates the current formation by exchanging data with other agents within a network """

        self.__communication.subscribe(TOPIC_BACKWARD_PASS, self.receive_backward_pass)
        self.__communication.subscribe(TOPIC_FORWARD_PASS, self.receive_forward_pass)
        self.__communication.subscribe(TOPIC_CONFIRMATION, self.receive_confirmation)

        while True:
            front_agent_id = None  # TODO

            if front_agent_id == None:
                self.__tmp_agents = [self.__agent.get_id()]
                self.send_backward_pass()

                time.sleep(self.AWAIT_CONFIRMATION)

                if not self.__confirmed:
                    print("set", self.__agents, "to", self.__tmp_agents)
                    self.__agents = self.__tmp_agents
                    self.send_forward_pass()

                self.__confirmed_backpass = False

            time.sleep(self.UPDATE_INTERVAL)
            
    def receive_backward_pass(self, message):
        """ callback function handling a formation that was sent backwards
        
            Args:
                message (Message): message containing the formation's agent list
        """

        front_agent_id = None  # TODO

        # check if the formation was sent to this specific agent
        if front_agent_id == message.sender():
            self.send_confirmation(message.sender())
            
            self.__tmp_agents = message.content()
            self.__tmp_agents.append(self.__agent.get_id())
            self.send_backward_pass()
    
    def receive_forward_pass(self, message):
        """ callback function handling a formation that was sent forwards as valid formation

            Args:
                message (Message): message containing the formation's agent list
        """

        self.__agents = message.content()

    def receive_confirmation(self, message):
        """ callback function handling a message confirming that a backpass was received by the addressee

            Args:
                message (Message): message confirming a backpass

            TODO it might be reasonable to embed further validation if the up-to-date formation was received
        """

        if message.receiver() == self.__agent.get_id():
            self.__confirmed_backpass = True

    def send_backward_pass(self):
        """ sends an agent list backwards to other agents within the network """

        thread = threading.Thread(target=lambda: self.__communication.send(TOPIC_BACKWARD_PASS, self.__tmp_agents))
        thread.start()

    def send_forward_pass(self):
        """ sends an agent list forwards to other agents within the network """

        thread = threading.Thread(target=lambda: self.__communication.send(TOPIC_FORWARD_PASS, self.__tmp_agents))
        thread.start()

    def send_confirmation(self, sender):
        """ sends a confirmation that a backpass was received

            Args:
                sender (str): ID of the agent that sent the backpass
        """

        thread = threading.Thread(target=lambda: self.__communication.send(TOPIC_CONFIRMATION, None, sender))
        thread.start()
