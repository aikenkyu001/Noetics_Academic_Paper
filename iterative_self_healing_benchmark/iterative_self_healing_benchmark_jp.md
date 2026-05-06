# 大規模言語モデルの決定論的コード生成に向けた体系的アプローチ：スキャフォールディング戦略の有効性に関する研究

**著者：** Fumio Miyata  
**DOI:** [https://doi.org/10.5281/zenodo.18678188](https://doi.org/10.5281/zenodo.18678188)

---

## 要旨

本稿は、大規模言語モデル（LLM）の「機能的非決定性」という課題に対し、コード生成の信頼性を体系的に評価・改善する方法論を実験的に検証した結果を報告する。

我々は、形式言語「Sigma-Lisp」とPythonコード間の意味的一貫性を評価するベンチマークを設計し、二つの仮説を検証した。第一に、LLMに自己の誤りを分析させる「内省」アプローチの有効性を検証したが、本実験条件下では有意な改善は観測されなかった。第二に、モデルの弱点を外部から補強する「外部スキャフォールディング」アプローチを検証したところ、特定の論理誤りをプログラム的に修正する「エラー正規化」や、実装手順を詳細に記述する「誘導付きプロンプト」が有効であることが確認された。

最終的に、これらを統合した「スキャフォールディング・トリニティ」と、NL→Lisp変換で温度1.0、Lisp→Code変換で温度0.0を用いる「二段階温度設定」を組み合わせた方法論を構築した。この方法論を最も困難な「NL→Lisp→Code」パイプラインに適用した結果、`gemma3:12b`モデルは30タスクにおいて平均成功率100%（30/30、Clopper-Pearson法による95%信頼区間: [88.4%, 100%]）を達成した。

本研究は、LLMが精密な外部ガイド下で、実行可能なコードを安定的に生成しうることを、再現可能な実験条件のもとで示すものである。

---

## 1. 緒言

### 1.1 背景

大規模言語モデル（LLM）はソフトウェア開発支援において顕著な成果を示しているが、同一入力に対して異なる出力を生成する「機能的非決定性」は、実用上の課題として残されている。**図1**に示すように、単一のプロンプトから多様な、しかし必ずしも正しくないコードが生成されうるため、特にエンジニアリング分野では再現性と安定性が強く求められる。

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "LLMの機能的非決定性の問題を示す概念図",
  "title": { "text": "図1: 機能的非決定性の問題", "anchor": "start" },
  "width": 400, "height": 250,
  "config": {"view": {"stroke": "transparent"}},
  "datasets": {
    "nodes": [
      {"id": "A", "x": 50, "y": 125, "label": "Prompt"},
      {"id": "B", "x": 200, "y": 125, "label": "LLM"},
      {"id": "C1", "x": 350, "y": 50, "label": "Correct Code"},
      {"id": "C2", "x": 350, "y": 125, "label": "Buggy Code A"},
      {"id": "C3", "x": 350, "y": 200, "label": "Buggy Code B"}
    ],
    "edges": [
      {"source": "A", "target": "B"},
      {"source": "B", "target": "C1"},
      {"source": "B", "target": "C2"},
      {"source": "B", "target": "C3"}
    ]
  },
  "layer": [
    {
      "data": {"name": "edges"},
      "transform": [
        {
          "lookup": "source",
          "from": {"data": {"name": "nodes"}, "key": "id", "fields": ["x", "y"]},
          "as": ["source_x", "source_y"]
        },
        {
          "lookup": "target",
          "from": {"data": {"name": "nodes"}, "key": "id", "fields": ["x", "y"]},
          "as": ["target_x", "target_y"]
        }
      ],
      "mark": {"type": "rule", "strokeWidth": 2, "stroke": "#333"},
      "encoding": {
        "x": {"field": "source_x", "type": "quantitative", "axis": null},
        "y": {"field": "source_y", "type": "quantitative", "axis": null},
        "x2": {"field": "target_x", "type": "quantitative"},
        "y2": {"field": "target_y", "type": "quantitative"}
      }
    },
    {
      "data": {"name": "nodes"},
      "mark": {"type": "rect", "width": 100, "height": 40, "color": "#e0f2f7", "stroke": "#00796b", "strokeWidth": 1.5},
      "encoding": {
        "x": {"field": "x", "type": "quantitative", "axis": null},
        "y": {"field": "y", "type": "quantitative", "axis": null}
      }
    },
    {
      "data": {"name": "nodes"},
      "mark": {"type": "text", "fontWeight": "bold"},
      "encoding": {
        "x": {"field": "x", "type": "quantitative", "axis": null},
        "y": {"field": "y", "type": "quantitative", "axis": null},
        "text": {"field": "label"}
      }
    }
  ]
}
```

### 1.2 研究目的

本研究は、**図2**に示す二つの対照的なアプローチに基づき、以下の問いに答えることを目的とする。

1. LLMは内省的プロンプトにより論理誤りを自律的に修正できるか。（図2左: 内省アプローチ）
2. 外部からの構造的介入（スキャフォールディング）は性能安定化に寄与するか。（図2右: 外部スキャフォールディング）

本稿は観測事実の報告を目的とし、理論的普遍性を主張するものではない。

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "内省と外部スキャフォールディングの概念的対比",
  "title": {
    "text": "図2: 内省 vs 外部スキャフォールディングの概念的対比",
    "anchor": "start"
  },
  "spacing": 40,
  "align": "all",
  "bounds": "flush",

  "hconcat": [
    {
      "title": {"text": "内省アプローチ", "fontSize": 14, "anchor": "middle"},
      "width": 250,
      "height": 300,
      "autosize": {"type": "none", "contains": "padding"},
      "config": {"view": {"stroke": "#dddddd"}},

      "layer": [

        {
          "data": {
            "values": [
              {"x1":150,"y1":50,"x2":150,"y2":150},
              {"x1":150,"y1":150,"x2":50,"y2":150},
              {"x1":50,"y1":150,"x2":50,"y2":50},
              {"x1":50,"y1":50,"x2":150,"y2":50}
            ]
          },
          "mark": {"type":"rule","stroke":"#ff7f0e","strokeWidth":2},
          "encoding": {
            "x":{"field":"x1","type":"quantitative","axis":null},
            "y":{"field":"y1","type":"quantitative","axis":null},
            "x2":{"field":"x2"},
            "y2":{"field":"y2"}
          }
        },

        {
          "data": {
            "values": [
              {"x":150,"y":50,"label":"LLM"},
              {"x":150,"y":150,"label":"Code"},
              {"x":50,"y":150,"label":"Test"},
              {"x":50,"y":50,"label":"Feedback"}
            ]
          },
          "transform":[
            {"calculate":"datum.x-40","as":"x1"},
            {"calculate":"datum.x+40","as":"x2"},
            {"calculate":"datum.y-15","as":"y1"},
            {"calculate":"datum.y+15","as":"y2"}
          ],
          "mark":{"type":"rect","color":"#fff0e0","stroke":"#ff7f0e","strokeWidth":1.5},
          "encoding":{
            "x":{"field":"x1","type":"quantitative","axis":null},
            "x2":{"field":"x2"},
            "y":{"field":"y1","type":"quantitative","axis":null},
            "y2":{"field":"y2"}
          }
        },

        {
          "data": {
            "values": [
              {"x":150,"y":50,"label":"LLM"},
              {"x":150,"y":150,"label":"Code"},
              {"x":50,"y":150,"label":"Test"},
              {"x":50,"y":50,"label":"Feedback"}
            ]
          },
          "mark":{"type":"text","fontWeight":"bold","align":"center","baseline":"middle"},
          "encoding":{
            "x":{"field":"x","type":"quantitative","axis":null},
            "y":{"field":"y","type":"quantitative","axis":null},
            "text":{"field":"label"}
          }
        }

      ]
    },

{
  "title": {"text": "外部スキャフォールディング", "fontSize": 14, "anchor": "middle"},
  "width": 250,
  "height": 300,
  "autosize": {"type": "none", "contains": "padding"},
  "config": {"view": {"stroke": "#dddddd"}},

  "layer": [

    {
      "data": {
        "values": [
          {"x1":0,"y1":50,"x2":0,"y2":125},
          {"x1":0,"y1":125,"x2":0,"y2":200},
          {"x1":0,"y1":200,"x2":0,"y2":275}
        ]
      },
      "mark":{"type":"rule","stroke":"#00796b","strokeWidth":2},
      "encoding":{
        "x":{
          "field":"x1",
          "type":"quantitative",
          "axis":null,
          "scale":{"domain":[-30,30]}
        },
        "y":{
          "field":"y1",
          "type":"quantitative",
          "axis":null,
          "scale":{"domain":[0,320]}
        },
        "x2":{"field":"x2"},
        "y2":{"field":"y2"}
      }
    },

    {
      "data": {
        "values": [
          {"x":0,"y":50,"label":"Scaffold"},
          {"x":0,"y":125,"label":"LLM"},
          {"x":0,"y":200,"label":"Code"},
          {"x":0,"y":275,"label":"Test"}
        ]
      },
      "transform":[
        {"calculate":"datum.x-10","as":"x1"},
        {"calculate":"datum.x+10","as":"x2"},
        {"calculate":"datum.y-15","as":"y1"},
        {"calculate":"datum.y+15","as":"y2"}
      ],
      "mark":{
        "type":"rect",
        "color":"#e0f2f7",
        "stroke":"#00796b",
        "strokeWidth":1.5
      },
      "encoding":{
        "x":{
          "field":"x1",
          "type":"quantitative",
          "axis":null,
          "scale":{"domain":[-30,30]}
        },
        "x2":{"field":"x2"},
        "y":{
          "field":"y1",
          "type":"quantitative",
          "axis":null,
          "scale":{"domain":[0,320]}
        },
        "y2":{"field":"y2"}
      }
    },

    {
      "data": {
        "values": [
          {"x":0,"y":50,"label":"Scaffold"},
          {"x":0,"y":125,"label":"LLM"},
          {"x":0,"y":200,"label":"Code"},
          {"x":0,"y":275,"label":"Test"}
        ]
      },
      "mark":{
        "type":"text",
        "fontWeight":"bold",
        "align":"center",
        "baseline":"middle"
      },
      "encoding":{
        "x":{
          "field":"x",
          "type":"quantitative",
          "axis":null,
          "scale":{"domain":[-30,30]}
        },
        "y":{
          "field":"y",
          "type":"quantitative",
          "axis":null,
          "scale":{"domain":[0,320]}
        },
        "text":{"field":"label"}
      }
    }

  ]
}

  ]
}

```

