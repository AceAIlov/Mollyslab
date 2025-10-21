# API Reference

## Router Program
- **initialize(admin, oracle_authority, risk_threshold_bps)**
- **set_pause(paused)** [admin]
- **update_threshold(risk_threshold_bps)** [admin]
- **set_oracle_score(asset_mint, score_bps)** [oracle_authority]
- **mint_mandate(asset_mint, strategy, ttl_seconds)** [user]
- **revoke_mandate()** [user|admin]
- **veto_mandate()** [admin]

### Accounts
- `RouterState` — admin, oracle_authority, risk_threshold_bps, paused
- `OracleScore` — asset_mint, score_bps
- `Mandate` — user, asset_mint, strategy, expires_at

## Slab Program
- **initialize_slab(strategy)** [user]
- **execute_signal(confidence_bps, direction, notional, price)** [owner]
- **close_slab()** [owner]

### Accounts
- `SlabAccount` — owner, strategy, performance_pnl, last_signal_ts

## Events
- RouterInitialized, Paused, Unpaused, ThresholdUpdated, OracleScoreSet, MandateMinted, MandateRevoked
- SlabInitialized, SignalExecuted
