"""SelfClap CLI エントリポイント"""
import typer
from rich.console import Console

# メインアプリ
app = typer.Typer(
    name="clap",
    help="👏 誰も拍手してくれないなら、自分で拍手しよう",
    add_completion=False,
    no_args_is_help=True
)

console = Console()


# サブコマンドは後で追加
from selfclap.commands import diary, task, stats, calendar


# サブコマンドグループ登録
app.add_typer(diary.app, name="diary", help="📝 日記管理")
app.add_typer(task.app, name="task", help="✅ タスク管理")
app.add_typer(stats.app, name="stats", help="📊 統計ダッシュボード")
app.add_typer(calendar.app, name="calendar", help="📅 継続カレンダー")


@app.command()
def reflect():
    """🔍 振り返りモード - 他人軸vs自分軸"""
    from selfclap.commands.reflect import run_reflect_mode
    run_reflect_mode()


@app.command()
def listen():
    """🤝 傾聴モード - 感情に寄り添う"""
    from selfclap.commands.listen import run_listen_mode
    run_listen_mode()


def main():
    """エントリポイント"""
    app()


if __name__ == "__main__":
    main()
