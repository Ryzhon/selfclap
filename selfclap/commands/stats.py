"""統計ダッシュボードコマンド実装"""
from datetime import date, timedelta
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from selfclap.database.queries import DiaryQueries, TaskQueries

app = typer.Typer(help="📊 統計ダッシュボード")
console = Console()


@app.command()
def show(
    days: int = typer.Option(30, "--days", "-d", help="集計期間（日数）"),
):
    """統計情報を表示"""
    diary_db = DiaryQueries()
    task_db = TaskQueries()

    # 期間設定
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    # データ取得
    all_entries = diary_db.get_all_entries()
    entries_in_period = [e for e in all_entries if start_date <= e.date <= end_date]

    all_tasks = task_db.get_all_tasks()
    completed_tasks = [t for t in all_tasks if t.status == "done"]
    completed_in_period = [t for t in completed_tasks if t.completed_date and start_date <= t.completed_date <= end_date]

    # === 基本統計 ===
    console.print(f"\n[bold cyan]📊 統計ダッシュボード[/bold cyan] [dim]（過去{days}日間）[/dim]\n")

    basic_stats = Table(show_header=False, box=None, padding=(0, 2))
    basic_stats.add_column("項目", style="cyan")
    basic_stats.add_column("値", style="bold white")

    basic_stats.add_row("📝 日記エントリ数", f"{len(entries_in_period)}件")
    basic_stats.add_row("✅ タスク完了数", f"{len(completed_in_period)}件")

    if entries_in_period:
        days_with_entries = len(set([e.date for e in entries_in_period]))
        continuation_rate = (days_with_entries / days) * 100
        basic_stats.add_row("📅 日記記録日数", f"{days_with_entries}日 ({continuation_rate:.1f}%)")

    console.print(Panel(basic_stats, title="基本統計", border_style="cyan"))

    # === 気分の推移 ===
    moods = [e.mood for e in entries_in_period if e.mood]
    if moods:
        mood_count = {}
        for mood in moods:
            mood_count[mood] = mood_count.get(mood, 0) + 1

        mood_table = Table(title="😊 気分の分布")
        mood_table.add_column("気分", style="magenta")
        mood_table.add_column("回数", style="white")
        mood_table.add_column("割合", style="cyan")

        mood_emoji = {
            "happy": "😊",
            "neutral": "😐",
            "tired": "😴",
            "stressed": "😰",
            "frustrated": "😤",
            "anxious": "😟"
        }

        for mood, count in sorted(mood_count.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(moods)) * 100
            emoji = mood_emoji.get(mood, "")
            mood_table.add_row(f"{emoji} {mood}", str(count), f"{percentage:.1f}%")

        console.print(mood_table)
        console.print()

    # === 成長データの充実度 ===
    growth_stats = Table(title="🌱 成長データの充実度")
    growth_stats.add_column("項目", style="cyan")
    growth_stats.add_column("記録数", style="white")
    growth_stats.add_column("記録率", style="green")

    total_entries = len(entries_in_period) if entries_in_period else 1  # ゼロ除算回避

    learned_count = len([e for e in entries_in_period if e.learned_today])
    compared_count = len([e for e in entries_in_period if e.compared_to_past])
    invisible_count = len([e for e in entries_in_period if e.invisible_growth])
    external_count = len([e for e in entries_in_period if e.external_feedback])
    self_eval_count = len([e for e in entries_in_period if e.self_assessment])

    growth_stats.add_row(
        "📚 学んだこと",
        f"{learned_count}件",
        f"{(learned_count/total_entries)*100:.1f}%"
    )
    growth_stats.add_row(
        "📈 過去との比較",
        f"{compared_count}件",
        f"{(compared_count/total_entries)*100:.1f}%"
    )
    growth_stats.add_row(
        "🌱 見えない成長",
        f"{invisible_count}件",
        f"{(invisible_count/total_entries)*100:.1f}%"
    )
    growth_stats.add_row(
        "👥 他人の評価",
        f"{external_count}件",
        f"{(external_count/total_entries)*100:.1f}%"
    )
    growth_stats.add_row(
        "🪞 自己評価",
        f"{self_eval_count}件",
        f"{(self_eval_count/total_entries)*100:.1f}%"
    )

    console.print(growth_stats)
    console.print()

    # === タスクの難易度変化 ===
    difficulty_improvements = []
    for task in completed_in_period:
        if task.difficulty_before and task.difficulty_after:
            improvement = task.difficulty_before - task.difficulty_after
            difficulty_improvements.append({
                "task": task.title,
                "before": task.difficulty_before,
                "after": task.difficulty_after,
                "improvement": improvement
            })

    if difficulty_improvements:
        diff_table = Table(title="📊 理解度の向上（難易度の変化）")
        diff_table.add_column("タスク", style="white", max_width=40)
        diff_table.add_column("開始時", style="yellow", justify="center")
        diff_table.add_column("完了時", style="green", justify="center")
        diff_table.add_column("改善度", style="cyan", justify="center")

        for item in sorted(difficulty_improvements, key=lambda x: x["improvement"], reverse=True)[:10]:
            improvement_str = f"+{item['improvement']}" if item['improvement'] > 0 else str(item['improvement'])
            if item['improvement'] > 0:
                improvement_display = f"[green]{improvement_str}[/green]"
            elif item['improvement'] < 0:
                improvement_display = f"[red]{improvement_str}[/red]"
            else:
                improvement_display = "[dim]0[/dim]"

            diff_table.add_row(
                item['task'][:40],
                str(item['before']),
                str(item['after']),
                improvement_display
            )

        console.print(diff_table)
        console.print()

        # 平均改善度
        avg_improvement = sum([d['improvement'] for d in difficulty_improvements]) / len(difficulty_improvements)
        if avg_improvement > 0:
            console.print(f"[green]✨ 平均改善度: +{avg_improvement:.2f}[/green]")
            console.print("[dim]タスクを通じて着実に理解度が向上しています！[/dim]\n")
        elif avg_improvement < 0:
            console.print(f"[yellow]📝 平均改善度: {avg_improvement:.2f}[/yellow]")
            console.print("[dim]実際にやってみると想定より難しかったようです。それも学びです。[/dim]\n")

    # === データ充実度アドバイス ===
    if entries_in_period:
        avg_growth_rate = (learned_count + compared_count + invisible_count) / (total_entries * 3) * 100

        if avg_growth_rate < 30:
            console.print(Panel(
                """[yellow]💡 成長データの記録率が低めです[/yellow]

日記を書く時に、以下の情報も記録すると振り返りがより効果的になります:
• 学んだこと（--learned）
• 過去との比較（--compared）
• 見えない成長（--invisible）

例:
```bash
clap diary write "今日の内容" --learned "学んだこと" --compared "過去との比較"
```
""",
                border_style="yellow",
                title="💡 アドバイス"
            ))
