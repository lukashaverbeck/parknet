from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, TypedDict

import attributes
import interaction
import sensing
import util


class _Member:
    class Dictionary(TypedDict):
        signature: str
        delta: float
        filing: Optional[float]

    def encode(self) -> _Member.Dictionary:
        """ Creates a dictionary representation of the member.

        The representation contains the member's signature, delta and filing date.

        Returns:
            The dictionary representation of the member.
        """

        return {
            'signature': self.signature,
            'delta': self.delta,
            'filing': None if self.filing is None else self.filing.timestamp()
        }

    @staticmethod
    def decode(member: _Member.Dictionary) -> _Member:
        """ Creates a member from a given dictionary representation of that message.

        The json representation must contain the member's signature, delta and filing.

        Args:
            member: Dictionary representation of the member.

        Returns:
            The member represented by the dictionary.
        """

        return _Member(
            member['signature'],
            member['delta'],
            None if member['filing'] is None else datetime.fromtimestamp(member['filing'])
        )

    @staticmethod
    def agent(filing: bool = False):
        """ Creates a member that represents the main agent.

        Args:
            filing: Boolean whether the main agent is intending to leave the parking lane.

        Returns:
            The main agent member.
        """

        return _Member(attributes.SIGNATURE, attributes.DELTA, datetime.now() if filing else None)

    def __init__(self, signature: str, delta: float, filing: Optional[datetime]):
        self.signature: str = signature
        self.delta: float = delta
        self.filing: datetime = filing

    def __repr__(self):
        return f"Agent[#{self.signature}, δ: {self.delta}{util.const.Units.DISTANCE}]"

    def __eq__(self, other: _Member):
        return self.signature == other.signature

    def __hash__(self):
        return hash(self.signature)


class _MemberRelation:
    class Dictionary(TypedDict):
        member: _Member.Dictionary
        ahead_signature: Optional[str]

    def encode(self) -> _MemberRelation.Dictionary:
        """ Creates a dictionary representation of the member relation.

        The representation contains the member relation's member and ahead signature.
        The member is therefore also dictionary encoded.

        Returns:
            The dictionary representation of the member relation.
        """

        return {
            'member': self.member.encode(),
            'ahead_signature': self.ahead_signature
        }

    @staticmethod
    def decode(member_relation: _MemberRelation.Dictionary) -> _MemberRelation:
        """ Creates a member relation from a given dictionary representation of that member relation.

        The json representation must contain the member relation's member and ahead signature.

        Args:
            member_relation: Dictionary representation of the member relation.

        Returns:
            The member relation represented by the dictionary.
        """

        return _MemberRelation(_Member.decode(member_relation['member']), member_relation['ahead_signature'])

    def __init__(self, member: _Member, ahead_signature: Optional[str]):
        self.member: _Member = member
        self.ahead_signature: Optional[str] = ahead_signature


