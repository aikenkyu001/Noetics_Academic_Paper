```mermaid
graph TD
    A["入力: 自然言語プロンプト<br>(en, ja, eo, jbo) x (命令/会話調)"] --> B{LLM};
    B --> C["出力: Python関数コード"];
    C --> D{Pytestによる自動検証};
    D --> E["結果: 成功 / 失敗"];
```

```mermaid
graph TD
    A["入力: フィルター条件と厳格な出力形式を指定したプロンプト<br>例: '偶数かつ8ではない数をリスト文字列として返せ'"] --> B{LLM};
    B --> C["出力: Pythonコードではなく<b>文字列</b><br>例: '[2, 4, 6, 10, ...]'"];
    C --> D{期待される文字列との完全一致検証};
    D --> E["結果: 成功 / 失敗"];
```

```mermaid
graph TD
    subgraph 入力プロンプト
        A1["ルールセット (S式形式)"]
        A2["ルールセット (JSON形式)"]
        A3["ルールセット (TSV形式など)"]
    end
    A1 --> B{LLM};
    A2 --> B;
    A3 --> B;
    B --> C["出力: ルールを実装したPython関数"];
    C --> D{Pytestによる自動検証};
    D --> E["結果: 成功 / 失敗"];
```

```mermaid
graph TD
    A["<b>入力: 1つの長大なプロンプト</b><br>以下を含む:<br>1. 未知のトークン言語で書かれたパズル<br>2. トークン言語の文法ルール<br>3. バックトラッキングアルゴリズムの模範解答例"] --> B{LLM};
    subgraph "LLMが達成すべき内部タスク"
        B1["<b>課題1: 文法学習</b><br>トークン言語のルールを解釈する"]
        B2["<b>課題2: アルゴリズム学習</b><br>模範解答からバックトラッキング構造を抽出する"]
        B3["<b>課題3: コード実装</b><br>学習した文法とアルゴリズムを組み合わせ、<br>Pythonでソルバーを実装する"]
    end
    B --> B1 --> B2 --> B3;
    B3 --> C["出力: 最終的なPythonソルバーコード"];
    C --> D{Pytestによる自動検証};
    D -- 実行時エラー (KeyErrorなど) --> E["結果: 失敗"];
```

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Overall Performance Ranking",
  "height": 500,
  "data": {
    "values": [
      {"モデル": "yi:6b", "総合成功率": "74.42%"},
      {"モデル": "gemma3:4b", "総合成功率": "73.75%"},
      {"モデル": "llama3.2:3b", "総合成功率": "70.42%"},
      {"モデル": "falcon3:3b", "総合成功率": "70.00%"},
      {"モデル": "gemma:7b", "総合成功率": "70.00%"},
      {"モデル": "deepseek-r1:8b", "総合成功率": "68.17%"},
      {"モデル": "llama3:8b", "総合成功率": "67.42%"},
      {"モデル": "mistral:7b", "総合成功率": "52.50%"},
      {"モデル": "llama2:7b", "総合成功率": "45.00%"},
      {"モデル": "deepseek-r1:1.5b", "総合成功率": "40.00%"},
      {"モデル": "deepseek-llm:7b", "総合成功率": "35.00%"},
      {"モデル": "stablelm2:1.6b", "総合成功率": "33.17%"},
      {"モデル": "smollm:360m", "総合成功率": "32.50%"},
      {"モデル": "gemma:2b", "総合成功率": "30.00%"},
      {"モデル": "gemma3:270m", "総合成功率": "27.50%"},
      {"モデル": "tinyllama:1.1b", "総合成功率": "15.00%"},
      {"モデル": "qwen:4b", "総合成功率": "12.50%"},
      {"モデル": "phi3:mini", "総合成功率": "7.50%"},
      {"モデル": "qwen:1.8b", "総合成功率": "5.08%"},
      {"モデル": "qwen:0.5b", "総合成功率": "5.00%"}
    ]
  },
  "transform": [
    {"calculate": "toNumber(replace(datum.総合成功率, '%', '')) / 100", "as": "SuccessRate"}
  ],
  "mark": "bar",
  "encoding": {
    "y": {
      "field": "モデル",
      "type": "nominal",
      "title": "Model",
      "sort": {"op": "sum", "field": "SuccessRate", "order": "descending"}
    },
    "x": {
      "field": "SuccessRate",
      "type": "quantitative",
      "axis": {"format": "%"},
      "title": "Overall Success Rate"
    },
    "tooltip": [
      {"field": "モデル", "type": "nominal", "title": "Model"},
      {"field": "SuccessRate", "type": "quantitative", "format": ".2%"}
    ]
  }
}
```