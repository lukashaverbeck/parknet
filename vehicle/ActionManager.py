import time
import json
import threading
from Communication import Communication


class ActionManager:
    """ coordinates the interactive behaviour of multiple agents by determining which agent is allowed to execute which
        action at what time
    """

    TOPIC_GLOBAL_ACTION_ACTIVE = "action/active-global"
    TOPIC_GLOBAL_ACTION_COMPLETED = "action/completed-global"

    WAIT_SEND_GLOBAL = 1
    WAIT_CHECK_PERMISSION = 1
    WAIT_VERIFY_FIRST_IN_QUEUE = 2

    def __init__(self, agent):
        """ initializes the action manager

            Args:
                agent (Agent): agent to take actions
        """

        self.__agent = agent
        self.__global_action = None
        self.__local_action = None
        self.__critical_error = False
        self.__communication = Communication.instance(self.__agent.get_id())

        # continuously send current global action
        send_thread = threading.Thread(target=self.update_global_action)
        send_thread.start()

        # continuously check if the agent is allowed to globally execute his local action
        check_thread = threading.Thread(target=self.check_global_permission)
        check_thread.start()

        self.__communication.subscribe(self.TOPIC_GLOBAL_ACTION_COMPLETED, self.receive_completion)
        self.__communication.subscribe(self.TOPIC_GLOBAL_ACTION_ACTIVE, self.receive_global_action)

    def update_global_action(self):
        """ continuously checks if the agent is currently taking an action and in this case sends it to every agent in
            the network
        """

        while True:
            if self.__global_action is not None:
                if self.__global_action.is_owner(self.__agent):
                    self.send_global_action()            

            time.sleep(self.WAIT_SEND_GLOBAL)

    def send_global_action(self):
        """ sends the current global action to every agent in the nework """

        action_data = self.__global_action.dumps()
        self.__communication.send(self.TOPIC_GLOBAL_ACTION_ACTIVE, action_data)

    def receive_global_action(self, message):
        """ handles the receivement of the currently globally executed action

            Args:
                message (Message): message wrapping the information about the current global action
        """

        action = Action.loads(message.content())
        self.__global_action = Action.choose(self.__global_action, action)

    def send_completion(self):
        """ informs every agent in the network that the global action the agent was taking has terminated """

        if not self.__global_action.is_owner(self.__agent):
            return

        self.__global_action = None
        self.__communication.send(self.TOPIC_GLOBAL_ACTION_COMPLETED, None)

    def receive_completion(self, message):
        """ handles the receivement of the information that the global action has terminated

            Args:
                message (Message): message wrapping the information
        """

        self.__global_action = None

    def check_global_permission(self):
        """ continuously checks if the agent is allowed to make its local agent it intents to take global and in this
            case executes this action
        """

        while True:
            if self.local_allowed_global():
                self.__global_action = self.__local_action
                self.send_global_action()

                time.sleep(self.WAIT_VERIFY_FIRST_IN_QUEUE)
                if not self.__global_action.is_owner(self.__agent):
                    continue

                self.__local_action = None

                self.execute_global_action()
            
            time.sleep(self.WAIT_CHECK_PERMISSION)

    def local_allowed_global(self):
        """ determines if the currently global action may be overwritten with the currently local action

            Returns:
                bool: True if the global action may be overwritten - otherwhise False
        """

        if self.__local_action is not None:
            if self.__global_action is None:
                return True
            elif self.__local_action.get_timestamp() < self.__local_action.get_timestamp():
                return True

        return False

    def execute_global_action(self):
        """ actually takes the global action by addressing the driver accordingly to the task of the global action """

        if self.__global_action is None:
            return

        if not self.__global_action.is_owner(self.__agent):
            return
        
        task = self.__global_action.get_task()

        # TODO implement execution of real tasks
        if task == "parking/enter":
            time.sleep(4)
        else:
            print(self.__agent.get_id(), "- do " + task + " with timestamp", self.__global_action.get_timestamp())
            time.sleep(4)

        print(self.__agent.get_id(), "finished task")
        self.__global_action = None
        self.send_completion()

    # -- setters --

    def set_local_action(self, task):
        self.__local_action = Action(task, self.__agent.get_id(), time.time())


class Action:
    """ helper class representing the state of an agent's behaviour """

    def __init__(self, task, agent_id, timestamp):
        """ initializes the action

            Args:
                task (str): type of the action
                agent_id (str): the agent's unique ID
                timestamp (float): time the action was initially set
        """

        self.__task = task
        self.__agent_id = agent_id
        self.__timestamp = timestamp

    def dumps(self):
        """ creates a dictionary representation of the action

            Returns:
                dict: action data
        """

        data = {
            "task": self.__task,
            "agent": self.__agent_id,
            "timestamp": self.__timestamp
        }

        return json.dumps(data)

    def equals(self, action):
        """ compares the action to another action

            Args:
                action (Action): action to be compared to

            Returns:
                bool: True if the actions contain the exact same data - otherwhise False
        """

        if action is None:
            return False
        elif not action.get_task() == self.__task:
            return False
        elif not action.get_agent_id() == self.__agent_id:
            return False
        elif not action.get_timestamp() == self.__timestamp():
            return False

        return True

    @staticmethod
    def loads(json_data):
        """ creates an Action object out of a JSON representation of an action

            Args:
                json_data (str): JSON String representing the action's data

            Returns:
                Action: Action object containing the given data
        """

        data = json.loads(json_data)

        assert "task" in json_data, "Action could not be loaded because the JSON data did not contain a task"
        assert "agent" in json_data, "Action could not be loaded because the JSON data did not contain a agent ID"
        assert "timestamp" in json_data, "Action could not be loaded because the JSON data did not contain a timestamp"

        return Action(data["task"], data["agent"], data["timestamp"])

    @staticmethod
    def choose(action1, action2):
        """ determines which action to choose out of multiple actions

            Args:
                action1 (Action): first action
                action2 (Action): second action

            Returns:
                Action: the latest action out of the two - if the actions have the exact same timestamp the action with
                        alphabetically lower agent ID is returned

                Note that if one of the actions is None, the other action is returned in every case
        """

        if action1 is None:
            return action2
        elif action2 is None:
            return action1
        elif action1.get_timestamp() < action2.get_timestamp():
            return action1
        elif action1.get_timestamp() == action2.get_timestamp():
            if action1.get_agent_id() < action2.get_agent_id():
                return action1
    
            return action2
    
        return action2

    def is_owner(self, agent):
        return agent.get_id() == self.__agent_id

    # -- getters --

    def get_task(self):
        return self.__task

    def get_agent_id(self):
        return self.__agent_id

    def get_timestamp(self):
        return self.__timestamp