class _RelationGraph:
    def __init__(self):
        self.vertices: Dict[str, _Member] = {}
        self.edges: Dict[str, Optional[str]] = {}

    def add(self, member_relation: _MemberRelation) -> None:
        """ Adds the relation of two members to the graph.

        The primary (behind) member is added as a vertex. The secondary (ahead) member is not added as a vertex.
        The relation between both members is represented as a new directed edge from the primary member to the secondary
        member. In the case that there already is an edge leaving the primary member vertex, this edge is overwritten as
        there may only be one emanating edge per vertex.

        Args:
            member_relation: Relation between the primary (behind) member and the secondary (ahead) member.
        """

        member = member_relation.member  # primary member
        ahead_signature = member_relation.ahead_signature  # signature of the secondary member

        # _add primary member as a vertex and the relation between the primary and the secondary member as an edge
        self.vertices[member.signature] = member
        self.edges[member.signature] = ahead_signature

    def max_linear_transitivities(self) -> List[List[_Member]]:
        """ Traces all linear transitivities of maximum length.

        A linear transitivity is of maximum length exactly if it starts from a starting agent.

        See Also:
            For reference regarding linear transitivities and starting members:
                - ``def _linear_transitivity(...)``
                - ``def _is_starting_agent(...)``

        Returns:
            A list of all maximum linear transitivities.
        """

        linear_transitivities = []  # list of maximum linear transitivities to be traced
        starting_agents = self._starting_vertices()  # get starting vertices to start tracing

        # get every maximum linear transitivity by tracing from every starting agent
        for starting_agent in starting_agents:
            # get maximum linear transitivity starting from starting agent
            transitivity = self._linear_transitivity(starting_agent)

            # _add maximum linear transitivity to list
            linear_transitivities.append(transitivity)

        return linear_transitivities

    def _linear_transitivity(self, starting_member: _Member) -> List[_Member]:
        """ Traces a linear transitivity starting from a given vertex member.

        A linear transitivity is a non-cyclical path starting from a given vertex member.
        A vertex member is a member that is represented as a vertex in the graph. This is exactly the case if the member
        has demonstrated to be willing to be part of a formation by sharing his front agent (or ``None`` if there is
        none).

        Args:
            starting_member: Vertex member to start the linear transitivity from.

        Returns:
            The transitivity list starting from the given vertex member.

        Raises:
            AssertionError: If the given starting member is not a vertex member.
            AssertionError: If there is a cyclical transitivity.
        """

        # starting member must be a vertex member
        assert starting_member.signature in self.vertices, f"Starting member {starting_member} must be a vertex member."

        reversed_edges = self._reversed_edges()  # edges linking from secondary (ahead) agent to primary (behind) agent
        transitivity_list = [starting_member]  # every linear transitivity contains at least the starting member

        # trace directed relations between the agents by traversing the edges starting from the starting member
        member = starting_member
        while member.signature in reversed_edges:
            # get linked member (the agent in front of the current member)
            behind = reversed_edges[member.signature]
            member = self._vertex_member(behind)

            # a linear transitivity must not contain cycles
            assert member not in transitivity_list, f"Found cycle in linear transitivity {transitivity_list}."

            # _add member to linear transitivity list
            transitivity_list.append(member)

        return transitivity_list

    def _is_starting_vertex(self, member: _Member) -> bool:
        """ Determines whether a given member is a vertex that is not linking to another vertex member.

        A member is exactly if a starting vertex if the member
            - is a vertex and
            - either has no front agent or has a front agent that is not a vertex.

        Notes:
            A vertex with an emanating edge can still be a starting vertex. This is exactly the case if the linked
            member is not a vertex in the graph. This handling is necessary because the simple fact that a primary agent
            identifies a secondary agent as its front agent does not mean that this front agent is also part of the same
            formation as the primary agent. The secondary agent first has to communicate its ability and willingness to
            be part of a formation at all by sharing his front agent (or ``None`` if there is none) itself.

        Args:
            member: The member to be checked.

        Returns:
            Boolean whether the member is a starting vertex.
        """

        # check if the member is a vertex (has communicated his front agent)
        if member.signature in self.edges:
            # check if the member has no front agent
            if (ahead := self.edges[member.signature]) is None:
                return True
            # check if the member's front agent is not a vertex (has not communicated his front agent)
            elif ahead not in self.edges:
                return True

        return False

    def _starting_vertices(self) -> List[_Member]:
        """ Gets every vertex member that is a starting member.

        See Also:
            For Reference regarding starting vertices:
                - ``@def _is_starting_vertex(...)``

        Returns:
            List of all starting member.
        """

        # filter starting vertices from vertex members
        return [member for member in self.vertices.values() if self._is_starting_vertex(member)]

    def _reversed_edges(self) -> Dict[str, str]:
        """ Reverses the direction of the edges by switching keys with values of ``vertices``.

        Vertices that are linked to ``None`` are not included in the resulting edged.

        Returns:
            Dictionary representing the reversed directed edges.
        """

        return {ahead: behind for behind, ahead in self.edges.items() if ahead is not None}

    def _vertex_member(self, signature: str) -> _Member:
        """ Gets vertex agent by it's signature.

        Args:
            signature: Signature of the vertex member.

        Returns:
            The vertex member.

        Raises:
            AssertionError: If there is no vertex member with the given signature.
        """

        # vertex member must be in vertices
        assert signature in self.vertices, f"Agent #{signature} is no vertex member."

        return self.vertices[signature]

    def __repr__(self):
        return repr(self.edges)


@util.Singleton
class Formation(interaction.Communication):
    @property
    def delta_max(self) -> float:
        return max(member.delta for member in self)

    def __init__(self):
        super().__init__()
        self.agents: List[_Member] = []
        self._scanner = sensing.Scanner()
        self._relation_graph: _RelationGraph = _RelationGraph()

        self._subscribe(interaction.Communication.Topics.FORMATION, self._handle_member_relation)

    def update(self, filing: bool = False) -> None:
        """ Updates the member relation graph by adding and sharing main agent's member relation.

        Args:
            filing: Boolean whether the main agent is intending to leave the parking lane.
        """

        # create the main agent's member relation containing the front agent signature and the main agent Member
        ahead_signature = self._scanner.ahead_signature
        member = _Member.agent(filing)
        member_relation = _MemberRelation(member, ahead_signature)

        # add and share the member relation
        self._add(member_relation)
        self._send(interaction.Communication.Topics.FORMATION, member_relation.encode())

    def _add(self, member_relation: _MemberRelation) -> None:
        self._relation_graph.add(member_relation)
        self._update_agents()

    def _update_agents(self) -> None:
        agents = [_Member.agent()]

        for max_linear_transitivity in self._relation_graph.max_linear_transitivities():
            if any(member.signature == attributes.SIGNATURE for member in max_linear_transitivity):
                agents = max_linear_transitivity

        self.agents = agents

    def _handle_member_relation(self, message: interaction.Message[_MemberRelation.Dictionary]) -> None:
        """ Handles an incoming member relation message by updating the formation member relation.

        Args:
            message: Incoming member relation message.
        """

        # decode message and add it to the graph
        member_relation = _MemberRelation.decode(message.content)
        self._add(member_relation)

    def __eq__(self, other: Formation):
        return self.agents == other.agents

    def __iter__(self):
        yield from self.agents

    def __len__(self):
        return len(self.agents)

    def __contains__(self, item: _Member):
        return item in self.agents

    def __getitem__(self, key: int):
        return self.agents[key]

    def __repr__(self):
        return f"Formation{self.agents}"
