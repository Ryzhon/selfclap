# SelfClap 実装タスク

## Phase 1: 基盤構築 (優先度: 最高)

### 1.1 データベース設計と実装
- [ ] データベース接続管理クラスの実装 (`selfclap/database/connection.py`)
  - SQLite接続のコンテキストマネージャ
  - 初回実行時の自動テーブル作成
  - `~/.selfclap/` ディレクトリの自動作成

- [ ] データモデルの定義 (`selfclap/database/models.py`)
  - `DiaryEntry` dataclass (拡張版フィールド含む)
  - `Task` dataclass (成長記録フィールド含む)
  - `ReflectionData` dataclass (振り返りデータ用)

- [ ] テーブルスキーマの作成
  ```sql
  diary_entries テーブル:
  - 基本: id, date, content, mood, energy_level
  - 成長: learned_today, compared_to_past, invisible_growth
  - 評価軸: external_feedback, self_assessment
  - 困難: challenges_faced, how_overcome
  - メタ: created_at, updated_at

  tasks テーブル:
  - 基本: id, title, description, status, priority
  - 成長: learnings, difficulty_before, difficulty_after
  - 時間: time_estimated, time_actual
  - 比較: similar_task_before, improvement_notes
  - 外部: external_review
  - メタ: created_date, completed_date, created_at, updated_at
  ```

- [ ] インデックスの設定
  - `diary_entries`: date, mood
  - `tasks`: status, completed_date, created_date

### 1.2 データベースクエリ実装
- [ ] DiaryQueries クラス (`selfclap/database/queries.py`)
  - `create_entry()`: 日記作成
  - `get_entry_by_date()`: 日付指定取得
  - `get_entries_since()`: 期間指定取得
  - `get_entries_by_mood()`: 気分でフィルタ
  - `update_entry()`: 日記更新（データ追記用）

- [ ] TaskQueries クラス
  - `create_task()`: タスク作成
  - `get_task_by_id()`: ID指定取得
  - `get_active_tasks()`: 未完了タスク一覧
  - `complete_task()`: タスク完了
  - `get_completed_tasks_since()`: 完了タスク取得
  - `update_task()`: タスク更新

## Phase 2: CLI基盤 (優先度: 最高)

### 2.1 CLIフレームワークセットアップ
- [ ] メインCLI構造 (`selfclap/cli.py`)
  - Typer app 初期化
  - Rich console セットアップ
  - サブコマンドグループの登録

- [ ] エントリポイント設定
  - `setup.py` の `console_scripts` 設定
  - `clap` コマンドが動作することを確認

### 2.2 日記コマンド実装
- [ ] `clap diary` サブコマンドグループ (`selfclap/commands/diary.py`)

- [ ] `clap diary write <content>` コマンド
  - 必須: content 引数
  - オプション: --mood, --learned, --compared-to-past
  - データベースに保存
  - 成功メッセージ表示

- [ ] `clap diary show [date]` コマンド
  - 日付省略時は今日
  - Rich パネルで見やすく表示
  - 存在しない場合のエラーメッセージ

- [ ] `clap diary list` コマンド
  - `--month` オプション
  - Rich Table で一覧表示
  - 内容は50文字で省略

- [ ] `clap diary update <date>` コマンド
  - 既存エントリにフィールド追加
  - データ追記促進用

### 2.3 タスクコマンド実装
- [ ] `clap task` サブコマンドグループ (`selfclap/commands/task.py`)

- [ ] `clap task add <title>` コマンド
  - オプション: --description, --priority
  - タスクID を表示

- [ ] `clap task list` コマンド
  - デフォルト: 未完了のみ
  - `--all` オプション: すべて表示
  - Rich Table で表示

- [ ] `clap task done <id>` コマンド
  - オプション: --difficulty-before, --difficulty-after, --learning
  - 完了日時を記録
  - データ入力促進メッセージ

- [ ] `clap task delete <id>` コマンド
  - 確認プロンプト表示

## Phase 3: 分析・振り返り機能 (優先度: 高)

### 3.1 データ分析ロジック
- [ ] 成長データ分析 (`selfclap/analysis/growth.py`)
  - `calculate_current_streak()`: 連続記録計算
  - `calculate_longest_streak()`: 最長連続記録
  - `get_task_completion_trend()`: タスク完了推移
  - `get_difficulty_improvement()`: 難易度変化分析

- [ ] 思考パターン分析 (`selfclap/analysis/patterns.py`)
  - `extract_recurring_worries()`: 頻出する悩み抽出
  - `find_recovery_patterns()`: 回復パターン検出
  - `analyze_mood_trends()`: 気分の傾向分析

### 3.2 振り返りモード実装
- [ ] 振り返りデータ生成 (`selfclap/analysis/reflection.py`)
  - `generate_reflection_data()`: 振り返り用データ構造化
  - 他人軸 vs 自分軸の対比データ
  - 見える成長 vs 見えない成長
  - 過去との比較データ
  - データ不足の検出と指摘

- [ ] `clap reflect` コマンド (`selfclap/commands/reflect.py`)
  - データ生成
  - YAML形式で出力
  - Claude Code 向けプロンプト表示
  - Rich パネルで整形

