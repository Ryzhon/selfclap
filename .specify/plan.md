# SelfClap 実装計画

## 技術スタック

### 言語・ランタイム
- **Python 3.10+**
  - 理由: 豊富なライブラリ、型ヒント、標準ライブラリのSQLite
  - 新卒エンジニアにも馴染みやすい

### コアライブラリ

#### CLI フレームワーク
- **Typer 0.23.0+**
  - 理由: モダンで使いやすい、型ヒントベース、自動ヘルプ生成
  - サブコマンド構造が直感的
  - Rich との統合

#### ターミナルUI
- **Rich 14.3.2+**
  - 理由: 美しいターミナル出力、テーブル、パネル、進捗表示
  - カラー表示、マークダウンレンダリング
  - カレンダー表示に使用

#### グラフ可視化
- **Plotille 6.0.4+**
  - 理由: ASCII グラフ、軽量、依存少ない
  - ターミナルで動作

#### データベース
- **SQLite3（標準ライブラリ）**
  - 理由: サーバー不要、ファイルベース、十分な性能
  - Python 標準搭載、追加インストール不要

#### 設定管理
- **PyYAML 6.0.3+**
  - 理由: 人間が読み書きしやすい設定ファイル
  - オプション機能で使用

#### 日付・時刻
- **python-dateutil 2.9.0+**
  - 理由: 柔軟な日付解析、タイムゾーン対応

## アーキテクチャ設計

### ディレクトリ構造

```
selfclap/
├── selfclap/
│   ├── __init__.py
│   ├── cli.py              # Typer CLI エントリポイント
│   ├── commands/           # コマンド実装
│   │   ├── __init__.py
│   │   ├── diary.py        # 日記コマンド
│   │   ├── task.py         # タスクコマンド
│   │   ├── stats.py        # 統計コマンド
│   │   └── mentor.py       # メンターモード
│   ├── database/           # データベース層
│   │   ├── __init__.py
│   │   ├── connection.py   # DB接続管理
│   │   ├── models.py       # データモデル
│   │   └── queries.py      # クエリ実装
│   ├── visualization/      # 可視化
│   │   ├── __init__.py
│   │   ├── dashboard.py    # 統計ダッシュボード
│   │   ├── calendar.py     # 継続カレンダー
│   │   └── graphs.py       # グラフ
│   ├── analysis/           # メンターモード分析
│   │   ├── __init__.py
│   │   ├── patterns.py     # 思考パターン分析
│   │   └── mentor_data.py  # メンターデータ生成
│   └── utils/              # ユーティリティ
│       ├── __init__.py
│       ├── config.py       # 設定管理
│       └── date_utils.py   # 日付ヘルパー
├── tests/
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_commands.py
│   └── test_analysis.py
├── .specify/               # Speckit ファイル
├── .claude/                # Claude Code 統合
├── README.md
├── requirements.txt
├── setup.py
└── .gitignore
```

### データベーススキーマ

```sql
-- 日記エントリテーブル
CREATE TABLE diary_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE NOT NULL,              -- YYYY-MM-DD
    content TEXT NOT NULL,                  -- 日記本文
    mood TEXT,                              -- happy, neutral, tired, stressed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_diary_date ON diary_entries(date DESC);
CREATE INDEX idx_diary_mood ON diary_entries(mood);

-- タスクテーブル
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,                    -- タスク名
    description TEXT,                       -- 詳細説明
    status TEXT DEFAULT 'todo',             -- todo, in_progress, done
    priority TEXT DEFAULT 'medium',         -- low, medium, high
    created_date DATE NOT NULL,             -- 作成日
    completed_date DATE,                    -- 完了日
    estimated_hours REAL,                   -- 予定工数
    actual_hours REAL,                      -- 実績工数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_task_status ON tasks(status);
CREATE INDEX idx_task_completed_date ON tasks(completed_date DESC);
CREATE INDEX idx_task_created_date ON tasks(created_date DESC);

-- 統計キャッシュテーブル（任意・パフォーマンス向上用）
CREATE TABLE stats_cache (
    date DATE PRIMARY KEY,
    tasks_completed INTEGER DEFAULT 0,
    diary_written BOOLEAN DEFAULT FALSE,
    mood TEXT,
    streak_count INTEGER DEFAULT 0,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stats_date ON stats_cache(date DESC);
```

