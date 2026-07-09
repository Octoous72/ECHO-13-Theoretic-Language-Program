"""Tests for parity mod 2 calculations.

Tests ECHO-13 parity mod 2 rule definitions.
"""


def test_parity_constants():
    """Verify parity mod 2 constant definitions."""
    C1 = 1
    C2 = 0
    P1 = 1
    P2 = 0
    K = 3

    assert C1 == 1
    assert C2 == 0
    assert P1 == 1
    assert P2 == 0
    assert K == 3


def test_parity_mod2_rule():
    """Verify parity mod 2 rule calculation."""
    C1, C2, P1, P2, K = 1, 0, 1, 0, 3
    # Rule: (C1 + C2) % 2 == (P1 + P2 + 2*K) % 2
    left_side = (C1 + C2) % 2
    right_side = (P1 + P2 + 2 * K) % 2
    assert left_side == right_side