### 1.3 関連研究

LLMのコード生成における信頼性の研究は、大きく二つの潮流に分類できる。

#### 1.3.1 自己修正（Self-Correction）系研究
第一の潮流は、LLMに自己の出力の誤りを検知・修正させる「内省的」アプローチである。しかし、このアプローチの有効性には限界があることが指摘されている。複雑なタスクやコード生成において、外部からのフィードバックなしでの内在的自己修正はほぼ機能しない（Kamoi et al., 2024）。LLMは自身の誤りを特定できない「自己修正盲点」（blind spot）を持ち、平均64.5%のケースで修正に失敗するという報告もある（Self-Correction Bench, 2025）。さらに、推論タスクでは自己修正が逆に性能を低下させるケースも観測されており（Huang et al., 2024）、外部知識（RAGなど）を用いた方が改善効果が高いことも示唆されている（Failure-Aware Enhancements..., 2026）。本研究のフェーズ4–6で観測された内省アプローチの失敗は、これらの知見をコード生成ドメインで実証・拡張したものである。

#### 1.3.2 外部構造・プロンプト工学・エージェント系研究
第二の潮流は、プロンプト工学や外部ツール、エージェント・フレームワークを用いてLLMの挙動を構造化・安定化させるアプローチである。プロンプトにI/O仕様、例、曖昧さ解消などの詳細な情報を含めることで、コード生成の信頼性が大幅に向上することが経験的に知られている（Guidelines..., 2026; Prompt engineering..., 2025）。エージェント・システムもまた、外部ツールやイテレーションといった構造を利用してタスク達成率を高めている（A Survey on Code Generation with LLM-based Agents, 2025）。

