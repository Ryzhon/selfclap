"""タスクコマンド実装"""
from datetime import date
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from selfclap.database.queries import TaskQueries

app = typer.Typer(help="✅ タスク管理")
console = Console()


@app.command("add")
def add(
    title: str = typer.Argument(..., help="タスク名"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="説明"),
    priority: str = typer.Option("medium", "--priority", "-p", help="優先度 (low/medium/high)"),
):
    """タスクを追加"""
    db = TaskQueries()

    try:
        task = db.create_task(
            title=title,
            created_date=date.today(),
            description=description,
            priority=priority
        )
        console.print(f"✅ [green]タスクを追加しました![/green] (ID: {task.id})")
    except Exception as e:
        console.print(f"[red]エラー: {e}[/red]")


@app.command("list")
def list_tasks(
    all: bool = typer.Option(False, "--all", "-a", help="完了済みも含めて全て表示")
):
    """タスク一覧を表示"""
    db = TaskQueries()

    if all:
        tasks = db.get_all_tasks()
        title = "✅ タスク一覧（全て）"
    else:
        tasks = db.get_active_tasks()
        title = "✅ タスク一覧（未完了）"

    if not tasks:
        console.print("[yellow]タスクがありません[/yellow]")
        return

    table = Table(title=title)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("タイトル", style="white")
    table.add_column("状態", style="magenta")
    table.add_column("優先度", style="yellow")
    table.add_column("作成日", style="dim")

    for task in tasks:
        status_icon = {
            "todo": "⏳",
            "in_progress": "🔄",
            "done": "✅"
        }
        priority_icon = {
            "low": "🔵",
            "medium": "🟡",
            "high": "🔴"
        }

        table.add_row(
            str(task.id),
            task.title,
            f"{status_icon.get(task.status, '')} {task.status}",
            f"{priority_icon.get(task.priority, '')} {task.priority}",
            str(task.created_date)
        )

    console.print(table)
    console.print(f"\n[dim]合計: {len(tasks)}件[/dim]")


@app.command("done")
def done(
    task_id: int = typer.Argument(..., help="タスクID"),
    difficulty_before: Optional[int] = typer.Option(None, "--difficulty-before", "-b", help="開始時の難易度 (1-5)"),
    difficulty_after: Optional[int] = typer.Option(None, "--difficulty-after", "-a", help="完了時の難易度 (1-5)"),
    learning: Optional[str] = typer.Option(None, "--learning", "-l", help="学んだこと"),
    time_actual: Optional[float] = typer.Option(None, "--time", "-t", help="実際の所要時間（時間）"),
):
    """タスクを完了にする"""
    db = TaskQueries()

    # タスク存在確認
    task = db.get_task_by_id(task_id)
    if not task:
        console.print(f"[red]エラー: ID {task_id} のタスクが見つかりません[/red]")
        return

    if task.status == "done":
        console.print(f"[yellow]タスク {task_id} は既に完了しています[/yellow]")
        return

    # 完了処理
    task = db.complete_task(
        task_id=task_id,
        completed_date=date.today(),
        difficulty_before=difficulty_before,
        difficulty_after=difficulty_after,
        learnings=learning,
        time_actual=time_actual
    )

    console.print(f"✅ [green]タスクを完了しました![/green] \"{task.title}\"")

    # AI学び抽出プロンプト出力
    if not any([difficulty_before, difficulty_after, learning]):
        from selfclap.prompts.auto_classify import generate_task_learning_prompt
        from rich.panel import Panel

        learning_prompt = generate_task_learning_prompt(task.title, task_id)

        console.print("\n")
        console.print(Panel(
            learning_prompt,
            title="🤖 Claude Code: 学びの抽出をお願いします",
            border_style="yellow",
            subtitle="質問に答えて学びを記録してください"
        ))
    else:
        console.print("\n[dim]💡 学びの情報が含まれています[/dim]\n")


@app.command("delete")
def delete(
    task_id: int = typer.Argument(..., help="タスクID"),
    yes: bool = typer.Option(False, "--yes", "-y", help="確認をスキップ")
):
    """タスクを削除"""
    db = TaskQueries()

    # タスク存在確認
    task = db.get_task_by_id(task_id)
    if not task:
        console.print(f"[red]エラー: ID {task_id} のタスクが見つかりません[/red]")
        return

    # 確認
    if not yes:
        confirm = typer.confirm(f"タスク \"{task.title}\" を削除しますか?")
        if not confirm:
            console.print("[yellow]キャンセルしました[/yellow]")
            return

    # 削除
    if db.delete_task(task_id):
        console.print(f"✅ [green]タスクを削除しました[/green]")
    else:
        console.print(f"[red]削除に失敗しました[/red]")
