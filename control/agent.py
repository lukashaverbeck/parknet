from __future__ import annotations

import time
from typing import Callable

import attributes
import control
import interaction
import util

_MIN_DELAY: float = 0.2
_MAX_DELAY: float = 4
_DELAY_STEPS: int = 8


def _action(function: Callable[[MainAgent], None]):
    """ Decorator managing the ``standby`` state of the main agent.

    This function wraps and returns a function that calls a driving ``function``. Before executing the action the main
    agent is activated. Afterwards the main agent is deactivated. This sets the ``standby`` state of the main agent
    which is necessary to ensure that state updates to the main agent are timed correctly.

    Notes:
        This function is intended to be used as a decorator for driving functions of the main agent.

    Args:
        function: Function executing a driving action.

    Returns:
        Wrapper function calling the decorated function and handling the main agent's ``standby`` state.
    """

    def wrapper(agent: MainAgent):
        agent.activate()  # activate agent  -> standby = False
        function(agent)  # execute action
        agent.deactivate()  # deactivate agent -> standby = True

    return wrapper


@util.SingleUse
class MainAgent(interaction.Communication):
    @property
    def minimum_distance(self) -> float:
        number_agents = len(self._formation)
        assert number_agents > 0, f"A formation must always contain at least one agent but {self._formation} does not."

        return self._formation.delta_max / number_agents + util.const.Driving.SAFETY_DISTANCE

    def __init__(self):
        super().__init__()
        self._standby: bool = True
        self._formation: interaction.Formation = interaction.Formation()
        self._driver: control.Driver = control.Driver()
        self._current_state_hash: int = hash(self)

        self._run()

    @util.stabilized_concurrent(util.const.ThreadNames.MAIN_AGENT_ACTION, _MIN_DELAY, _MAX_DELAY, _DELAY_STEPS, False)
    def _run(self) -> bool:
        """ Concurrently updates the agent's state.

        The state of the agent is only updated if there is no action.
        This is to ensure that the formation remains coherent and complete for every agent in the formation while an
        action is executed.

        Notes:
            This method runs concurrently with dynamic delays.

        See Also:
            For reference regarding updating the state:
                - ``def _update_state(...)``
                - ``def _state_hash_stable(...)``

        Returns:
            Boolean whether the execution was stable which is the case exactly if the state of the agent did not change.
        """

        # if there is currently no action to perform, update the state
        if self._standby:
            self._update_state()

        return self._state_hash_stable()

    def _update_state(self) -> None:
        """ Updates the agents state updating its formation.

        See Also:
            For reference regarding updating the formation:
                - ``def Formation.update(...)``
        """

        # update formation
        self._formation.update()

    def _state_hash_stable(self) -> bool:
        """ Update the current state hash and determines whether it has remained the same since the last update.

        See Also:
            For reference regarding the calculation of the state hash:
                - ``def __hash__(self)``

        Returns:
            Boolean whether the state hash has remained the same.
        """

        old_state_hash = self._current_state_hash  # temporarily store the current state hash
        self._current_state_hash = hash(self)  # update the current state hash

        # return whether the state hash has remained the same
        return self._current_state_hash == old_state_hash

    def activate(self):
        """ Sets ``self._standby`` to ``False`` """

        self._standby = False

    def deactivate(self):
        """ Sets ``self._standby`` to ``True`` """

        self._standby = True

    # TODO: address driver to leave parking lot
    @_action
    def leave(self):
        pass

    @_action
    def create_space(self) -> None:
        """ Creates space for a leaving agent.

        In order to do so, the main agent moves up in the according direction until the agent has left the formation.
        After the leaving agent finished the leaving process, the main agent minimizes the space again.

        See Also:
            For reference regarding minimizing space:
                - def minimize_space(...)
        """

        # get the leaving agent from the formation
        filing_member = self._formation.filing_member

        # only create space if the leaving agent is part of the same formation
        if not filing_member:
            return

        # initially the leaving process is running
        process_running = True

        def on_process_finish(message: interaction.Message) -> None:
            """ Flags the leaving process as finished.

            This should be called when a nearby driving process is finished.
            The process is only flagged if the process was finished by the leaving agent.

            Args:
                message: Message sent to confirm that a driving process was finished.
            """

            nonlocal process_running
            process_running = not message.sender == filing_member.signature

        # listen for finished processes to determine when the leaving agent left the parking lane
        self.subscribe(interaction.Communication.Topics.PROCESS_FINISHED, on_process_finish)

        # drive in the matching direction as long as the leaving agent has not yet finished the process
        comes_before = self._formation.comes_before(attributes.SIGNATURE, filing_member.signature)  # get direction
        direction = self._driver.forward if comes_before else self._driver.backward  # get driving mode
        direction.do_while(lambda: process_running)  # drive

        # minimize space after waiting for other agents closer to the leaving agent
        delay = self._formation.distance(attributes.SIGNATURE, filing_member.signature)  # determine prior distance
        time.sleep(delay)  # wait an according amount of time
        self.minimize_space()  # start minimizing the space again

    # TODO: address driver to minimize the distance to the next agent
    @_action
    def minimize_space(self):
        pass

    def __hash__(self):
        return hash(repr(self._formation))