本研究は、この第二の潮流に位置づけられる。特に、Lispを介したメタプログラミング（From Tool Calling..., 2025）や形式的構成推論（LLM-Based Code Translation..., 2025）の重要性が指摘される中、本研究のスキャフォールディング・トリニティは、これらのアイデアを統合・体系化したものである。**本研究の新規性は、LLMエージェントのような動的な実行ループに依存せず、静的なプロンプトと外部スクリプトによる「スキャフォールディング」のみで、同等の安定性を達成した点にある。**

コード生成タスクは、他の自然言語生成タスクと比較して、機能的非決定性の問題が特に顕著になる傾向がある。これは、コードが厳密な構文規則と意味論に従う必要があり、わずかな誤差がコンパイルエラーや実行時エラーに直結するためである。また、求める出力が離散的な「正解」コードであるため、曖昧さが許容される自然言語テキストとは異なり、完全一致性が強く要求される。このような生成空間の特性が、LLMの確率的な挙動と相まって、コード生成の安定化を一層困難にしている。

---

## 2. 実験設計

### 2.1 ベンチマーク・パイプライン

本研究では以下の二種のパイプラインを使用した：

* **Lisp⇔Code パイプライン（フェーズ1–11）**
  形式言語とPythonコード間の往復変換と自己修正能力を評価。

