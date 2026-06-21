"""memory_store/memory.py – persistent memory abstraction.

Provides a `Memory` class that is compatible with the original API
(`add`, `list_all`, `get`, `delete`) while using the underlying
`MemoryStore` implementation for safe, corruption‑resistant storage.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

class MemoryStore:
    """
    Low‑level persistent store.  Each memory item is saved as a JSON
    file under ``MEMORY_DIR`` (defaults to the package directory).
    The store guarantees corruption‑safe loading: broken JSON is removed
    automatically.
    """
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = base_path or os.getenv("MEMORY_DIR", "memory_store")
        os.makedirs(self.base_path, exist_ok=True)

    def _path(self, memory_id: str) -> str:
        return os.path.join(self.base_path, f"{memory_id}.json")

    def add(self, payload: Dict[str, Any]) -> str:
        """Store *payload* under a new unique id and return the id."""
        memory_id = str(uuid.uuid4())
        record: Dict[str, Any] = {
            "id": memory_id,
            "payload": payload,
            "created": datetime.utcnow().isoformat(),
            "updated": datetime.utcnow().isoformat(),
        }
        with open(self._path(memory_id), "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False)
        return memory_id

    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the payload for *memory_id* or ``None`` if missing/corrupt."""
        if not os.path.exists(self._path(memory_id)):
            return None
        try:
            with open(self._path(memory_id), "r", encoding="utf-8") as f:
                data = json.load(f)
            # Basic corruption check
            if all(k in data for k in ("id", "payload", "created", "updated")):
                return data.get("payload")
        except (json.JSONDecodeError, OSError):
            # Remove broken file silently
            try:
                os.remove(self._path(memory_id))
            except OSError:
                pass
        return None

    def list_all(self) -> List[Dict[str, Any]]:
        """Return a list of all stored payloads, newest first."""
        records: List[Dict[str, Any]] = []
        for name in os.listdir(self.base_path):
            if not name.endswith(".json"):
                continue
            memory_id = name[:-5]
            payload = self.get(memory_id)
            if payload is not None:
                records.append(payload)
        records.sort(key=lambda x: x.get("created", ""), reverse=True)
        return records

    def delete(self, memory_id: str) -> bool:
        """Delete the file for *memory_id*; returns ``True`` if removed."""
        try:
            os.remove(self._path(memory_id))
            return True
        except OSError:
            return False


# Export the store instance and the Memory wrapper for compatibility.
store = MemoryStore()

class Memory:
    """Thin wrapper around the global ``store`` instance, matching the original API."""

    def __init__(self):
        self._store = store

    def add(self, payload: Dict[str, Any]) -> str:
        return self._store.add(payload)

    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(memory_id)

    def list_all(self) -> List[Dict[str, Any]]:
        return self._store.list_all()

    def delete(self, memory_id: str) -> bool:
        return self._store.delete(memory_id)

# Make the class importable as ``from memory_store import Memory``