"""日記コマンド実装"""
from datetime import date, datetime
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from selfclap.database.queries import DiaryQueries

app = typer.Typer(help="📝 日記管理")
console = Console()


@app.command("write")
def write(
    content: str = typer.Argument(..., help="日記の内容"),
    mood: Optional[str] = typer.Option(None, "--mood", "-m", help="気分 (happy/neutral/tired/stressed/frustrated/anxious)"),
    learned: Optional[str] = typer.Option(None, "--learned", "-l", help="今日学んだこと"),
    compared: Optional[str] = typer.Option(None, "--compared", "-c", help="過去の自分と比べてできたこと"),
    invisible: Optional[str] = typer.Option(None, "--invisible", "-i", help="他人は気づかないが自分は成長したこと"),
    external: Optional[str] = typer.Option(None, "--external", "-e", help="他人からの評価・指摘"),
    self_eval: Optional[str] = typer.Option(None, "--self-eval", "-s", help="自己評価"),
):
    """日記を書く"""
    db = DiaryQueries()
    today = date.today()

    try:
        entry = db.create_entry(
            entry_date=today,
            content=content,
            mood=mood,
            learned_today=learned,
            compared_to_past=compared,
            invisible_growth=invisible,
            external_feedback=external,
            self_assessment=self_eval
        )
        console.print(f"✅ [green]日記を保存しました![/green] ({entry.date})")

        # 感情検知とモード推薦
        from selfclap.prompts.emotion_detect import detect_emotional_content, generate_mode_recommendation

        emotion_data = detect_emotional_content(content)

        # モード推薦の表示
        if emotion_data["recommended_mode"]:
            recommendation = generate_mode_recommendation(emotion_data, content)
            console.print(recommendation)

        # AI自動分類プロンプト出力
        if not any([learned, compared, invisible, external, self_eval]):
            # 愚痴や不満の場合は分類をスキップ（傾聴/振り返りを優先）
            if emotion_data["is_venting"]:
                console.print("\n[dim]💡 感情を吐き出すことも大切です。分類は不要です。[/dim]\n")
            else:
                from selfclap.prompts.auto_classify import generate_diary_classification_prompt
                from rich.panel import Panel

                classification_prompt = generate_diary_classification_prompt(content, entry.date)

                console.print("\n")
                console.print(Panel(
                    classification_prompt,
                    title="🤖 Claude Code: 自動分類をお願いします",
                    border_style="cyan",
                    subtitle="このプロンプトに従って分類してください"
                ))
        else:
            console.print("\n[dim]💡 すでに分類情報が含まれています[/dim]\n")

    except Exception as e:
        console.print(f"[red]エラー: {e}[/red]")


@app.command("show")
def show(target_date: Optional[str] = typer.Argument(None, help="日付 (YYYY-MM-DD)")):
    """日記を表示"""
    db = DiaryQueries()

    if target_date:
        try:
            d = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            console.print("[red]エラー: 日付はYYYY-MM-DD形式で指定してください[/red]")
            return
    else:
        d = date.today()

    entry = db.get_entry_by_date(d)

    if not entry:
        console.print(f"[yellow]{d} の日記はありません[/yellow]")
        return

    # パネルで表示
    content = f"[bold]{entry.date}[/bold]\n\n"

    if entry.mood:
        mood_emoji = {
            "happy": "😊",
            "neutral": "😐",
            "tired": "😴",
            "stressed": "😰",
            "frustrated": "😤",
            "anxious": "😟"
        }
        content += f"気分: {mood_emoji.get(entry.mood, '')} {entry.mood}\n\n"

    content += f"{entry.content}\n"

    # 成長記録
    if entry.learned_today:
        content += f"\n📚 学んだこと:\n{entry.learned_today}\n"

    if entry.compared_to_past:
        content += f"\n📈 過去と比べて:\n{entry.compared_to_past}\n"

    if entry.invisible_growth:
        content += f"\n🌱 見えない成長:\n{entry.invisible_growth}\n"

    # 評価軸
    if entry.external_feedback:
        content += f"\n👥 他人の評価:\n{entry.external_feedback}\n"

    if entry.self_assessment:
        content += f"\n🪞 自己評価:\n{entry.self_assessment}\n"

    console.print(Panel(content, title="📝 日記", border_style="cyan"))


@app.command("list")
def list_entries(
    month: Optional[int] = typer.Option(None, "--month", "-m", help="月を指定 (1-12)"),
    all: bool = typer.Option(False, "--all", "-a", help="全期間表示")
):
    """日記一覧を表示"""
    db = DiaryQueries()

    if all:
        entries = db.get_all_entries()
    elif month:
        today = date.today()
        start_date = date(today.year, month, 1)
        entries = [e for e in db.get_all_entries() if e.date.month == month]
    else:
        # 今月
        today = date.today()
        start_date = date(today.year, today.month, 1)
        entries = db.get_entries_since(start_date)

    if not entries:
        console.print("[yellow]日記がありません[/yellow]")
        return

    table = Table(title="📝 日記一覧")
    table.add_column("日付", style="cyan", no_wrap=True)
    table.add_column("気分", style="magenta")
    table.add_column("内容（抜粋）", style="white")

    for entry in entries:
        mood = entry.mood or "-"
        preview = entry.content[:50] + "..." if len(entry.content) > 50 else entry.content
        table.add_row(str(entry.date), mood, preview)

    console.print(table)
    console.print(f"\n[dim]合計: {len(entries)}件[/dim]")


@app.command("update")
def update(
    target_date: str = typer.Argument(..., help="日付 (YYYY-MM-DD)"),
    learned: Optional[str] = typer.Option(None, "--learned", "-l", help="今日学んだこと"),
    compared: Optional[str] = typer.Option(None, "--compared", "-c", help="過去の自分と比べてできたこと"),
    invisible: Optional[str] = typer.Option(None, "--invisible", "-i", help="見えない成長"),
    external: Optional[str] = typer.Option(None, "--external", "-e", help="他人からの評価"),
    self_eval: Optional[str] = typer.Option(None, "--self-eval", "-s", help="自己評価"),
):
    """日記を更新（データ追記用）"""
    db = DiaryQueries()

    try:
        d = datetime.strptime(target_date, "%Y-%m-%d").date()
    except ValueError:
        console.print("[red]エラー: 日付はYYYY-MM-DD形式で指定してください[/red]")
        return

    entry = db.update_entry(
        entry_date=d,
        learned_today=learned,
        compared_to_past=compared,
        invisible_growth=invisible,
        external_feedback=external,
        self_assessment=self_eval
    )

    if entry:
        console.print(f"✅ [green]日記を更新しました![/green] ({d})")
    else:
        console.print(f"[yellow]{d} の日記が見つかりません[/yellow]")
