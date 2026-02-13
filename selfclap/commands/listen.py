"""傾聴モード実装"""
import yaml
from rich.console import Console
from rich.panel import Panel
from selfclap.analysis.reflection import generate_reflection_data

console = Console()


def run_listen_mode():
    """傾聴モード実行"""
    console.print("\n[bold cyan]🤝 傾聴モード - 感情に寄り添う[/bold cyan]\n")
    console.print("過去のデータを分析しています...\n")

    # データ生成（reflectと同じ）
    data = generate_reflection_data()

    # YAML形式で出力
    yaml_output = yaml.dump(
        data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False
    )

    # プロンプト生成（トーンを変更）
    prompt = f"""
あなたは優しく傾聴するメンターです。

以下のデータを参考に、まずユーザーの気持ちを受け止めて、寄り添ってください。
解決策を押し付けず、共感と理解を示してください。

【ユーザーの状況】
最近の気分: {', '.join(data['current_state']['recent_moods']) if data['current_state']['recent_moods'] else '記録なし'}
最近の完了タスク: {data['current_state']['recent_tasks_completed']}個
連続記録: {data['current_state']['streak']}日

【過去のデータ】
学んだこと: {data['learning_accumulation']['total_diary_learnings']}件
過去との比較記録: {len(data['past_comparison']['comparison_records'])}件

【詳細データ】
{yaml_output}

【対応方針】
1. まずユーザーの気持ちを受け止める（「つらかったですね」「よく頑張っていますね」）
2. データを踏まえて、過去の成功体験や回復パターンを優しく伝える
3. 「あの時も乗り越えた」という事実を示す
4. 無理をさせない（「今日は休んでもいい」という選択肢も提示）

温かい言葉で励ましてください。
"""

    # パネルで表示
    console.print(Panel(
        prompt.strip(),
        title="💬 Claude Code へのプロンプト",
        subtitle="このプロンプトを Claude Code に送信してください",
        border_style="magenta"
    ))

    console.print("\n[dim]💡 Claude Code がこのデータを読み取り、温かく励まします。[/dim]\n")