### データモデル設計

```python
# selfclap/database/models.py
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

@dataclass
class DiaryEntry:
    id: Optional[int]
    date: date
    content: str
    mood: Optional[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class Task:
    id: Optional[int]
    title: str
    description: Optional[str]
    status: str  # todo, in_progress, done
    priority: str  # low, medium, high
    created_date: date
    completed_date: Optional[date]
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    created_at: datetime
    updated_at: datetime

@dataclass
class MentorData:
    """メンターモードで使用するデータ"""
    current_state: dict
    similar_past_situations: list
    success_patterns: list
    thought_patterns: dict
    encouragement_points: list
```

## CLI コマンド設計

### コマンド構造

```bash
clap                          # ルートコマンド
├── diary                     # 日記管理
│   ├── write <content>       # 日記を書く
│   ├── show [date]           # 日記を表示
│   └── list [--month N]      # 日記一覧
├── task                      # タスク管理
│   ├── add <title>           # タスク追加
│   ├── list [--all]          # タスク一覧
│   ├── done <id>             # タスク完了
│   ├── delete <id>           # タスク削除
│   └── update <id>           # タスク更新
├── stats                     # 統計ダッシュボード
├── calendar [--month N]      # 継続カレンダー
├── mentor                    # メンターモード
└── init                      # 初期化（任意）
```

### コマンド実装例

```python
# selfclap/cli.py
import typer
from rich.console import Console

app = typer.Typer(
    name="clap",
    help="誰も拍手してくれないなら、自分で拍手しよう",
    add_completion=False
)

console = Console()

# サブコマンドグループ
from selfclap.commands import diary, task, stats, mentor

app.add_typer(diary.app, name="diary", help="日記管理")
app.add_typer(task.app, name="task", help="タスク管理")

@app.command()
def stats():
    """統計ダッシュボードを表示"""
    from selfclap.visualization.dashboard import show_dashboard
    show_dashboard()

@app.command()
def calendar(month: int = typer.Option(None, "--month", "-m")):
    """継続カレンダーを表示"""
    from selfclap.visualization.calendar import show_calendar
    show_calendar(month)

@app.command()
def mentor():
    """メンターモード - 過去のデータから励まし"""
    from selfclap.commands.mentor import run_mentor_mode
    run_mentor_mode()
```

### 日記コマンド実装

```python
# selfclap/commands/diary.py
import typer
from datetime import date
from rich.console import Console
from selfclap.database.queries import DiaryQueries

app = typer.Typer()
console = Console()

@app.command("write")
def write(
    content: str = typer.Argument(..., help="日記の内容"),
    mood: str = typer.Option(None, "--mood", "-m", help="気分 (happy/neutral/tired/stressed)")
):
    """日記を書く"""
    db = DiaryQueries()
    entry = db.create_entry(date.today(), content, mood)
    console.print(f"✅ [green]日記を保存しました![/green] (ID: {entry.id})")

@app.command("show")
def show(target_date: str = typer.Argument(None, help="日付 (YYYY-MM-DD)")):
    """日記を表示"""
    from selfclap.utils.date_utils import parse_date

    d = parse_date(target_date) if target_date else date.today()
    db = DiaryQueries()
    entry = db.get_entry_by_date(d)

    if entry:
        console.print(f"\n[bold]{entry.date}[/bold]")
        if entry.mood:
            mood_emoji = {"happy": "😊", "neutral": "😐", "tired": "😴", "stressed": "😰"}
            console.print(f"気分: {mood_emoji.get(entry.mood, '')} {entry.mood}")
        console.print(f"\n{entry.content}\n")
    else:
        console.print(f"[yellow]{d} の日記はありません[/yellow]")

@app.command("list")
def list_entries(month: int = typer.Option(None, "--month", "-m")):
    """日記一覧を表示"""
    db = DiaryQueries()
    entries = db.get_entries(month=month)

    if not entries:
        console.print("[yellow]日記がありません[/yellow]")
        return

    from rich.table import Table
    table = Table(title="日記一覧")
    table.add_column("日付", style="cyan")
    table.add_column("気分", style="magenta")
    table.add_column("内容（抜粋）", style="white")

    for entry in entries:
        mood = entry.mood or "-"
        preview = entry.content[:50] + "..." if len(entry.content) > 50 else entry.content
        table.add_row(str(entry.date), mood, preview)

    console.print(table)
```

