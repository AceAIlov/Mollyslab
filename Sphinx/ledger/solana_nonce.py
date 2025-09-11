# Durable Nonce metadata helpers for offline Solana sending.
# Works without solana-py; if solana-py is present, online code can use the
# attached metadata to rebuild a proper advance-nonce + transfer transaction.

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

try:
    # Optional: only used at online broadcast time
    from solana.publickey import PublicKey  # type: ignore
    HAVE_SOLANA = True
except Exception:
    HAVE_SOLANA = False


@dataclass
class DurableNonceMeta:
    """
    Minimal data needed to reconstruct a durable-nonce transfer online.

    nonce_account:     base58 of the Nonce Account
    nonce_authority:   base58 of the signer that can advance the nonce
    nonce_value:       the current nonce value (blockhash-like string) captured
                       when composing offline; online sender should re-fetch/
                       validate and include `advanceNonceAccount` before submit.
    cluster:           devnet | mainnet-beta | custom label for routing
    """
    nonce_account: str
    nonce_authority: str
    nonce_value: str
    cluster: str = "devnet"

    def to_json(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"), ensure_ascii=False)

    @staticmethod
    def from_json(text: str) -> "DurableNonceMeta":
        data = json.loads(text)
        return DurableNonceMeta(**data)


def attach_nonce_metadata(outbox_payload: Dict[str, Any], meta: DurableNonceMeta) -> Dict[str, Any]:
    """
    Embed nonce metadata into a payload destined for the Outbox.

    The broadcaster (when online) reads this to rebuild a proper transaction
    that (1) uses the durable nonce as recentBlockhash, and (2) includes an
    `advanceNonceAccount` instruction authorized by `nonce_authority`.
    """
    out = dict(outbox_payload)
    out.setdefault("ledger", {})
    out["ledger"]["durable_nonce"] = asdict(meta)
    return out


def describe_nonce(meta: DurableNonceMeta) -> str:
    """
    Human-friendly string for audit/approval screens.
    """
    short = lambda s: f"{s[:4]}…{s[-4:]}" if len(s) > 10 else s
    return (
        f"Durable Nonce — account {short(meta.nonce_account)}, "
        f"authority {short(meta.nonce_authority)}, "
        f"value {short(meta.nonce_value)} on {meta.cluster}"
    )


def validate_nonce_fields(meta: DurableNonceMeta) -> None:
    """
    Lightweight structural checks so we fail fast offline.
    """
    for name, val in [
        ("nonce_account", meta.nonce_account),
        ("nonce_authority", meta.nonce_authority),
        ("nonce_value", meta.nonce_value),
    ]:
        if not isinstance(val, str) or not val.strip():
            raise ValueError(f"DurableNonceMeta.{name} is missing/invalid")

    if HAVE_SOLANA:
        # Best-effort base58 sanity (won't hit network)
        _ = PublicKey(meta.nonce_account)
        _ = PublicKey(meta.nonce_authority)
