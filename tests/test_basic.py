"""test_basic.py - ECHO-13 Foundation Tests

Verifies core engine and graph functionality.
"""

from echo13.engine import EngineConfig, Session
from echo13.graph import Node, SymbolGraph


class TestEngineConfig:
    """Tests for EngineConfig defaults and validation."""

    def test_default_values(self) -> None:
        config = EngineConfig()
        assert config.recursion_depth == 1
        assert config.mutation_rate == 0.0
        assert config.seed == 42
        assert config.enable_tracing is False

    def test_custom_values(self) -> None:
        config = EngineConfig(recursion_depth=5, mutation_rate=0.8, seed=99)
        assert config.recursion_depth == 5
        assert config.mutation_rate == 0.8
        assert config.seed == 99

    def test_invalid_depth_raises(self) -> None:
        try:
            EngineConfig(recursion_depth=0)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_invalid_rate_raises(self) -> None:
        try:
            EngineConfig(mutation_rate=1.5)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


class TestNode:
    """Tests for Node creation and identity."""

    def test_defaults(self) -> None:
        node = Node(label="a")
        assert node.label == "a"
        assert node.value == 0.0
        assert node.generation == 0
        assert node.mutated is True

    def test_custom_value(self) -> None:
        node = Node(label="b", value=3.14)
        assert node.value == 3.14

    def test_equality_by_label(self) -> None:
        a = Node(label="a", value=1.0)
        b = Node(label="a", value=9.9)
        assert a == b  # same label = same node


class TestSymbolGraph:
    """Tests for graph construction and queries."""

    def _make_linear_graph(self) -> tuple[SymbolGraph, Node, Node, Node]:
        graph = SymbolGraph()
        a = Node(label="a", value=1.0)
        b = Node(label="b", value=2.0)
        c = Node(label="c", value=3.0)
        graph.add_node(a)
        graph.add_node(b)
        graph.add_node(c)
        graph.add_edge(a, b)
        graph.add_edge(b, c)
        return graph, a, b, c

    def test_node_count(self) -> None:
        graph, *_ = self._make_linear_graph()
        assert len(graph.nodes) == 3

    def test_edge_count(self) -> None:
        graph, *_ = self._make_linear_graph()
        assert len(graph.edges) == 2

    def test_get_parents(self) -> None:
        graph, a, b, c = self._make_linear_graph()
        assert graph.get_parents(b) == [a]
        assert graph.get_parents(c) == [b]
        assert graph.get_parents(a) == []

    def test_get_children(self) -> None:
        graph, a, b, c = self._make_linear_graph()
        assert graph.get_children(a) == [b]
        assert graph.get_children(b) == [c]
        assert graph.get_children(c) == []

    def test_duplicate_node_raises(self) -> None:
        graph = SymbolGraph()
        graph.add_node(Node(label="a"))
        try:
            graph.add_node(Node(label="a"))
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


class TestSession:
    """Tests for session execution."""

    def test_basic_run_completes(self) -> None:
        config = EngineConfig(recursion_depth=1, mutation_rate=0.0, seed=42)
        graph = SymbolGraph()
        a = Node(label="a", value=1.0)
        b = Node(label="b", value=2.0)
        graph.add_node(a)
        graph.add_node(b)
        graph.add_edge(a, b)

        session = Session(config=config, graph=graph)
        session.run()

        assert a.generation == 1
        assert b.generation == 1

    def test_no_mutation_at_zero_rate(self) -> None:
        config = EngineConfig(recursion_depth=1, mutation_rate=0.0)
        graph = SymbolGraph()
        a = Node(label="a", value=5.0)
        graph.add_node(a)

        session = Session(config=config, graph=graph)
        session.run()

        assert a.mutated is False

    def test_tracing_produces_events(self) -> None:
        config = EngineConfig(
            recursion_depth=1, mutation_rate=0.0, enable_tracing=True
        )
        graph = SymbolGraph()
        a = Node(label="a", value=1.0)
        b = Node(label="b", value=2.0)
        graph.add_node(a)
        graph.add_node(b)
        graph.add_edge(a, b)

        session = Session(config=config, graph=graph)
        session.run()

        trace = session.get_trace()
        assert len(trace) == 2
        assert all(e["kind"] == "evaluate" for e in trace)

    def test_values_change_with_edges(self) -> None:
        config = EngineConfig(recursion_depth=1, mutation_rate=0.0)
        graph = SymbolGraph()
        a = Node(label="a", value=4.0)
        b = Node(label="b", value=2.0)
        graph.add_node(a)
        graph.add_node(b)
        graph.add_edge(a, b)

        session = Session(config=config, graph=graph)
        session.run()

        # b receives a's value: (2.0 + 4.0) / 2 = 3.0
        assert b.value == 3.0

    def test_multiple_passes(self) -> None:
        config = EngineConfig(recursion_depth=2, mutation_rate=0.0)
        graph = SymbolGraph()
        a = Node(label="a", value=1.0)
        graph.add_node(a)

        session = Session(config=config, graph=graph)
        session.run()

        assert a.generation == 2
