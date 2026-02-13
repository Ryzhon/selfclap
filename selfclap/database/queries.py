"""データベースクエリ実装"""
from datetime import date, datetime
from typing import List, Optional
from selfclap.database.connection import Database
from selfclap.database.models import DiaryEntry, Task


class DiaryQueries:
    """日記エントリのクエリ"""

    def __init__(self):
        self.db = Database()

    def create_entry(
        self,
        entry_date: date,
        content: str,
        **kwargs
    ) -> DiaryEntry:
        """日記エントリ作成"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO diary_entries (
                    date, content, learned_today, compared_to_past,
                    invisible_growth, external_feedback, self_assessment,
                    mood, energy_level, challenges_faced, how_overcome
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry_date,
                content,
                kwargs.get('learned_today'),
                kwargs.get('compared_to_past'),
                kwargs.get('invisible_growth'),
                kwargs.get('external_feedback'),
                kwargs.get('self_assessment'),
                kwargs.get('mood'),
                kwargs.get('energy_level'),
                kwargs.get('challenges_faced'),
                kwargs.get('how_overcome')
            ))
            entry_id = cursor.lastrowid

        return self.get_entry_by_id(entry_id)

    def get_entry_by_id(self, entry_id: int) -> Optional[DiaryEntry]:
        """ID指定でエントリ取得"""
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM diary_entries WHERE id = ?",
                (entry_id,)
            ).fetchone()

        if row:
            return self._row_to_entry(row)
        return None

    def get_entry_by_date(self, entry_date: date) -> Optional[DiaryEntry]:
        """日付指定でエントリ取得"""
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM diary_entries WHERE date = ?",
                (entry_date,)
            ).fetchone()

        if row:
            return self._row_to_entry(row)
        return None

    def get_entries_since(self, since_date: date) -> List[DiaryEntry]:
        """指定日以降のエントリ取得"""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM diary_entries WHERE date >= ? ORDER BY date DESC",
                (since_date,)
            ).fetchall()

        return [self._row_to_entry(row) for row in rows]

    def get_entries_by_mood(self, mood: str) -> List[DiaryEntry]:
        """気分でフィルタ"""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM diary_entries WHERE mood = ? ORDER BY date DESC",
                (mood,)
            ).fetchall()

        return [self._row_to_entry(row) for row in rows]

    def get_all_entries(self) -> List[DiaryEntry]:
        """全エントリ取得"""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM diary_entries ORDER BY date DESC"
            ).fetchall()

        return [self._row_to_entry(row) for row in rows]

    def update_entry(self, entry_date: date, **kwargs) -> Optional[DiaryEntry]:
        """エントリ更新（データ追記用）"""
        # 更新するフィールドを動的に構築
        update_fields = []
        values = []

        for field in ['learned_today', 'compared_to_past', 'invisible_growth',
                      'external_feedback', 'self_assessment', 'mood',
                      'energy_level', 'challenges_faced', 'how_overcome']:
            if field in kwargs and kwargs[field] is not None:
                update_fields.append(f"{field} = ?")
                values.append(kwargs[field])

        if not update_fields:
            return self.get_entry_by_date(entry_date)

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(entry_date)

        with self.db.get_connection() as conn:
            conn.execute(
                f"UPDATE diary_entries SET {', '.join(update_fields)} WHERE date = ?",
                values
            )

        return self.get_entry_by_date(entry_date)

    def _row_to_entry(self, row) -> DiaryEntry:
        """SQLiteのRowをDiaryEntryに変換"""
        return DiaryEntry(
            id=row['id'],
            date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
            content=row['content'],
            learned_today=row['learned_today'],
            compared_to_past=row['compared_to_past'],
            invisible_growth=row['invisible_growth'],
            external_feedback=row['external_feedback'],
            self_assessment=row['self_assessment'],
            mood=row['mood'],
            energy_level=row['energy_level'],
            challenges_faced=row['challenges_faced'],
            how_overcome=row['how_overcome'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )


class TaskQueries:
    """タスクのクエリ"""

    def __init__(self):
        self.db = Database()

    def create_task(
        self,
        title: str,
        created_date: date,
        **kwargs
    ) -> Task:
        """タスク作成"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO tasks (
                    title, description, status, priority, created_date,
                    learnings, difficulty_before, difficulty_after,
                    time_estimated, time_actual, similar_task_before,
                    improvement_notes, external_review
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title,
                kwargs.get('description'),
                kwargs.get('status', 'todo'),
                kwargs.get('priority', 'medium'),
                created_date,
                kwargs.get('learnings'),
                kwargs.get('difficulty_before'),
                kwargs.get('difficulty_after'),
                kwargs.get('time_estimated'),
                kwargs.get('time_actual'),
                kwargs.get('similar_task_before'),
                kwargs.get('improvement_notes'),
                kwargs.get('external_review')
            ))
            task_id = cursor.lastrowid

        return self.get_task_by_id(task_id)

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """ID指定でタスク取得"""
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?",
                (task_id,)
            ).fetchone()

        if row:
            return self._row_to_task(row)
        return None

    def get_active_tasks(self) -> List[Task]:
        """未完了タスク取得"""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE status != 'done' ORDER BY created_date DESC"
            ).fetchall()

        return [self._row_to_task(row) for row in rows]

    def get_all_tasks(self) -> List[Task]:
        """全タスク取得"""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY created_date DESC"
            ).fetchall()

        return [self._row_to_task(row) for row in rows]

    def get_completed_tasks_since(self, since_date: date) -> List[Task]:
        """指定日以降の完了タスク取得"""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE status = 'done' AND completed_date >= ? ORDER BY completed_date DESC",
                (since_date,)
            ).fetchall()

        return [self._row_to_task(row) for row in rows]

    def complete_task(self, task_id: int, completed_date: date, **kwargs) -> Optional[Task]:
        """タスク完了"""
        update_fields = ["status = 'done'", "completed_date = ?", "updated_at = CURRENT_TIMESTAMP"]
        values = [completed_date]

        for field in ['learnings', 'difficulty_before', 'difficulty_after',
                      'time_actual', 'external_review']:
            if field in kwargs and kwargs[field] is not None:
                update_fields.append(f"{field} = ?")
                values.append(kwargs[field])

        values.append(task_id)

        with self.db.get_connection() as conn:
            conn.execute(
                f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?",
                values
            )

        return self.get_task_by_id(task_id)

    def delete_task(self, task_id: int) -> bool:
        """タスク削除"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0

    def _row_to_task(self, row) -> Task:
        """SQLiteのRowをTaskに変換"""
        return Task(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            status=row['status'],
            priority=row['priority'],
            learnings=row['learnings'],
            difficulty_before=row['difficulty_before'],
            difficulty_after=row['difficulty_after'],
            time_estimated=row['time_estimated'],
            time_actual=row['time_actual'],
            similar_task_before=row['similar_task_before'],
            improvement_notes=row['improvement_notes'],
            external_review=row['external_review'],
            created_date=datetime.strptime(row['created_date'], '%Y-%m-%d').date() if row['created_date'] else None,
            completed_date=datetime.strptime(row['completed_date'], '%Y-%m-%d').date() if row['completed_date'] else None,
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )
