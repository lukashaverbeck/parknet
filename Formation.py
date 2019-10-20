from Agent import Agent


class Formation:
    def __init__(self):
        """ initializes an empty formation of agents """

        self.__agents = []
        self.__longest = 0.0

    def calc_gap(self) -> float:
        """ calculates the minimal gap between two agents

        Returns:
            float: length of minimal gap rounded to 2 decimal places
        """
        
        number_of_agents = len(self.__agents)
        needed_space_proportion = 1.4
        needed_space = self.__longest * needed_space_proportion

        return round(needed_space / number_of_agents, 2)

    def add_agent(self, agent: Agent) -> None:
        """ adds an agent to the formation

        Args:
            agent (Agent): agent that is to be added
        """

        self.__agents.append(agent)

        if agent.length > self.__longest:
            self.__longest = agent.length

    def clear(self) -> None:
        """ resets the formation to its default values """

        self.__agents = []
        self.__longest = 0
