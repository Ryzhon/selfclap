"""振り返りモード実装"""
import yaml
from rich.console import Console
from rich.panel import Panel
from selfclap.analysis.reflection import generate_reflection_data

console = Console()


def run_reflect_mode():
    """振り返りモード実行"""
    console.print("\n[bold cyan]🔍 振り返りモード - 他人軸 vs 自分軸[/bold cyan]\n")
    console.print("過去のデータを分析しています...\n")

    # データ生成
    data = generate_reflection_data()

    # YAML形式で出力
    yaml_output = yaml.dump(
        data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False
    )

    # プロンプト生成
    prompt = f"""
あなたは客観的なデータ分析者です。

以下のデータを読み取り、「他人の評価軸」と「自分の成長軸」を対比して示してください。

【重要な視点】
- 他人から見たあなた vs 客観的なデータが示すあなたの成長
- 見える成長（他人が認める） vs 見えない成長（データが証明する）
- 過去の自分と今の自分の比較

【データ】
{yaml_output}

【出力形式】
以下の形式で分析結果を提示してください:

━━━━━━━━━━━━━━━━━━━━━━━━
他人の評価 vs あなたの成長
━━━━━━━━━━━━━━━━━━━━━━━━

【他人から見たあなた】
（external_feedback から抽出）

【客観的なデータ: あなたの成長】
（learned_items, compared_items, difficulty_improvements から具体例を挙げる）

【見える成長 vs 見えない成長】
見える成長: （少ないかもしれない）
見えない成長: （データが証明する成長を列挙）

【結論】
あなたは確実に成長しています。
他人が認めるかどうかと、あなたが成長しているかは別の話です。

━━━━━━━━━━━━━━━━━━━━━━━━
"""

    # パネルで表示
    console.print(Panel(
        prompt.strip(),
        title="📊 Claude Code へのプロンプト",
        subtitle="このプロンプトを Claude Code に送信してください",
        border_style="cyan"
    ))

    # データ不足の指摘
    if data["data_gaps"]["suggestions"]:
        console.print("\n[yellow]📋 データ不足の指摘[/yellow]\n")
        for suggestion in data["data_gaps"]["suggestions"]:
            console.print(f"  • {suggestion}")
        console.print("\n[dim]これらを追記すると、より正確な分析ができます。[/dim]\n")
