# SelfClap 👏

**誰も拍手してくれないなら、自分で拍手しよう**

SelfClap は、あなたの日々の努力を記録し、AI が褒めてくれる日記 × タスク管理 CLI ツールです。

## 特徴

- 📝 **日記機能**: 毎日の出来事を記録
- ✅ **タスク管理**: TODO の追加・完了・管理
- 🤖 **AI が褒める**: Claude AI があなたの努力を認めてくれる
- 📊 **可視化**: 継続カレンダー、統計グラフで成長を実感
- 💡 **Tips & 名言**: たまに人生のアドバイスや励ましの言葉

## インストール

```bash
git clone https://github.com/yourname/selfclap.git
cd selfclap
pip install -e .
```

## セットアップ

```bash
clap init
```

Claude API Key を入力してください。

## 使い方

```bash
# 日記を書く
clap diary write

# タスク管理
clap task add "API を実装する"
clap task list
clap task done 1

# 統計・可視化
clap stats
clap calendar

# 励まし
clap encourage
```

## 開発

```bash
pip install -e ".[dev]"
pytest
```

## ライセンス

MIT
