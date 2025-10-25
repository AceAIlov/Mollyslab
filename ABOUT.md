# About — MollySlab

**MollySlab** is a full-stack, open-source framework for running **AI trading agents on Solana and BNB** that **trade and bridge autonomously**.

## What it does
- **Agent → Signal → Safe Execution**  
  Off-chain AI (Claude or your model) proposes trades; on-chain programs enforce guardrails: short-lived **mandates**, **oracle-gated risk thresholds**, **confidence gates (≥85%)**, and **per-user execution slabs** with PnL + events.
- **Cross-chain / Bridging**  
  Agents can initiate cross-chain moves (e.g., SOL↔BNB) via pluggable bridges (Wormhole/LayerZero/etc.). The Router only authorizes bridging when policy checks pass; the Orchestrator performs the relay; the destination Slab validates confidence and executes.

## Why it’s different
- **Safety is on-chain** (not “best effort” off-chain): TTL mandates, risk thresholds, admin pause/veto, and confidence checks are hard program rules.  
- **Isolation by design:** each user’s Slab is a separate PDA/state sandbox (Solana) or mapping entry (BNB).  
- **Composability:** drop-in oracles (e.g., Pyth), DEX CPIs (Jupiter/Raydium on Solana; routers on BNB), MEV protections (Jito, TWAP/commit-reveal), and bridge adapters.  
- **Testnet-first:** spin up on Solana localnet/devnet and BNB testnet with fake funds; graduate to mainnet after audit.

## High-level flow
```mermaid
flowchart TD
  A[AI/Orchestrator] -->|Signal JSON| R[Router (policy)]
  R -->|Mandate (TTL, risk≥threshold)| S[Slab (exec & PnL)]
  A -->|Optionally: Bridge Request| B[Bridge Adapter]
  B -->|Cross-chain message & funds| S2[Slab on target chain]
  S & S2 -->|Events & PnL| M[Monitoring/Analytics]