### メンターモード実装

```python
# selfclap/commands/mentor.py
from rich.console import Console
from rich.panel import Panel
import yaml
from selfclap.analysis.mentor_data import generate_mentor_data

console = Console()

def run_mentor_mode():
    """メンターモード実行"""
    console.print("\n[bold cyan]🤝 メンターモード[/bold cyan]\n")
    console.print("過去のデータを分析しています...\n")

    # メンターデータ生成
    mentor_data = generate_mentor_data()

    # YAML形式で出力（Claude Codeが読み取る）
    yaml_output = yaml.dump(
        mentor_data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False
    )

    console.print(Panel(
        yaml_output,
        title="📊 メンターデータ",
        subtitle="Claude Code がこのデータを参考に励まします"
    ))

    console.print("\n[dim]💡 Claude Code に「このデータを見て励まして」と伝えてください[/dim]\n")
```

### メンターデータ分析実装

```python
# selfclap/analysis/mentor_data.py
from datetime import date, timedelta
from selfclap.database.queries import DiaryQueries, TaskQueries
from collections import Counter
import re

def generate_mentor_data() -> dict:
    """メンターモード用のデータを生成"""
    diary_db = DiaryQueries()
    task_db = TaskQueries()

    today = date.today()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)

    # 現在の状態
    recent_entries = diary_db.get_entries_since(last_7_days)
    recent_moods = [e.mood for e in recent_entries if e.mood]
    recent_tasks = task_db.get_completed_tasks_since(last_7_days)
    completion_rate = len(recent_tasks) / 7.0

    # 過去の似た状況
    stressed_entries = diary_db.get_entries_by_mood("stressed")
    tired_entries = diary_db.get_entries_by_mood("tired")

    similar_situations = []
    for entry in (stressed_entries + tired_entries)[-5:]:
        # その後の回復を探す
        recovery = diary_db.get_entries_after(entry.date, limit=3)
        if recovery:
            similar_situations.append({
                "date": str(entry.date),
                "mood": entry.mood,
                "content": entry.content[:100],
                "recovery": [
                    {"date": str(r.date), "content": r.content[:100]}
                    for r in recovery if r.mood in ["happy", "neutral"]
                ]
            })

    # 成功パターン
    total_tasks = task_db.get_completed_tasks_since(last_30_days)
    success_patterns = [
        f"過去30日で{len(total_tasks)}個のタスク完了",
        f"最長連続記録: {calculate_longest_streak()}日",
    ]

    # 思考パターン分析
    all_entries = diary_db.get_all_entries()
    all_text = " ".join([e.content for e in all_entries])

    # 頻出する悩みキーワード
    worry_keywords = ["遅い", "できない", "難しい", "わからない", "失敗"]
    recurring_worries = [kw for kw in worry_keywords if kw in all_text]

    # 励ましポイント
    streak = calculate_current_streak()
    encouragement = [
        f"現在{streak}日連続で記録継続中" if streak > 0 else "新しいスタート!",
        f"過去7日で{len(recent_tasks)}個のタスクを完了"
    ]

    return {
        "current_state": {
            "recent_mood": recent_moods,
            "recent_completion_rate": round(completion_rate, 2),
            "streak_status": f"{streak}日連続"
        },
        "similar_past_situations": similar_situations,
        "success_patterns": success_patterns,
        "thought_patterns": {
            "recurring_worries": recurring_worries,
            "total_entries": len(all_entries)
        },
        "encouragement_points": encouragement
    }

def calculate_current_streak() -> int:
    """現在の連続記録日数を計算"""
    db = DiaryQueries()
    streak = 0
    current = date.today()

    while True:
        entry = db.get_entry_by_date(current)
        if entry:
            streak += 1
            current -= timedelta(days=1)
        else:
            break

    return streak

def calculate_longest_streak() -> int:
    """最長連続記録日数を計算"""
    db = DiaryQueries()
    all_entries = db.get_all_entries()

    if not all_entries:
        return 0

    dates = sorted([e.date for e in all_entries])
    max_streak = 1
    current_streak = 1

    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1

    return max_streak
```

## データベース実装

