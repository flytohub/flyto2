# Refactor

Refactors here should improve the distribution control plane without absorbing product source.

Good targets include:

- simplifying product/release schemas;
- reducing duplicate release metadata;
- centralizing verification logic;
- making channel promotion atomic and auditable;
- improving deterministic release indexes;
- clarifying source/distribution ownership.

Do not move Flow, Runtime, Agent Firewall, or other product implementation into this repository as part of a refactor.
