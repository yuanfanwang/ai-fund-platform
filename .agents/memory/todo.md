# Current Task

## Question

Assess whether `zkTLS` or homomorphic encryption can support a strategy marketplace where creator-submitted strategies must actually be executed according to the declared strategy, especially across DEX, CEX, FX, and equities.

## Plan

- [x] Separate the proof problem from the execution-enforcement problem
- [x] Compare DEX vs CEX/FX/equities execution trust models
- [x] Recommend an MVP architecture and a long-term architecture

## Review

- `zkTLS` / `zkFetch` fit proving external API facts and broker/exchange receipts, but not enforcing future strategy-faithful execution by themselves.
- `FHE` is not the right primitive for custody or venue interaction; it is useful for computation on encrypted data, not for proving orders hit the market as intended.
- For `DEX`, enforceability is realistic through smart contracts and on-chain vault logic.
- For `CEX`, `FX`, and equities, the best achievable model today is restricted custody plus attested execution plus auditable broker receipts, not full trustlessness.
- Recommended product path: start with verified performance + signal marketplace, then add DEX-native vaults, and only later consider managed-account execution for TradFi venues.