* **NL→Lisp→Code パイプライン（フェーズ12）**
  自然言語要求から形式仕様を経てコードを生成する最終評価系。

---

### 2.2 タスクセット

* タスク数：30
* カテゴリ：動的計画法、グラフ理論、バックトラッキング、文字列処理等
* 平均テストケース数：約10ケース／タスク
* 全ての実験リソース（定義・スクリプト・プロンプト）は、https://github.com/aikenkyu001/iterative_self_healing_benchmark で公開されている。

---

### 2.3 評価指標

* **成功の定義**：最大10サイクル以内に全テストケースを通過
* **試行回数**：各タスクにつき30回独立実行
* **成功率**：30試行の平均成功率

---

### 2.4 決定論的挙動の定義

本研究における「決定論的」とは、理論的決定性を主張するものではなく、以下の条件を満たす**操作的定義（operational definition）**である。

*   温度0.0設定下で同一入力に対し、生成されたコードの出力トークンが完全一致する。
*   生成されたコードが全Test Caseを安定して通過し、実行結果も一致する。
*   30回の独立試行において成功率100%を達成する。
ただし、この操作的定義はOllamaの実装依存性やGPU差異などの実行基盤依存性を完全に排除するものではない。

---

### 2.5 二段階温度設定

自然言語段階では多様性を許容し、形式仕様段階では決定性を最大化する設計とした。この全体構造を**図3**に示す。

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",

  "title": {
    "text": "図3: 二段階温度設定パイプライン",
    "anchor": "start"
  },

  "width": 250,
  "height": 450,
  "autosize": {"type": "none", "contains": "padding"},

  "config": {
    "view": {"stroke": null}
  },

  "layer": [

    {
      "data": {
        "values": [
          {"x":0,"y":0,"label":"Natural Language"},
          {"x":0,"y":100,"label":"LLM @ T=1.0"},
          {"x":0,"y":200,"label":"Sigma-Lisp"},
          {"x":0,"y":300,"label":"LLM @ T=0.0"},
          {"x":0,"y":400,"label":"Python Code"}
        ]
      },
      "transform":[
        {"calculate":"datum.x","as":"x1"},
        {"calculate":"datum.x+120","as":"x2"},
        {"calculate":"datum.y","as":"y1"},
        {"calculate":"datum.y+40","as":"y2"}
      ],
      "mark":{
        "type":"rect",
        "color":"#e0f2f7",
        "stroke":"#00796b",
        "strokeWidth":1.5
      },
      "encoding":{
        "x":{"field":"x1","type":"quantitative","axis":null,"scale":{"domain":[0,200]}},
        "x2":{"field":"x2"},
        "y":{"field":"y1","type":"quantitative","axis":null,"scale":{"domain":[0,450]}},
        "y2":{"field":"y2"}
      }
    },

    {
      "data": {
        "values": [
          {"x":60,"y":20,"label":"Natural Language"},
          {"x":60,"y":120,"label":"LLM @ T=1.0"},
          {"x":60,"y":220,"label":"Sigma-Lisp"},
          {"x":60,"y":320,"label":"LLM @ T=0.0"},
          {"x":60,"y":420,"label":"Python Code"}
        ]
      },
      "mark":{
        "type":"text",
        "fontWeight":"bold",
        "align":"center",
        "baseline":"middle"
      },
      "encoding":{
        "x":{"field":"x","type":"quantitative","axis":null,"scale":{"domain":[0,200]}},
        "y":{"field":"y","type":"quantitative","axis":null,"scale":{"domain":[0,450]}},
        "text":{"field":"label"}
      }
    },

    {
      "data": {
        "values": [
          {"x1":60,"y1":40,"x2":60,"y2":100},
          {"x1":60,"y1":140,"x2":60,"y2":200},
          {"x1":60,"y1":240,"x2":60,"y2":300},
          {"x1":60,"y1":340,"x2":60,"y2":400}
        ]
      },
      "mark":{"type":"rule","stroke":"black","strokeWidth":2},
      "encoding":{
        "x":{"field":"x1","type":"quantitative","axis":null,"scale":{"domain":[0,200]}},
        "y":{"field":"y1","type":"quantitative","axis":null,"scale":{"domain":[0,450]}},
        "x2":{"field":"x2"},
        "y2":{"field":"y2"}
      }
    },

    {
      "data": {
        "values": [
          {"x":60,"y":80},
          {"x":60,"y":180},
          {"x":60,"y":280},
          {"x":60,"y":380}
        ]
      },
      "mark":{
        "type":"text",
        "text":"↓",
        "fontSize":20,
        "fontWeight":"bold",
        "align":"center",
        "baseline":"middle"
      },
      "encoding":{
        "x":{"field":"x","type":"quantitative","axis":null,"scale":{"domain":[0,200]}},
        "y":{"field":"y","type":"quantitative","axis":null,"scale":{"domain":[0,450]}}
      }
    }
  ]
}

```

### 2.6 再現性について

本実験の再現性を確保するため、環境設定を明記する。推論にはOllamaを介して論文中で指定されたモデルバージョンを使用した。ランダムシードは固定し、温度（T=1.0およびT=0.0）以外のLLMパラメータはデフォルト設定を採用した。詳細な実験設定、プロンプト、スクリプトを含む全ての実験リソースは、https://github.com/aikenkyu001/iterative_self_healing_benchmark で公開されている。

---

## 3. 実験結果

### 3.1 内省アプローチ（フェーズ4–6）

本実験条件下では内省プロンプト導入による成功例は観測されなかった。**表1**に示す通り、30タスク×30試行の合計900試行において成功は0回であり、成功率は著しく低下した。フェーズごとの成功率の全体的な推移を**図4**に示す。

**表1: 内省アプローチの成功率**
| フェーズ | 戦略     | 成功率  |
| ---- | ------ | ---- |
| 1–3  | ベースライン | 100% |
| 4–6  | 内省導入   | 0%   |

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "実験フェーズごとの成功率推移",
  "title": {
    "text": "図4: 実験フェーズごとの成功率推移",
    "anchor": "start"
  },
  "width": 500,
  "height": 300,
  "data": {
    "values": [
      {"phase_group": "Phase 1-3", "strategy": "ベースライン", "success_rate": 100},
      {"phase_group": "Phase 4-6", "strategy": "内省導入", "success_rate": 0},
      {"phase_group": "Phase 7-12", "strategy": "外部スキャフォールディング", "success_rate": 100}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {
      "field": "phase_group",
      "type": "ordinal",
      "title": "実験フェーズ",
      "sort": null
    },
    "y": {
      "field": "success_rate",
      "type": "quantitative",
      "title": "成功率 (%)",
      "axis": {"titleOrient": "bottom"},
      "scale": {"domain": [0, 100]}
    },
    "color": {
      "field": "strategy",
      "type": "nominal",
      "title": "戦略",
      "scale": {
        "domain": ["ベースライン", "内省導入", "外部スキャフォールディング"],
        "range": ["#1f77b4", "#ff7f0e", "#2ca02c"]
      }
    },
    "tooltip": [
      {"field": "phase_group", "title": "フェーズグループ"},
      {"field": "strategy", "title": "戦略"},
      {"field": "success_rate", "title": "成功率", "format": ".1f"}
    ]
  },
  "config": {
    "axis": {"labelFontSize": 12, "titleFontSize": 14},
    "legend": {"orient": "right"},
    "title": {"anchor": "start", "fontSize": 16}
  }
}

```

---

### 3.2 外部スキャフォールディング（フェーズ7, 9）

外部スクリプトによる補正導入後、**表2**に示すように性能はベースラインに回復した。

**表2: 外部介入による性能回復**
| フェーズ | 戦略   | 成功率  |
| ---- | ---- | ---- |
| 4–6  | 内省   | 0%   |
| 7,9  | 外部介入 | 100% |

---

### 3.3 最終パイプライン（フェーズ12）

最終的なNL→Lisp→Codeパイプラインにおける各モデルの性能を**表3**に示す。

**表3: 最終パイプラインにおける各モデルの性能**
| モデル                 | 成功 (30試行平均) | 成功率  |
| ------------------- | ----------- | ---- |
| gemma3:12b          | 30/30       | 100% | (決定論的達成)
| llama3.2-vision:11b | 25/30       | 83%  |
| llama3:8b           | 22/30       | 73%  |

gemma3:12bは全試行において成功した（30/30、Clopper-Pearson法による95%信頼区間: [88.4%, 100%]）。信頼区間は二項分布に基づくClopper–Pearsonの正確法（exact method）で算出した。

---

## 4. 総合考察

観測結果は、LLMの挙動安定化において、モデル自身の「内省（内在的制御）」よりも、外部からの構造的な制約やガイド（外在的制御）の方が有効である可能性を示唆する。本研究の最も重要な発見は、「内省は性能を低下させ、外部構造は性能を安定させる」という、制御理論的な対比である。

