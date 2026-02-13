"""カレンダー表示コマンド実装"""
from datetime import date, timedelta
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from selfclap.database.queries import DiaryQueries

app = typer.Typer(help="📅 カレンダー")
console = Console()


@app.command()
def show(
    month: Optional[int] = typer.Option(None, "--month", "-m", help="月を指定 (1-12)"),
    year: Optional[int] = typer.Option(None, "--year", "-y", help="年を指定"),
):
    """日記記録カレンダーを表示（継続ストリーク表示）"""
    diary_db = DiaryQueries()

    # 期間設定
    today = date.today()
    if year and month:
        target_year = year
        target_month = month
    elif month:
        target_year = today.year
        target_month = month
    else:
        target_year = today.year
        target_month = today.month

    # 月の最初と最後の日
    first_day = date(target_year, target_month, 1)

    # 次の月の1日を取得して1日引く（月の最終日）
    if target_month == 12:
        last_day = date(target_year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(target_year, target_month + 1, 1) - timedelta(days=1)

    # 日記エントリ取得
    all_entries = diary_db.get_all_entries()
    entry_dates = set([e.date for e in all_entries])

    # カレンダー生成
    console.print(f"\n[bold cyan]📅 日記カレンダー[/bold cyan] [dim]{target_year}年{target_month}月[/dim]\n")

    # 曜日ヘッダー
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    header = "  ".join([f"[bold]{day}[/bold]" for day in weekdays])
    console.print(f"  {header}")

    # カレンダー本体
    current_date = first_day
    # 月の最初の日の曜日を取得（月曜日=0, 日曜日=6）
    start_weekday = (first_day.weekday()) % 7  # 月曜始まり

    calendar_lines = []
    week_line = ["  "] * start_weekday

    while current_date <= last_day:
        has_entry = current_date in entry_dates
        is_today = current_date == today

        if has_entry:
            # 日記あり - 記号を追加
            if is_today:
                day_str = f"[bold green]★{current_date.day:1d}[/bold green]"
            else:
                day_str = f"[bold green]●{current_date.day:1d}[/bold green]"
        else:
            # 日記なし
            if is_today:
                day_str = f"[bold yellow]▶{current_date.day:1d}[/bold yellow]"
            else:
                day_str = f"[dim]{current_date.day:2d}[/dim]"

        week_line.append(day_str)

        # 日曜日で改行
        if (current_date.weekday() + 1) % 7 == 0:
            calendar_lines.append("  ".join(week_line))
            week_line = []

        current_date += timedelta(days=1)

    # 最後の週を追加
    if week_line:
        while len(week_line) < 7:
            week_line.append("  ")
        calendar_lines.append("  ".join(week_line))

    for line in calendar_lines:
        console.print(f"  {line}")

    console.print()

    # 凡例
    console.print("[bold green]●N[/bold green] 記録あり  [dim]NN[/dim] 記録なし  [bold green]★N[/bold green] 今日(記録あり)  [bold yellow]▶N[/bold yellow] 今日(記録なし)\n")

    # === 継続ストリーク計算 ===
    # 今日から遡って連続記録日数を計算
    current_streak = 0
    check_date = today

    while check_date in entry_dates:
        current_streak += 1
        check_date -= timedelta(days=1)

    # 最長ストリーク計算
    sorted_dates = sorted(entry_dates)
    max_streak = 0
    current_max = 0
    prev_date = None

    for entry_date in sorted_dates:
        if prev_date is None:
            current_max = 1
        elif entry_date - prev_date == timedelta(days=1):
            current_max += 1
        else:
            max_streak = max(max_streak, current_max)
            current_max = 1
        prev_date = entry_date

    max_streak = max(max_streak, current_max)

    # 今月の記録率
    month_entries = [d for d in entry_dates if d.year == target_year and d.month == target_month]
    days_in_month = (last_day - first_day).days + 1
    month_rate = (len(month_entries) / days_in_month) * 100

    # ストリーク情報表示
    streak_info = f"""[bold]🔥 現在の継続ストリーク:[/bold] {current_streak}日
[bold]🏆 最長ストリーク:[/bold] {max_streak}日
[bold]📊 今月の記録率:[/bold] {len(month_entries)}/{days_in_month}日 ({month_rate:.1f}%)
[bold]📝 総日記数:[/bold] {len(entry_dates)}件"""

    console.print(Panel(streak_info, title="📈 統計情報", border_style="cyan"))

    # 励ましメッセージ
    if current_streak > 0:
        if current_streak >= 7:
            console.print(f"\n[bold green]✨ 素晴らしい！{current_streak}日連続で記録しています！[/bold green]")
        elif current_streak >= 3:
            console.print(f"\n[bold green]👍 いいですね！{current_streak}日連続です！[/bold green]")
        else:
            console.print(f"\n[green]📝 {current_streak}日連続で記録中です[/green]")
    else:
        if today in entry_dates:
            console.print("\n[cyan]📝 今日も記録できました！[/cyan]")
        else:
            console.print("\n[yellow]💡 今日の日記を書いてみませんか？[/yellow]")
            console.print("[dim]コマンド: clap diary write \"今日の内容\"[/dim]")

    console.print()
