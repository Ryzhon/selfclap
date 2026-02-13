"""データベース接続管理"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator


class Database:
    """SQLiteデータベース接続管理クラス"""

    def __init__(self):
        self.db_path = Path.home() / ".selfclap" / "selfclap.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_if_needed()

    def _initialize_if_needed(self):
        """初回実行時にテーブルを作成"""
        if not self.db_path.exists():
            self._create_tables()

    def _create_tables(self):
        """テーブル作成"""
        with self.get_connection() as conn:
            conn.executescript("""
                -- 日記エントリテーブル
                CREATE TABLE IF NOT EXISTS diary_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE NOT NULL,
                    content TEXT NOT NULL,

                    -- 成長記録
                    learned_today TEXT,
                    compared_to_past TEXT,
                    invisible_growth TEXT,

                    -- 評価軸の分離
                    external_feedback TEXT,
                    self_assessment TEXT,

                    -- 感情・状態
                    mood TEXT,
                    energy_level INTEGER,

                    -- 困難度
                    challenges_faced TEXT,
                    how_overcome TEXT,

                    -- メタデータ
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_diary_date ON diary_entries(date DESC);
                CREATE INDEX IF NOT EXISTS idx_diary_mood ON diary_entries(mood);

                -- タスクテーブル
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'todo',
                    priority TEXT DEFAULT 'medium',

                    -- 成長記録
                    learnings TEXT,
                    difficulty_before INTEGER,
                    difficulty_after INTEGER,
                    time_estimated REAL,
                    time_actual REAL,

                    -- 比較データ
                    similar_task_before TEXT,
                    improvement_notes TEXT,

                    -- 外部評価
                    external_review TEXT,

                    -- メタデータ
                    created_date DATE NOT NULL,
                    completed_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status);
                CREATE INDEX IF NOT EXISTS idx_task_completed_date ON tasks(completed_date DESC);
                CREATE INDEX IF NOT EXISTS idx_task_created_date ON tasks(created_date DESC);
            """)

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """DB接続のコンテキストマネージャ"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
