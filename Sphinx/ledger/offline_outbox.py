# Offline Outbox — encrypted queue for signed payloads (e.g., Solana tx)
from __future__ import annotations

import base64
import json
import os
import time
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from cryptography.fernet import Fernet  # pyproject includes cryptography
except Exception:  # fallback: plaintext (still functional, not encrypted)
    Fernet = None  # type: ignore


def _mkdirp(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _load_or_create_key(path: Path) -> Optional[bytes]:
    if Fernet is None:
        return None
    _mkdirp(path.parent)
    if path.exists():
        return path.read_bytes()
    key = Fernet.generate_key()
    path.write_bytes(key)
    os.chmod(path, 0o600)
    return key


@dataclass
class QueueItem:
    id: str
    kind: str  # e.g., "sol_tx"
    created_at: float  # utc epoch seconds
    payload_b64: str   # encrypted or plain b64
    metadata: Dict[str, Any]


class Outbox:
    """
    Disk-backed, append-only queue. Each item is a JSON file (optionally encrypted).
    """
    def __init__(
        self,
        base_dir: Optional[Path] = None,
        key_path: Optional[Path] = None,
        box_name: str = "outbox",
    ):
        home = Path(os.environ.get("SPHINX_HOME", Path.home() / ".sphinx"))
        self.root = base_dir or (home / box_name)
        self.sent = self.root / "sent"
        self.err = self.root / "error"
        self.keys = Path(os.environ.get("SPHINX_KEYS", home / "keys"))
        self.key_path = key_path or (self.keys / "outbox.key")
        _mkdirp(self.root)
        _mkdirp(self.sent)
        _mkdirp(self.err)
        self._fernet: Optional[Fernet] = None
        key = _load_or_create_key(self.key_path)
        if Fernet is not None and key:
            self._fernet = Fernet(key)

    def _enc(self, raw: bytes) -> bytes:
        if self._fernet:
            return self._fernet.encrypt(raw)
        return raw

    def _dec(self, enc: bytes) -> bytes:
        if self._fernet:
            return self._fernet.decrypt(enc)
        return enc

    def add(self, kind: str, payload: bytes, metadata: Optional[Dict[str, Any]] = None) -> str:
        qid = uuid.uuid4().hex
        created_at = time.time()
        body = self._enc(payload)
        item = QueueItem(
            id=qid,
            kind=kind,
            created_at=created_at,
            payload_b64=base64.b64encode(body).decode("ascii"),
            metadata=metadata or {},
        )
        path = self.root / f"{created_at:.6f}__{qid}__{kind}.json"
        path.write_text(json.dumps(asdict(item), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        return qid

    def _iter_paths(self, kind: Optional[str] = None) -> List[Path]:
        items = sorted(self.root.glob("*.json"), key=lambda p: p.name)
        if kind:
            items = [p for p in items if p.name.endswith(f"__{kind}.json")]
        return items

    def list(self, kind: Optional[str] = None) -> List[QueueItem]:
        out: List[QueueItem] = []
        for p in self._iter_paths(kind):
            data = json.loads(p.read_text(encoding="utf-8"))
            out.append(QueueItem(**data))
        return out

    def pop_next(self, kind: Optional[str] = None) -> Optional[QueueItem]:
        paths = self._iter_paths(kind)
        if not paths:
            return None
        p = paths[0]
        data = json.loads(p.read_text(encoding="utf-8"))
        p.unlink(missing_ok=True)
        return QueueItem(**data)

    def decode_payload(self, item: QueueItem) -> bytes:
        enc = base64.b64decode(item.payload_b64.encode("ascii"))
        return self._dec(enc)

    def mark_sent(self, item: QueueItem, receipt: Dict[str, Any]) -> None:
        path = self.sent / f"{item.created_at:.6f}__{item.id}__{item.kind}.json"
        payload = asdict(item)
        payload["receipt"] = receipt
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def mark_error(self, item: QueueItem, error_msg: str) -> None:
        path = self.err / f"{item.created_at:.6f}__{item.id}__{item.kind}.json"
        payload = asdict(item)
        payload["error"] = error_msg
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