### 3.3 傾聴モード実装
- [ ] `clap listen` コマンド (`selfclap/commands/listen.py`)
  - `reflect` と同じデータ取得ロジック使用
  - プロンプトテンプレートを傾聴モード用に変更
  - 温かいトーンのメッセージ
  - YAML + プロンプト出力

## Phase 4: 可視化機能 (優先度: 中)

### 4.1 統計ダッシュボード
- [ ] ダッシュボード実装 (`selfclap/visualization/dashboard.py`)
  - `show_dashboard()`: 統計表示
  - Rich Table/Panel 使用
  - 連続記録、今月の統計、気分分布
  - 成長指標の表示

- [ ] `clap stats` コマンド
  - ダッシュボード呼び出し
  - オプション: --month, --json (JSON出力)

### 4.2 継続カレンダー
- [ ] カレンダー表示 (`selfclap/visualization/calendar.py`)
  - `show_calendar()`: 月別カレンダー
  - 日記・タスクの有無を色分け
  - Rich 使用

- [ ] `clap calendar` コマンド
  - オプション: --month

### 4.3 グラフ表示 (オプション)
- [ ] ASCII グラフ実装 (`selfclap/visualization/graphs.py`)
  - Plotille 使用
  - タスク完了数推移
  - 難易度変化グラフ

## Phase 5: データ入力促進 (優先度: 高)

### 5.1 データ不足検出
- [ ] データ充足度チェッカー (`selfclap/analysis/data_quality.py`)
  - `check_data_completeness()`: データの充足度チェック
  - 不足フィールドの特定
  - 優先度付け（今必要 vs 将来役立つ）

### 5.2 入力促進メッセージ
- [ ] プロンプトテンプレート (`selfclap/prompts/`)
  - `diary_write_prompt.txt`: 日記記録時の質問
  - `task_done_prompt.txt`: タスク完了時の質問
  - `reflect_data_shortage.txt`: 振り返り時のデータ不足指摘

- [ ] 入力促進ロジック
  - 記録時に自動的に質問を表示
  - Claude Code が質問を代行
  - 回答は任意であることを明示

## Phase 6: ユーティリティ (優先度: 中)

### 6.1 ヘルパー関数
- [ ] 日付ユーティリティ (`selfclap/utils/date_utils.py`)
  - `parse_date()`: 日付文字列パース
  - `get_month_range()`: 月の開始・終了日

- [ ] 設定管理 (`selfclap/utils/config.py`)
  - YAML設定ファイルの読み書き（オプション）

### 6.2 エラーハンドリング
- [ ] カスタム例外定義 (`selfclap/exceptions.py`)
  - `EntryNotFoundError`
  - `TaskNotFoundError`
  - `DatabaseError`

- [ ] グローバルエラーハンドラー
  - Typer のエラーハンドリング
  - ユーザーフレンドリーなメッセージ

## Phase 7: テスト (優先度: 中)

### 7.1 ユニットテスト
- [ ] データベーステスト (`tests/test_database.py`)
  - DiaryQueries のテスト
  - TaskQueries のテスト
  - エッジケースのテスト

- [ ] 分析ロジックテスト (`tests/test_analysis.py`)
  - 連続記録計算のテスト
  - パターン分析のテスト

### 7.2 統合テスト
- [ ] CLIコマンドテスト (`tests/test_cli.py`)
  - Typer の CliRunner 使用
  - 各コマンドの動作確認

## Phase 8: ドキュメント・仕上げ (優先度: 低)

### 8.1 ドキュメント
- [ ] README.md の最終調整
  - インストール手順
  - 使い方の例
  - Claude Code との連携方法

- [ ] CHANGELOG.md 作成
  - v0.1.0 の機能一覧

### 8.2 パッケージング
- [ ] requirements.txt の確認
  - すべての依存関係を記載
  - バージョン固定

- [ ] setup.py の最終調整
  - メタデータ
  - エントリポイント

### 8.3 初回実行体験
- [ ] ウェルカムメッセージ
  - 初回実行時のガイド
  - サンプルデータ（オプション）

## 実装順序の推奨

### Week 1: コア機能
1. Phase 1: データベース (1-2日)
2. Phase 2: CLI基盤 + 日記・タスク (2-3日)

### Week 2: 分析・可視化
3. Phase 3: 振り返り・傾聴モード (2-3日)
4. Phase 4: 統計・可視化 (1-2日)

### Week 3: 仕上げ
5. Phase 5: データ入力促進 (1-2日)
6. Phase 6-8: ユーティリティ、テスト、ドキュメント (2-3日)

## 依存関係

```
Phase 1 (データベース)
  ↓
Phase 2 (CLI基盤)
  ↓
Phase 3 (分析機能) ← データベース必須
  ↓
Phase 4 (可視化) ← 分析機能推奨
  ↓
Phase 5 (入力促進) ← すべての基盤が必要
  ↓
Phase 6-8 (仕上げ)
```

## マイルストーン

### Milestone 1: MVP (Minimum Viable Product)
- データベース動作
- 日記・タスクの基本CRUD
- `clap reflect` コマンド動作
- 目標: 2週間

### Milestone 2: 完全版
- すべての機能実装
- テスト完了
- ドキュメント完備
- 目標: 3週間

## 備考

- 各タスクは独立して実装可能
- 優先度の高いものから着手
- テストは機能実装と並行して進める
- Claude Code との連携を常に意識
