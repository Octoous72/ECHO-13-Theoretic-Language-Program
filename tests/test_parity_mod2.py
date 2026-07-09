# tests/parity_mod2.echo13
define echo C1 = 1
define echo C2 = 0
define echo P1 = 1
define echo P2 = 0
define echo K  = 3

rule parity_mod2
    (C1 + C2) % 2 == (P1 + P2 + 2*K) % 2
