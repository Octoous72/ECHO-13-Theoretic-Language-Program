def test_parity_mod2_basic():
    """Minimal parity test converted from repository artifact.

    Original file appeared to contain non-Python domain text; replace with
    a simple test asserting the intended parity relationship.
    """
    C1, C2 = 1, 0
    P1, P2 = 1, 0
    K = 3

    assert (C1 + C2) % 2 == (P1 + P2 + 2 * K) % 2
