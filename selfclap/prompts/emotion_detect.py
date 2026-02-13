"""感情検知とモード推薦"""


def detect_emotional_content(content: str) -> dict:
    """
    日記内容から感情的なキーワードを検知

    Returns:
        {
            "is_negative": bool,
            "is_venting": bool,  # 愚痴・不満
            "is_frustrated": bool,
            "is_struggling": bool,
            "keywords": list,
            "recommended_mode": str or None
        }
    """

    # ネガティブキーワード
    negative_keywords = [
        "むかつく", "イライラ", "腹立つ", "うざい", "きつい",
        "つらい", "しんどい", "疲れた", "無理", "できない",
        "わからない", "ダメ", "最悪", "嫌", "辛い"
    ]

    # 愚痴・不満キーワード
    venting_keywords = [
        "先輩", "上司", "怒られた", "注意された", "指摘",
        "ばかり", "また", "いつも", "毎回", "何度も"
    ]

    # 挫折・苦悩キーワード
    struggling_keywords = [
        "わからない", "できない", "進まない", "詰まった",
        "行き詰まった", "どうすれば", "もう", "限界"
    ]

    content_lower = content.lower()

    found_negative = [kw for kw in negative_keywords if kw in content]
    found_venting = [kw for kw in venting_keywords if kw in content]
    found_struggling = [kw for kw in struggling_keywords if kw in content]

    is_negative = len(found_negative) > 0
    is_venting = len(found_venting) >= 2  # 2個以上で愚痴と判定
    is_struggling = len(found_struggling) > 0

    # モード推薦
    recommended_mode = None

    if is_venting or (is_negative and is_struggling):
        # 愚痴や不満 → 傾聴モード
        recommended_mode = "listen"
    elif is_struggling:
        # 苦悩・行き詰まり → 振り返りモード
        recommended_mode = "reflect"
    elif is_negative:
        # 一般的なネガティブ → 傾聴モード
        recommended_mode = "listen"

    return {
        "is_negative": is_negative,
        "is_venting": is_venting,
        "is_frustrated": is_negative and not is_struggling,
        "is_struggling": is_struggling,
        "keywords": found_negative + found_venting + found_struggling,
        "recommended_mode": recommended_mode
    }


def generate_mode_recommendation(emotion_data: dict, content: str) -> str:
    """モード推薦メッセージを生成"""

    mode = emotion_data["recommended_mode"]

    if not mode:
        return ""

    if mode == "listen":
        return f"""
╭───────────────────────────────────────────────────────────────────────────╮
│ 💭 つらそうな内容を検知しました                                          │
╰───────────────────────────────────────────────────────────────────────────╯

感情的な内容や不満・愚痴を書くことも大切です。
まず吐き出すことで、心が軽くなることがあります。

🤝 **この内容を傾聴モードで実行しますか?**

傾聴モードは、あなたの気持ちに寄り添い、温かい言葉で受け止めます。
過去のデータから、「あの時も乗り越えた」という事実を優しく伝えます。

実行方法:
```bash
clap listen
```

もちろん、今は何もしなくても大丈夫です。
書くだけでも十分です。
"""

    elif mode == "reflect":
        return f"""
╭───────────────────────────────────────────────────────────────────────────╮
│ 🤔 行き詰まっている様子を検知しました                                    │
╰───────────────────────────────────────────────────────────────────────────╯

「できない」「わからない」と感じている時こそ、
客観的なデータを見ることで新しい視点が得られるかもしれません。

🔍 **この内容を振り返りモードで実行しますか?**

振り返りモードは、「他人の評価」ではなく「自分の成長」を
データで客観的に示します。

実は、結果が出ていなくても、あなたは確実に成長しているかもしれません。

実行方法:
```bash
clap reflect
```

もちろん、今は休んでも大丈夫です。
無理をする必要はありません。
"""

    return ""
