"""データモデル定義"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class DiaryEntry:
    """日記エントリ"""
    id: Optional[int]
    date: date
    content: str

    # 成長記録
    learned_today: Optional[str] = None
    compared_to_past: Optional[str] = None
    invisible_growth: Optional[str] = None

    # 評価軸の分離
    external_feedback: Optional[str] = None
    self_assessment: Optional[str] = None

    # 感情・状態
    mood: Optional[str] = None
    energy_level: Optional[int] = None

    # 困難度
    challenges_faced: Optional[str] = None
    how_overcome: Optional[str] = None

    # メタデータ
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Task:
    """タスク"""
    id: Optional[int]
    title: str
    description: Optional[str] = None
    status: str = 'todo'
    priority: str = 'medium'

    # 成長記録
    learnings: Optional[str] = None
    difficulty_before: Optional[int] = None
    difficulty_after: Optional[int] = None
    time_estimated: Optional[float] = None
    time_actual: Optional[float] = None

    # 比較データ
    similar_task_before: Optional[str] = None
    improvement_notes: Optional[str] = None

    # 外部評価
    external_review: Optional[str] = None

    # メタデータ
    created_date: Optional[date] = None
    completed_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
