# SelfClap 👏

**誰も拍手してくれないなら、自分で拍手しよう**

SelfClap は、あなたの日々の努力を記録し、AI が褒めてくれる日記 × タスク管理 CLI ツールです。

## 👊 社会に負けるな！

### 背景: 新卒エンジニアが直面する課題
- 凄腕の先輩に「論理的思考力が弱い」「技術力が低い」と指摘され続ける
- なかなか結果が出ない
- 全く成長している感覚がない
- **評価軸が完全に他人（先輩）になっている**

### 問題: 「結果が出ない」=「成長していない」の思い込み
- 他人の評価でしか自分を測れない
- 見えない成長（他人は認めない成長）に気づけない
- 自分で自分を見つめ直す方法がわからない

### でも、あなたは確実に成長しています 💪

**「結果が出ない」≠「成長していない」**

SelfClap は、**客観的なデータで見えない成長を可視化**します：

- 📚 **学んだこと**を記録 → 知識の蓄積を証明
- 📈 **過去の自分との比較**を記録 → 成長の軌跡を可視化
- 🎯 **他人の評価 vs 自己評価**を分離 → 評価軸の独立
- 📊 **難易度の変化**を記録 → 理解度の向上を数値化

→ **「結果が出ていなくても、あなたは確実に成長している」ことを証明**

## 重要: Claude Code 前提の設計

**このツールは Claude Code CLI 上で使用することを前提に設計されています。**

- Claude Code と会話しながら使用するツールです
- API キー不要 - Claude Code Max プラン利用者がそのまま使えます
- AI 機能（褒め、励まし、分析）は Claude Code が担当
- SelfClap はデータ管理・可視化に特化

## 特徴

- 📝 **日記機能**: 毎日の出来事を記録
- ✅ **タスク管理**: TODO の追加・完了・管理
- 🤖 **Claude Code 統合**: Claude と会話しながら励ましを受ける
- 📊 **可視化**: 継続カレンダー、統計グラフで成長を実感
- 🏠 **完全ローカル**: データはすべて `~/.selfclap/` に保存、プライバシー保護

## 前提条件

- Python 3.10 以上
- [uv](https://github.com/astral-sh/uv) (高速Pythonパッケージマネージャー)
- Claude Code CLI (Max プラン推奨)

## インストール

```bash
# uvのインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# リポジトリをクローン
git clone https://github.com/yourname/selfclap.git
cd selfclap

# 仮想環境作成とパッケージインストール
uv venv
source .venv/bin/activate  # Windowsの場合: .venv\Scripts\activate
uv pip install -e .
```

## 使い方

**Claude Code 上で以下のように会話しながら使います:**

```
あなた: 「今日バグ修正できた!記録して!」

Claude Code: 「素晴らしい!バグ修正は...（褒める）
              記録しておきますね」
              → clap diary write "バグ修正できた"

あなた: 「今月の統計見せて」

Claude Code: → clap stats を実行
              → 結果を分析して励ましのコメント
```

### 基本コマンド

#### 日記コマンド

```bash
# 日記を書く
clap diary write "今日の内容" [OPTIONS]

オプション:
  --mood, -m           気分 (happy/neutral/tired/stressed/frustrated/anxious)
  --learned, -l        今日学んだこと
  --compared, -c       過去の自分と比べてできたこと
  --invisible, -i      他人は気づかないが自分は成長したこと
  --external, -e       他人からの評価・指摘
  --self-eval, -s      自己評価

例:
clap diary write "バグ修正完了!" --mood happy --learned "デバッグの効率的な進め方"

# 日記を表示
clap diary show [日付]          # 今日の日記 (日付省略時)
clap diary show 2026-02-13     # 指定日の日記

# 日記一覧
clap diary list                 # 今月の日記
clap diary list --month 1       # 1月の日記
clap diary list --all           # 全期間

# 日記を更新（データ追記）
clap diary update 2026-02-13 --learned "追加で学んだこと"
```

#### タスクコマンド

```bash
# タスク追加
clap task add "タスク名" [OPTIONS]

オプション:
  --desc, -d           説明
  --priority, -p       優先度 (low/medium/high)

例:
clap task add "API実装" --priority high --desc "ユーザー登録API"

# タスク一覧
clap task list          # 未完了タスク
clap task list --all    # 完了済みも含む

# タスク完了
clap task done <ID> [OPTIONS]

オプション:
  --difficulty-before, -b    開始時の難易度 (1-5)
  --difficulty-after, -a     完了時の難易度 (1-5)
  --learning, -l             学んだこと
  --time, -t                 実際の所要時間（時間）

例:
clap task done 1 --difficulty-before 4 --difficulty-after 2 --learning "エラーハンドリングの書き方"

# タスク削除
clap task delete <ID>       # 確認あり
clap task delete <ID> -y    # 確認なし
```

#### 分析・振り返りコマンド

```bash
# 振り返りモード（他人軸 vs 自分軸）
clap reflect

# 傾聴モード（感情に寄り添う）
clap listen

# 統計ダッシュボード
clap stats show [OPTIONS]

オプション:
  --days, -d    集計期間（日数）デフォルト: 30

例:
clap stats show           # 過去30日間の統計
clap stats show --days 7  # 過去7日間の統計

表示内容:
  • 基本統計（日記エントリ数、タスク完了数、記録日数）
  • 気分の分布
  • 成長データの充実度
  • タスクの難易度変化（理解度の向上）
  • データ充実度アドバイス

# 継続カレンダー
clap calendar show [OPTIONS]

オプション:
  --month, -m    月を指定 (1-12)
  --year, -y     年を指定

例:
clap calendar show              # 今月のカレンダー
clap calendar show --month 1    # 1月のカレンダー
clap calendar show --month 12 --year 2025  # 2025年12月

表示内容:
  • 月間カレンダー（記録日を緑色で表示）
  • 継続ストリーク（現在の連続記録日数）
  • 最長ストリーク
  • 月間記録率
  • 総日記数
```

## 開発

```bash
pip install -e ".[dev]"
pytest
```

## ライセンス

MIT