```python
# selfclap/database/connection.py
import sqlite3
from pathlib import Path
from contextlib import contextmanager

class Database:
    def __init__(self):
        self.db_path = Path.home() / ".selfclap" / "selfclap.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_if_needed()

    def _initialize_if_needed(self):
        """初回実行時にテーブル作成"""
        if not self.db_path.exists():
            self._create_tables()

    def _create_tables(self):
        """テーブル作成"""
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS diary_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE NOT NULL,
                    content TEXT NOT NULL,
                    mood TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_diary_date ON diary_entries(date DESC);
                CREATE INDEX IF NOT EXISTS idx_diary_mood ON diary_entries(mood);

                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'todo',
                    priority TEXT DEFAULT 'medium',
                    created_date DATE NOT NULL,
                    completed_date DATE,
                    estimated_hours REAL,
                    actual_hours REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status);
                CREATE INDEX IF NOT EXISTS idx_task_completed_date ON tasks(completed_date DESC);
            """)

    @contextmanager
    def get_connection(self):
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
```

## 可視化実装

```python
# selfclap/visualization/dashboard.py
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from selfclap.database.queries import DiaryQueries, TaskQueries
from datetime import date, timedelta

console = Console()

def show_dashboard():
    """統計ダッシュボード表示"""
    diary_db = DiaryQueries()
    task_db = TaskQueries()

    today = date.today()
    this_month_start = date(today.year, today.month, 1)

    # データ取得
    month_entries = diary_db.get_entries_since(this_month_start)
    month_tasks = task_db.get_completed_tasks_since(this_month_start)
    streak = calculate_current_streak()

    # ダッシュボード作成
    dashboard = Table.grid(padding=1)
    dashboard.add_column(style="cyan", justify="right")
    dashboard.add_column(style="white")

    dashboard.add_row("📅 現在の連続記録:", f"{streak}日")
    dashboard.add_row("📝 今月の日記:", f"{len(month_entries)}件")
    dashboard.add_row("✅ 今月の完了タスク:", f"{len(month_tasks)}個")

    if len(month_tasks) > 0:
        avg_tasks = len(month_tasks) / today.day
        dashboard.add_row("⏱️  1日平均タスク:", f"{avg_tasks:.1f}個")

    # 気分分布
    moods = [e.mood for e in month_entries if e.mood]
    if moods:
        from collections import Counter
        most_common = Counter(moods).most_common(1)[0]
        mood_emoji = {"happy": "😊", "neutral": "😐", "tired": "😴", "stressed": "😰"}
        dashboard.add_row(
            "😊 最も多い気分:",
            f"{mood_emoji.get(most_common[0], '')} {most_common[0]} ({most_common[1]}回)"
        )

    console.print(Panel(
        dashboard,
        title="[bold cyan]📊 あなたの統計[/bold cyan]",
        border_style="cyan"
    ))
```

## テスト戦略

### ユニットテスト

```python
# tests/test_database.py
import pytest
from datetime import date
from selfclap.database.queries import DiaryQueries

def test_create_diary_entry():
    db = DiaryQueries()
    entry = db.create_entry(date.today(), "テスト日記", "happy")
    assert entry.id is not None
    assert entry.content == "テスト日記"
    assert entry.mood == "happy"

def test_get_entry_by_date():
    db = DiaryQueries()
    today = date.today()
    db.create_entry(today, "今日の日記", None)

    entry = db.get_entry_by_date(today)
    assert entry is not None
    assert entry.content == "今日の日記"
```

## パフォーマンス最適化

- データベースインデックス適用
- 統計計算結果のキャッシング
- クエリの最適化（N+1問題回避）
- 起動時間100ms以下を目標

## エラーハンドリング

```python
# 例: データベースエラー
try:
    entry = db.create_entry(...)
except sqlite3.IntegrityError:
    console.print("[red]エラー: 同じ日付の日記が既に存在します[/red]")
except Exception as e:
    console.print(f"[red]エラーが発生しました: {e}[/red]")
```

## デプロイ・配布

### PyPI公開（将来的）
```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

### 開発インストール
```bash
pip install -e .
```

## まとめ

この実装計画により、SelfClap は:
- ✅ シンプルで保守しやすいアーキテクチャ
- ✅ Claude Code とシームレスに統合
- ✅ メンタルヘルスを守るメンターモード
- ✅ 高速でローカル完結
- ✅ 拡張しやすいモジュラー設計

を実現します。