特に、**図5**に示す「スキャフォールディング・トリニティ」が安定性向上に寄与したという構造仮説を支持する。
*   **Specification Scaffold:** 構造化された設計書。
*   **Grammar Scaffold:** 形式言語（Sigma-Lisp）による文法拡張。
*   **Execution Scaffold:** 実装指示の明示化と二段階温度設定。

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "スキャフォールディング・トリニティの構成要素",
  "title": {"text": "図5: スキャフォールディング・トリニティの構成要素", "anchor": "start"},
  "width": 500, "height": 300,
  "config": {"view": {"stroke": "transparent"}},
  "datasets": {
    "nodes": [
      {"id": "S1", "label": ["Specification","Scaffold"], "x": 100, "y": 50},
      {"id": "S2", "label": ["Grammar","Scaffold"], "x": 250, "y": 50},
      {"id": "S3", "label": ["Execution","Scaffold"], "x": 400, "y": 50},
      {"id": "LLM", "label": "LLM", "x": 250, "y": 150},
      {"id": "CODE", "label": "Deterministic Code", "x": 250, "y": 250}
    ],
    "edges": [
      {"source": "S1", "target": "LLM"},
      {"source": "S2", "target": "LLM"},
      {"source": "S3", "target": "LLM"},
      {"source": "LLM", "target": "CODE"}
    ]
  },
  "layer": [
    {
      "data": {"name": "edges"},
      "transform": [
        {
          "lookup": "source",
          "from": {"data": {"name": "nodes"}, "key": "id", "fields": ["x", "y"]},
          "as": ["source_x", "source_y"]
        },
        {
          "lookup": "target",
          "from": {"data": {"name": "nodes"}, "key": "id", "fields": ["x", "y"]},
          "as": ["target_x", "target_y"]
        }
      ],
      "mark": {"type": "rule", "strokeWidth": 2, "stroke": "#00796b"},
      "encoding": {
        "x": {"field": "source_x", "type": "quantitative", "axis": null},
        "y": {"field": "source_y", "type": "quantitative", "axis": null},
        "x2": {"field": "target_x", "type": "quantitative"},
        "y2": {"field": "target_y", "type": "quantitative"}
      }
    },
    {
      "data": {"name": "nodes"},
      "mark": {"type": "rect", "width": 120, "height": 90, "color": "#e0f2f7", "stroke": "#00796b", "strokeWidth": 1.5, "cornerRadius": 5},
      "encoding": {
        "x": {"field": "x", "type": "quantitative", "axis": null},
        "y": {"field": "y", "type": "quantitative", "axis": null}
      }
    },
    {
      "data": {"name": "nodes"},
      "mark": {"type": "text", "fontWeight": "bold", "align": "center", "baseline": "middle"},
      "encoding": {
        "x": {"field": "x", "type": "quantitative", "axis": null},
        "y": {"field": "y", "type": "quantitative", "axis": null},
        "text": {"field": "label"}
      }
    }
  ]
}
```

本結果は特定モデルおよび特定設定下での観測事実であり、他モデルへの一般化は本研究の範囲外である。

Lispを介したメタプログラミングループでLLMの象徴的思考を強化する試みがあるように（From Tool Calling to Symbolic Thinking..., 2025）、形式言語の活用はLLMの能力を引き出す上で重要な方向性を示唆する。LLM生成コードのエラーはドメイン知識不足由来が多く、外部構造で緩和可能であることが指摘されているが（Understanding and Mitigating Errors..., 2025）、本研究のTrinityは汎用アルゴリズムタスクで同様の知見を適用し、その有効性を示した。コード翻訳には形式的な構成推論が必要であるという提言（LLM-Based Code Translation..., 2025）は、Sigma-Lispを介した二段階パイプラインが、この形式性をLLMに強制する手法として機能し、決定論的コード生成に寄与したという本研究の成果を補強する。

本研究は、LLMの能力向上ではなく、構造設計による挙動制御の可能性を示すものである。

---

## 5. 限界

*   モデルは主にgemma系とllama系に限定される。
*   プロンプトは英語のみで検証した。
*   設計書（Specification Scaffold）は手動で構築した。
*   スキャフォールディングはタスク固有であり、一般化には追加の設計が必要である。
*   本方法論の自動化は未検証である。

---

## 6. 結論

本実験条件下では、内省のみでは安定化しなかった。一方、外部スキャフォールディング導入後には安定した成功が観測された。

スキャフォールディング・トリニティおよび二段階温度設定の下で、`gemma3:12b`は30の多様なアルゴリズムタスクにおいて、操作的に定義された決定論的な成功を達成した。

本稿は観測結果の報告を目的とし、理論的普遍性の主張は行わない。今後は本方法論の自動化および他モデルへの適用検証が課題となる。本研究は、LLMの決定論的コード生成に向けた外部構造化アプローチの有効性を示し、今後のLLM信頼性研究における基盤的知見を提供するものである。

---

## 参考文献
- Kamoi, R., et al. (2024). When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs. Transactions of the Association for Computational Linguistics. arXiv:2406.01297
- Huang, J., et al. (2024). Large Language Models Cannot Self-Correct Reasoning Yet. ICLR 2024. arXiv:2310.01798
- [Self-Correction Bench] (2025). Self-Correction Bench: Uncovering and Addressing the Self-Correction Blind Spot in Large Language Models. arXiv:2507.02778
- [Failure-Aware...] (2026). Failure-Aware Enhancements for Large Language Model (LLM) Code Generation: An Empirical Study on Decision Framework. arXiv:2602.02896
- Jiang, J., et al. (2025). A Survey on Large Language Models for Code Generation. arXiv:2406.00515 (v2: 2024/11更新)
- [Guidelines...] (2026). Guidelines to Prompt Large Language Models for Code Generation: An Empirical Characterization. arXiv:2601.13118
- [Prompt engineering...] (2025). Prompt engineering and framework: implementation to increase code reliability based guideline for LLMs. arXiv:2506.10989
- [A Survey on Code Generation with LLM-based Agents] (2025). A Survey on Code Generation with LLM-based Agents. arXiv:2508.00083
- [From Tool Calling...] (2025). From Tool Calling to Symbolic Thinking: LLMs in a Persistent Lisp Metaprogramming Loop. arXiv:2506.10021
- [Understanding...] (2025). Understanding and Mitigating Errors of LLM-Generated RTL Code. arXiv:2508.05266
- [LLM-Based Code Translation...] (2025). LLM-Based Code Translation Needs Formal Compositional Reasoning. EECS-2025-174, UC Berkeley.


---
