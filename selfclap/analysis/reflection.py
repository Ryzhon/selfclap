"""振り返りモード用のデータ生成"""
from datetime import date, timedelta
from typing import Dict, List, Any
from selfclap.database.queries import DiaryQueries, TaskQueries


def generate_reflection_data() -> Dict[str, Any]:
    """振り返り用データを生成"""
    diary_db = DiaryQueries()
    task_db = TaskQueries()

    today = date.today()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)

    # 現在の状態
    recent_entries = diary_db.get_entries_since(last_7_days)
    recent_moods = [e.mood for e in recent_entries if e.mood]
    recent_tasks = task_db.get_completed_tasks_since(last_7_days)

    # 他人の評価を集計
    external_feedback_list = [
        e.external_feedback for e in recent_entries
        if e.external_feedback
    ]

    # 自己評価を集計
    self_assessment_list = [
        e.self_assessment for e in recent_entries
        if e.self_assessment
    ]

    # 過去の成長記録
    all_entries = diary_db.get_all_entries()
    learned_items = [e.learned_today for e in all_entries if e.learned_today]
    compared_items = [e.compared_to_past for e in all_entries if e.compared_to_past]
    invisible_growth_items = [e.invisible_growth for e in all_entries if e.invisible_growth]

    # タスクの難易度変化分析
    completed_tasks = task_db.get_completed_tasks_since(last_30_days)
    difficulty_improvements = []
    for task in completed_tasks:
        if task.difficulty_before and task.difficulty_after:
            improvement = task.difficulty_before - task.difficulty_after
            if improvement > 0:
                difficulty_improvements.append({
                    "task": task.title,
                    "before": task.difficulty_before,
                    "after": task.difficulty_after,
                    "improvement": improvement
                })

    # 学びの蓄積
    task_learnings = [t.learnings for t in completed_tasks if t.learnings]

    # データ不足チェック
    data_gaps = check_data_gaps(all_entries, completed_tasks)

    return {
        "current_state": {
            "recent_moods": recent_moods,
            "recent_tasks_completed": len(recent_tasks),
            "streak": calculate_streak(diary_db)
        },
        "external_vs_internal": {
            "external_feedback": external_feedback_list,
            "self_assessment": self_assessment_list,
            "learned_count": len(learned_items),
            "compared_count": len(compared_items),
            "invisible_growth_count": len(invisible_growth_items)
        },
        "visible_vs_invisible_growth": {
            "visible": {
                "external_recognition": len([f for f in external_feedback_list if "良い" in f or "素晴らしい" in f])
            },
            "invisible": {
                "learned_items": learned_items[-5:] if learned_items else [],
                "compared_items": compared_items[-5:] if compared_items else [],
                "invisible_growth": invisible_growth_items[-5:] if invisible_growth_items else [],
                "difficulty_improvements": difficulty_improvements[:5]
            }
        },
        "learning_accumulation": {
            "total_diary_learnings": len(learned_items),
            "total_task_learnings": len(task_learnings),
            "recent_learnings": (learned_items[-5:] if learned_items else []) + (task_learnings[-5:] if task_learnings else [])
        },
        "past_comparison": {
            "total_entries": len(all_entries),
            "total_tasks_completed": len(task_db.get_all_tasks()),
            "comparison_records": compared_items[-5:] if compared_items else []
        },
        "data_gaps": data_gaps
    }


def calculate_streak(diary_db: DiaryQueries) -> int:
    """連続記録日数を計算"""
    streak = 0
    current = date.today()

    while True:
        entry = diary_db.get_entry_by_date(current)
        if entry:
            streak += 1
            current -= timedelta(days=1)
        else:
            break

    return streak


def check_data_gaps(entries: List, tasks: List) -> Dict[str, List[str]]:
    """データ不足をチェック"""
    gaps = {
        "missing_fields": [],
        "suggestions": []
    }

    # 日記のデータ不足チェック
    entries_without_learning = [e for e in entries if not e.learned_today]
    if len(entries_without_learning) > len(entries) * 0.5:
        gaps["missing_fields"].append("learned_today")
        gaps["suggestions"].append(
            f"{len(entries_without_learning)}件の日記に「学んだこと」が未記入です"
        )

    entries_without_comparison = [e for e in entries if not e.compared_to_past]
    if len(entries_without_comparison) > len(entries) * 0.7:
        gaps["missing_fields"].append("compared_to_past")
        gaps["suggestions"].append(
            f"{len(entries_without_comparison)}件の日記に「過去と比べてできたこと」が未記入です"
        )

    # タスクのデータ不足チェック
    tasks_without_learning = [t for t in tasks if t.status == 'done' and not t.learnings]
    if len(tasks_without_learning) > 0:
        gaps["missing_fields"].append("task_learnings")
        gaps["suggestions"].append(
            f"{len(tasks_without_learning)}個の完了タスクに「学び」が未記入です"
        )

    tasks_without_difficulty = [t for t in tasks if t.status == 'done' and not (t.difficulty_before and t.difficulty_after)]
    if len(tasks_without_difficulty) > 0:
        gaps["missing_fields"].append("task_difficulty")
        gaps["suggestions"].append(
            f"{len(tasks_without_difficulty)}個の完了タスクに「難易度」が未記入です"
        )

    return gaps
