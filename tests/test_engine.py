import math
from echo13 import Entity, Pair, Braid, Environment, soft_overlap_compression


def step_entities(entities, pairs, braid_map, env, dt=0.1, directions=None):
    """Perform one engine step following the reference order in echo13.py

    entities: list of Entity instances
    pairs: list of Pair instances
    braid_map: dict mapping Pair -> Braid (by instance)
    env: Environment
    directions: dict of entity_id -> (dx, dy)
    """
    if directions is None:
        directions = {e.id: (1, 0) for e in entities}
    # motion
    for e in entities:
        dx, dy = directions.get(e.id, (1, 0))
        x, y = e.position
        new_pos = (x + e.tempo * dx * dt, y + e.tempo * dy * dt)
        e.position = new_pos
        e.trace.append(new_pos)
        e.phase += 0.01 * dt
    # relational harmonize
    for pair in pairs:
        if pair.distance() < 1.0:
            pair.harmonize()
    # braids
    for pair in pairs:
        b = braid_map.get(pair)
        if b is not None:
            b.update()
    # environment
    for b in braid_map.values():
        env.update(b)
    # SOR
    for pair in pairs:
        soft_overlap_compression(pair.A, pair.B)


def run_full(steps=50):
    A = Entity("A", tempo=0.4, density=0.7, phase=0, position=(0, 0))
    B = Entity("B", tempo=0.38, density=0.8, phase=0, position=(0.2, 0))
    pair = Pair(A, B)
    braid = Braid(pair)
    env = Environment()
    braid_map = {pair: braid}
    for _ in range(steps):
        step_entities([A, B], [pair], braid_map, env)
    return A, B, pair, braid, env


def test_deterministic_run():
    A1, B1, pair1, braid1, env1 = run_full(steps=100)
    A2, B2, pair2, braid2, env2 = run_full(steps=100)
    # Compare final numeric state
    assert A1.position == A2.position
    assert B1.position == B2.position
    assert math.isclose(A1.density, A2.density, rel_tol=1e-12)
    assert math.isclose(B1.density, B2.density, rel_tol=1e-12)
    assert braid1.crossings == braid2.crossings
    assert math.isclose(env1.echo, env2.echo, rel_tol=1e-12)


def test_soft_overlap_increases_density():
    # Create two entities that will overlap traces completely
    A = Entity("A", tempo=0.1, density=0.5, phase=0, position=(0,0))
    B = Entity("B", tempo=0.1, density=0.5, phase=0, position=(0,0))
    pair = Pair(A, B)
    braid = Braid(pair)
    env = Environment()
    # Move them with identical directions so traces overlap fully
    for _ in range(20):
        step_entities([A,B], [pair], {pair: braid}, env, dt=0.1, directions={"A":(1,0),"B":(1,0)})
    # call SOR explicitly with low threshold to force growth
    soft_overlap_compression(A, B, threshold=0.0)
    assert A.density > 0.5
    assert B.density > 0.5


def test_trace_append_only():
    A = Entity("A", tempo=0.2, density=0.6, phase=0, position=(0,0))
    initial_len = len(A.trace)
    for _ in range(10):
        step_entities([A], [], {}, Environment(), dt=0.1, directions={"A":(0.5,0.3)})
    assert len(A.trace) >= initial_len + 10
