from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


DEFAULT_PREFERENCES = {"tone": "neutral", "audience": "general", "domain": "general"}


class Storage:
    def __init__(self, path: str):
        self.path = path
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    label TEXT NOT NULL,
                    saved_at TEXT NOT NULL,
                    analysis TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS history_user_id ON history(user_id);
                CREATE TABLE IF NOT EXISTS preferences (
                    user_id TEXT PRIMARY KEY,
                    preferences_json TEXT NOT NULL
                );
                """
            )

    def list_history(self, user_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, label, saved_at, analysis FROM history "
                "WHERE user_id = ? ORDER BY id DESC",
                (user_id,),
            ).fetchall()
        return [
            {"id": row["id"], "label": row["label"], "saved_at": row["saved_at"], "analysis": json.loads(row["analysis"])}
            for row in rows
        ]

    def save_history(self, user_id: str, label: str, saved_at: str, analysis: dict[str, Any]) -> list[dict[str, Any]]:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO history(user_id, label, saved_at, analysis) VALUES (?, ?, ?, ?)",
                (user_id, label, saved_at, json.dumps(analysis)),
            )
        return self.list_history(user_id)

    def count_history(self) -> int:
        with self._connect() as connection:
            return connection.execute("SELECT COUNT(*) FROM history").fetchone()[0]

    def get_preferences(self, user_id: str) -> dict[str, str]:
        with self._connect() as connection:
            row = connection.execute("SELECT preferences_json FROM preferences WHERE user_id = ?", (user_id,)).fetchone()
        return {**DEFAULT_PREFERENCES, **json.loads(row["preferences_json"])} if row else dict(DEFAULT_PREFERENCES)

    def update_preferences(self, user_id: str, values: dict[str, str]) -> dict[str, str]:
        preferences = {**self.get_preferences(user_id), **values}
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO preferences(user_id, preferences_json) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET preferences_json = excluded.preferences_json",
                (user_id, json.dumps(preferences)),
            )
        return preferences