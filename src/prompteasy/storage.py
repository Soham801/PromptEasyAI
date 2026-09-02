from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from contextlib import closing
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
        with closing(self._connect()) as connection:
            with connection:
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
        with closing(self._connect()) as connection:
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
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                "INSERT INTO history(user_id, label, saved_at, analysis) VALUES (?, ?, ?, ?)",
                (user_id, label, saved_at, json.dumps(analysis)),
            )
        return self.list_history(user_id)

    def count_history(self) -> int:
        with closing(self._connect()) as connection:
            return connection.execute("SELECT COUNT(*) FROM history").fetchone()[0]

    def backup_to(self, destination: str) -> Path:
        """Create a consistent SQLite backup without interrupting normal reads."""
        destination_path = Path(destination)
        if self.path != ":memory:" and destination_path.resolve() == Path(self.path).resolve():
            raise ValueError("Backup destination must differ from the active database.")
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        with closing(self._connect()) as source, closing(sqlite3.connect(destination_path)) as target:
            source.backup(target)
        return destination_path

    def restore_from(self, source: str) -> Path:
        """Replace the active database atomically with a validated SQLite backup."""
        if self.path == ":memory:":
            raise ValueError("Cannot restore a file backup into an in-memory database.")

        source_path = Path(source)
        if not source_path.is_file():
            raise FileNotFoundError(f"Backup file does not exist: {source}")
        if source_path.resolve() == Path(self.path).resolve():
            raise ValueError("Restore source must differ from the active database.")

        database_path = Path(self.path)
        database_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: str | None = None
        file_descriptor: int | None = None
        try:
            file_descriptor, temporary_path = tempfile.mkstemp(
                prefix=f"{database_path.stem}-restore-",
                suffix=".db",
                dir=database_path.parent,
            )
            os.close(file_descriptor)
            file_descriptor = None
            Path(temporary_path).unlink()
            source_connection = sqlite3.connect(source_path)
            target_connection = sqlite3.connect(temporary_path)
            try:
                source_connection.backup(target_connection)
            finally:
                target_connection.close()
                source_connection.close()
            os.replace(temporary_path, database_path)
            temporary_path = None
        finally:
            if temporary_path:
                Path(temporary_path).unlink(missing_ok=True)
            if file_descriptor is not None:
                os.close(file_descriptor)
        self._initialize()
        return database_path

    def get_preferences(self, user_id: str) -> dict[str, str]:
        with closing(self._connect()) as connection:
            row = connection.execute("SELECT preferences_json FROM preferences WHERE user_id = ?", (user_id,)).fetchone()
        return {**DEFAULT_PREFERENCES, **json.loads(row["preferences_json"])} if row else dict(DEFAULT_PREFERENCES)

    def update_preferences(self, user_id: str, values: dict[str, str]) -> dict[str, str]:
        preferences = {**self.get_preferences(user_id), **values}
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                "INSERT INTO preferences(user_id, preferences_json) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET preferences_json = excluded.preferences_json",
                (user_id, json.dumps(preferences)),
            )
        return preferences