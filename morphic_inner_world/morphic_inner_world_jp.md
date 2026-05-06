# Morphic Inner World：幾何学的項代数射影による言語およびプラットフォーム不変な決定論的知能の実現

**著者:** Fumio Miyata  
**日付:** 2026年3月10日  
**DOI:** https://doi.org/10.5281/zenodo.18905026  
**キーワード:** 認知アーキテクチャ、記号推論、項代数、合成性、決定論的推論、言語不変性、プラットフォーム不変性

---

## 概要
信頼性の高い合成的推論は、人工知能における中心的な課題であり続けている。現代の大規模言語モデルは優れた言語能力を示す一方で、深く入れ子になった構造や複雑なタスクにおいて不安定性を示すことが多い。本論文では、**「言語およびプラットフォーム不変な決定論的知能」**の可能性を探索する認知アーキテクチャ、**Morphic Inner World (MIW)** を提案する。本フレームワークは、推論を自然言語から自由項代数として定義される記号推論空間への構造保存的な**「幾何学的射影」**としてモデル化する。戦略的最長一致トークナイザ、**44 個の既約なプリミティブ**、およびデカップリングされた**「知恵の基底 (Wisdom Base)」**を用いることで、MIW は複数の言語（英語/日本語）と実行カーネル（Python/Fortran）にわたって高度な論理の一貫性を提供することを目指す。定義されたベンチマークの範囲内における 60 の課題を用いた評価では、100.0% の精度とビットレベルの一致を伴う決定論的推論が達成され、論理的実体をその言語的および物理的な基盤から効果的にデカップリングできることが示された。

---

## 1. 緒言
現代のニューラル言語モデルは、特に精密な構造操作を必要とするタスクにおいて、**系統的な合成的推論**に苦慮している (Lake & Baroni, 2018; Liu et al., 2023)。これらの限界は、強固な構造的アンカーを欠いたトランスフォーマーベースのアーキテクチャの確率的性質に起因すると考えられる (Baroni, 2022)。歴史的に、**ACT-R** (Anderson et al., 2004) や **SOAR** (Langley et al., 2009; Ludwig, 2005) といった認知アーキテクチャは 40 年以上にわたって構造化された枠組みを提供してきたが (Kotseruba & Tsotsos, 2020)、多くの場合、ヒューリスティックな探索に依存していた。近年の**「決定論的人工知能」** (Alexander, 2020) や**「適応型マシンインテリジェンス」** (Bhatnagar, 2025) の研究は、ビットレベルの再現性と形式的な由来（プロベナンス）を機械推論に導入することの重要性を強調している (Marcus, 2020)。本論文では、推論を項代数多様体における**決定論的な代数的簡約**としてモデル化する MIW を提案する (Gurevich, 1995; Abadi & Plotkin, 2020)。その論理的なルーツは、形式論理学の基礎を築いた**論理的公理系** (Church, 1932) にまで遡ることができる。

---

## 2. アーキテクチャと形式モデル

### 2.1 全体フロー
MIW アーキテクチャは、単方向の 3 段階パイプライン（図 1）を通じて入力を処理する。情報理論的な観点からは、このプロセスは高エントロピーな言語入力から、低エントロピーで構造化された論理正規形への遷移として捉えることができる (Tononi, 2004; Saanum et al., 2024)。この遷移は、**「調和する精神」** (Smolensky & Legendre, 2006) のアーキテクチャ原理に支配されている。

![図 1](images/fig1_global_flow.pdf)
**図 1: Morphic Inner World の全体構成。** 曖昧な自然言語から、構造保存的な段階を経て検証済みの正規形へと至る決定論的なプロセスを示す。

### 2.2 入力射影と MSP チェック
射影フェーズ $h: \mathcal{L} \to \Sigma^*$ は厳密に決定論的な自然言語となるよう設計されており、以下の要素を用いる：
1.  **戦略的最長一致トークナイズ**: 複雑なパーサーなしで意味の曖昧さを解消するため、辞書内のフレーズは照合前に文字数の降順でソートされる。これは、汎用的な構成要素よりも具体的な意味型を優先するカテゴリ文法的なアプローチ (Steedman, 2000) に着想を得ている。この決定論的写像は、ハイブリッド認知システムにおける**構造的表現** (Licato et al., 2014) や**普遍文法** (Montague, 1970) の原理と整合する。
2.  **MSP (Morphic Structural Pointers)**: 「1.」「2.」などの番号付きマーカーが構造的アンカーとして機能する。シンセサイザーはこれらのアンカーの外側にあるテキストを背景ノイズとして処理するように構成されている。このプロトコルは、8,000 トークンを超える非構造化テキストを含むドキュメントからでも、正確な論理を抽出することを目的としており、長文コンテキストにおける「Lost in the Middle」現象 (Liu et al., 2023) を解消し、熟慮的推論のための**言語構造**を確実に保存する (Baroni, 2022; Boggs, 2025)。

### 2.3 モルフィック・プリミティブと知恵の基底 (Wisdom Base)
辞書は、**44 個の既約なプリミティブ** ($\Sigma$) で構成される。この 44 個のセットは、ベンチマーク・スイート全体で観察された記号操作を反復的に簡約することによって導出された。各プリミティブは、追加の構造的曖昧さを導入することなく分解することができない既約な変換を表している。本研究は厳密な代数的意味での最小性を主張するものではないが、このセットは評価された推論タスクに対して安定した操作基底を提供する。

重要なアーキテクチャ上の特徴は、抽象的なプリミティブ ID をプラットフォーム固有の実装に写像するデカップリング層、**「知恵の基底 (Wisdom Base: WB)」** である（図 2）。このレジストリは、同一の普遍的な論理構造 (AST) を、機能的等価性を維持したまま、カーネル間 (Python と Fortran) で異なる実体としてインスタンス化できるよう設計されている。この手法は、**決定論的な自己反照性** (Bhatnagar, 2025) を基礎としている。

![図 2](images/fig2_substrate.pdf)
**図 2: 基盤非依存レイヤーの構造。** 知恵の基底が認知レジストリとして機能し、ユニバーサルな論理 (AST) をプラットフォーム固有の実行カーネルからデカップリングすることで、実装不変性を保証する。

さらに、MIW は実行カーネルの境界で**「セマンティック・クレンジング（意味論的洗浄）」**を採用しており、評価前にネイティブ入力データを正規化することを目指している。複雑な再帰アルゴリズムは、内部的な構造再帰をカプセル化した原子的なプリミティブである**「不動点パッケージ (Fixpoint Packages)」**として扱われる。このカプセル化により、シンセサイザーから見た構造的複雑性が一定に保たれ、高度に複雑なタスクにおいても管理可能な論理フローを維持することが可能になる。この集合が自由項代数 $\mathcal{M} = \mathcal{T}(\Sigma, \mathcal{V})$ の基底となり、代数的な表現による**系統的な般化** (Zhang et al., 2022) や普遍的な知識モデル (Sukhobokov, 2024) を可能にする。

---

## 3. 構造合成と評価意味論
合成 $g: \Sigma^* \to \mathcal{M}$ は、必須のアリティ制約 $\alpha(P)$ を満たす記号木を構築する（図 3）。合成エンジンは**アリティに基づく部分適用**を利用しており、全ての必須引数が提供されるまで、関数はクロージャ ($VClosure$) へへと変換される。これにより、線形の自然言語フレーズから論理を動的に構成することを容易にしている。これは、組立的般化の**二重過程モデル** (Novello et al., 2025) によって支持されている。

![図 3](images/fig3_folding.pdf)
**図 3: 再帰的フォールディングの論理。** 入力される引数に対してアリティ制約 $\alpha(P)$ を厳密に検証することで、プリミティブをユニバーサルな論理形式へと再帰的に構成する。

さらに、論理ステップは入れ子になった `Let` 結合を用いて**不変 DAG 構造**として構成される。これは、各中間結果を不変な名前付きオブジェクトとし、副作用を排除して計算された値の明確な系統を提供することを目的としている。評価は、終止性と合流性が保証された決定論的な書き換え規則 $R_P$ (Landin, 1964; Baader & Nipkow, 1998) を通じて実行される。この形式的評価プロセスは、 Gordon Plotkin による**構造的操作意味論 (SOS)** (Plotkin, 1977) や、**型としての命題** (Wadler, 2015) の原理に深く根ざしている。

---

## 4. 合成的推論の具体例
MIW は、単純なソート以外の多様な推論カテゴリーに適用された：
- **アルゴリズム**: `FILTER(EVEN, SORT(numbers))`。
- **空間推論**: `DIJKSTRA(graph, start, end)`。
- **制約充足**: `SOLVE_SUDOKU(grid)`。
- **最適化**: `TREE_MAX_PATH(root)`。

線形なタスク記述から形式的な結果への具体的な変換プロセスは、実行トレース（図 4）として可視化され、システムが熟慮的な**視覚的・記号的推論** (Boggs, 2025) を維持する能力を示している。

![図 4](images/fig4_trace.pdf)
**図 4: 実行トレース・パイプライン。** 活動選択問題を例に、自然言語フレーズからプリミティブ ID へのマッピング、および最終的に生成されるユニバーサルな論理形式への遷移を追跡する。

---

## 5. 実験的評価
MIWの評価は、算術変換、論理推論、構造解析、および記号操作を網羅する60の決定論的推論タスクを用いて行われた。本ベンチマーク・スイートは、多様な領域における決定論的な記号合成をストレス・テストするため、構造的な深さやアルゴリズムの性質が異なるタスクを意図的に含んでいる。タスクの詳細および評価手法については、付録 A に詳述する。図 5 に示す通り、MIWはテストされた全ての複雑性スケールにおいて絶対的な信頼性（精度 100.0%）を維持した。本研究の範囲内において、全てのタスクはビットレベルのパリティを検証するために複数のプラットフォーム（Python および Fortran）で実行され、実装不変性が確認された (Baumgartner et al., 2025)。全てのベンチマーク・タスク、実行ログ、およびカーネル実装は、Zenodo アーカイブ (DOI) および付随するソース・リポジトリを通じて公開されている。ここで強調すべき点は、報告された 100% の精度は本研究で定義されたベンチマーク・タスクに厳密に限定されるものであり、一般的な問題解決の完全性を主張するものではなく、定義されたプリミティブ・システム内における決定論的な合成の正当性の証拠として解釈されるべきであるということである。

![図 5](images/fig5_reliability.pdf)
**図 5: 信頼性 vs 複雑性の対比。** 先行研究ではニューラルモデルが深く入れ子になった推論タスクにおいて性能劣化を示すことが報告されているが (Liu et al., 2023)、MIW は評価されたベンチマークの範囲内において絶対的な信頼性 (100.0% の精度) を維持する。

---

## 6. 考察

### 6.1 言語不変性 (Language Invariance)
本研究の日英両言語の仕様において達成された 100.0% の一致は、**言語制形態（Form）と論理的実体（Substance）の根本的なデカップリング**（図 6）に関する実証的証拠を提供している。これはデータ至上主義の時代における意味（Meaning）と理解（Understanding）の批判的な区別 (Bender & Koller, 2020) を浮き彫りにするものである。MIW フレームワークにおいて、自然言語は論理プリミティブを配置し起動するための座標系として機能する。この**「言語不変性（Language Invariance）」**は、正式な AST として表現される「推論の幾何学」が、伝達に使用される特定の言語の殻から独立した普遍的な不変量として機能し得ることを示唆している。本稿において、**「推論の幾何学」とは、項代数空間への射影後に得られる不変な AST 構造（正規形）を具体的に指し**、意図の既約な論理的本質を表現している。この概念は**論理フレームワーク (LF)** (Harper et al., 1987) や **Institution 理論** (Goguen & Burstall, 1992) によって裏付けられている。

![図 6](images/fig6_manifold.pdf)
**図 6: 言語不変性の多様体。** 英語と日本語の仕様が同一のユニバーサルな論理形式へと射影され、最終的に同一の正規化された真理へと収束する幾何学的整合性を示す。

### 6.2 プラットフォーム不変性 (Platform Invariance)
Python と Modern Fortran という対照的なパラダイム間での**ビットレベルの完全一致**の達成は、**「プラットフォーム不変性（Platform Invariance）」**（図 7）の概念を支持している。これは、論理の正規形への簡約が、特定の計算環境の慣習を超越した数学的必然となり得ることを示している。「推論の論理」を「実行のメカニズム」からデカップリングすることで、MIW は、決定論的知能を下層構造から解放する可能性を示し、クロスプラットフォームな認知的検証のための基盤を提供している (Alexander, 2020; Bhatnagar, 2025)。これは、合成的推論が、物理的な基盤に関わらず既約な結果へと収束する、決定論的な構造保存写像として実装可能であることを証明している。

![図 7](images/fig7_manifold.pdf)
**図 7: 決定論的カーネル・パリティ。** 単一のユニバーサルな論理形式が独立した実行カーネル（Python および Fortran）によって処理され、共にビットレベルで同一の正規形へと収束する。

### 6.3 限界 (Limitations)
本研究は構造化された記号タスクに焦点を当てており、知覚的な接地（Perceptual Grounding）やオープンドメインの言語理解には対応していない。さらに、プリミティブ・セットは依然としてドメイン固有であり、より広範な推論領域に対しては拡張やさらなる般化が必要となる可能性がある。本報告における 100% の精度は、特定のベンチマーク・スイートおよび本ワークで定義された形式的プロトコルの範囲内に限定されたものである。

---

## 7. 結論
MIW は、合成的推論が決定論的な構造保存写像として実装可能であるという証拠を提供している。今後の課題は、構造的接地と知覚的接地を橋渡しするために、確率的モデルとのハイブリッド化 (Bengio et al., 2020) を調査し、**記号接地問題** (Harnad, 1990) にアプローチすることである。さらに、今後の展望として、Morphic アーキテクチャのスケーラビリティをさらに検証するため、より大規模な記号推論データセットへとベンチマークを拡張することを目指す。また、モルフィック・コア言語への **「層理論 (Sheaf Theory)」** (Shkursky, 2025) の導入により、複雑で重複する環境多様体を扱うことが可能な、より汎用的な **「幾何学的認知 (Geometric Cognition)」** (Dhar et al., 2025) への道が、**創発的知能**のためのアーキテクチャ COGENT3 (Salazar, 2025) や、神経形態学的工学 (Indiveri & Liu, 2021; Sandamirskaya, 2014) を通じて開かれるかもしれない。

---

## データの可用性に関する宣言
MIW カーネル（Python および Modern Fortran）の完全なソースコード、60 のアルゴリズムタスクからなるベンチマークスイート、および合成・実行ログは、査読および再現のために以下のリポジトリで公開されている： [https://github.com/aikenkyu001/morphic_inner_world](https://github.com/aikenkyu001/morphic_inner_world)。また、データセットは Zenodo でもアーカイブされている (DOI: [10.5281/zenodo.18905026](https://doi.org/10.5281/zenodo.18905026))。

---

## 付録 A：評価手法とタスクの詳細

### A.1 タスク・カテゴリー
60 のベンチマーク・タスクは、記号推論の広がりをテストするために、主に以下の 4 つの領域に分類される。

| カテゴリー | タスク数 | 説明 |
| :--- | :---: | :--- |
| 算術推論 (Arithmetic) | 10 | 数式の正規化と簡約の検証。 |
| 論理推論 (Logical) | 15 | 複雑なブール制約と述語の評価。 |
| 構造変換 (Structural) | 20 | 入れ子構造（リスト、木）の解析と再構築。 |
| 記号操作 (Symbolic) | 15 | 高度なアルゴリズムの執行（Dijkstra, 数独等）。 |

### A.2 タスクの具体例
射影プロセスを具体化するため、以下の特定のタスクを例示する。

**タスク 12: 算術正規化**
*   **入力**: "three plus five times two"（3足す5掛ける2）
*   **論理フロー**: `1. multiply 5 by 2`, `2. add result to 3`
*   **期待される表現**: `ADD(3, MUL(5, 2))`
*   **結果**: `13`

### A.3 決定論的実行と難易度
全てのタスクは決定論的記号推論をテストするために手動で構成されており、ビットレベルのパリティを検証するために複数のプラットフォーム（Python および Fortran）で実行された。

| タスク・カテゴリー | 難易度 | 推論の深さ |
| :--- | :---: | :---: |
| 算術 (Arithmetic) | 低 (Low) | 浅い (Shallow) |
| 論理 (Logical) | 中 (Medium) | 標準 (Moderate) |
| 構造 (Structural) | 中 (Medium) | 深い (Deep/Nested) |
| 記号 (Symbolic) | 高 (High) | 複雑 (Complex/Recursive) |

---

## 付録 B：形式的簡約意味論
評価プロセスを **正規形 (Normal Form: NF)** への簡約として定義する。評価関数 $Eval: \mathcal{T}(\Sigma, \mathcal{V}) \to NF$ は、原子リテラル $c$ に対して $Eval(c) = c$、適用 $P(t_1, ..., t_n)$ に対して $Eval(P(t_1, ..., t_n)) = R_P(Eval(t_1), ..., Eval(t_n))$ と定義される。有限のアリティ制約と書き換え規則の直交性 (Baader & Nipkow, 1998) により、終止性と合流性が保証される。この簡約は「型としての命題」 (Wadler, 2015) の原理に従う。

絶対的な予測可能性を維持するため、MIW は**決定論的エラーハンドリング**（図 8）を採用している。未定義の操作や型不一致が発生した場合、評価器はシステムレベルの例外を発生させる代わりに **VError** 値を返す。このアプローチはエラーを論理内の正当な状態として扱い、障害条件下でもカーネルがクラッシュせず、常に明確に定義された結果を生成することを保証する (Bhatnagar, 2025)。

![図 8](images/fig8_error.pdf)
**図 8: 決定論的エラーフロー。** MIW はユニバーサルな論理形式を通じて VError オブジェクトを伝播させ、安全かつ予測可能な終了を維持する。

## 付録 C：モルフィック・プリミティブ ($\Sigma$) 全リスト
| プリミティブ | アリティ | プリミティブ | アリティ |
| :--- | :---: | :--- | :---: |
| autocomplete_trie | 2 | matrix_chain | 1 |
| bitmask_group | 1 | merge_intervals | 1 |
| bitwise_range_and | 2 | merge_k_lists | 1 |
| boggle_solve | 2 | mergesort | 1 |
| check_constraints | 1 | mst_prim | 2 |
| composite_task_60 | 2 | optimal_bst | 1 |
| deserialize_tree | 1 | permute_dup | 1 |
| dijkstra | 3 | process_context | 2 |
| filter_overlapping | 1 | quicksort | 1 |
| flatten_nesting | 1 | rain_3d | 1 |
| fractional_knapsack | 2 | reconstruct_list | 1 |
| identity | 1 | redundant_conn | 1 |
| is_valid_parentheses | 1 | regex_match | 2 |
| kth_largest | 2 | rotate_matrix | 1 |
| ladder_all | 3 | serialize_tree | 1 |
| lca_nary | 3 | solve_sudoku | 1 |
| lcs | 2 | sort_by_end | 1 |
| length | 1 | sparse_mul | 2 |
| lru_cache_concurrent | 2 | spiral_gen | 1 |
| lru_cache_op | 2 | text_justify | 2 |
| tree_max_path | 1 | word_break | 2 |
| word_ladder_bfs | 3 | word_search_2 | 2 |

---

## 参考文献

- Abadi, M., & Plotkin, G. (2020). A simple differentiable programming language. *arXiv preprint*.
- Alexander, D. R. (2020). Deterministic artificial intelligence. *IntechOpen*.
- Anderson, J. R., et al. (2004). An integrated theory of the mind. *Psychological Review*, 111, 1036–1060.
- Baader, F., & Nipkow, T. (1998). *Term Rewriting and All That*. Cambridge University Press.
- Baroni, M. (2022). On the proper role of linguistically-oriented deep net analysis in linguistic theorizing. *arXiv preprint*.
- Baumgartner, P., et al. (2025). The AlphaPhysics term rewriting system for marking algebraic proofs. *arXiv preprint*.
- Bender, E. M., & Koller, A. (2020). Climbing towards NLU. *Proceedings of the ACL*.
- Bengio, Y., et al. (2020). Thinking fast and slow in AI. *arXiv preprint*.
- Bhatnagar, K. (2025). The RAM cognitive architecture: A deterministic, self-reflective paradigm for adaptive machine intelligence. *Zenodo*.
- Boggs, J. M. (2025). Deliberate visual-symbolic reasoning in a cognitive architecture (Doctoral dissertation). *University of Michigan*.
- Church, A. (1932). A set of postulates for the foundation of logic. *Annals of Mathematics*, 33, 346–366.
- Dhar, R., et al. (2025). Toward a sheaf-theoretic understanding of compositionality in large language models. *OpenReview*.
- Fabiano, F., et al. (2024). Plan-SOFAI: A neuro-symbolic planning architecture. *OpenReview*.
- Goguen, J. A., & Burstall, R. M. (1992). Institutions: Abstract model theory for specification and programming. *Journal of the ACM, 39*(1), 95–146.
- Gurevich, Y. (1995). Evolving algebras: A tutorial introduction. *Microsoft Research*.
- Harnad, S. (1990). The symbol grounding problem. *Physica D: Nonlinear Phenomena*, 42, 335–346.
- Harper, R., Honsell, F., & Plotkin, G. (1987). A framework for defining logics. *Journal of the ACM, 40*(1), 143–184.
- Indiveri, G., & Liu, S.-C. (2021). Introducing 'Neuromorphic Computing and Engineering'. *Neuromorphic Computing and Engineering*, 1(1), 010001.
- Kotseruba, I., & Tsotsos, J. K. (2020). 40 years of cognitive architectures. *AI Review*, 53(1), 17–94.
- Lake, B. M., & Baroni, M. (2018). Generalization without systematicity. *Proceedings of ICML*.
- Landin, P. J. (1964). The mechanical evaluation of expressions. *The Computer Journal*, 6(4), 308–320.
- Langley, P., et al. (2009). Cognitive architectures: Research issues and challenges. *Cognitive Systems Research, 10*(1), 141–160.
- Licato, J., et al. (2014). Structural representation and reasoning in a hybrid cognitive architecture. *IJCNN*.
- Liu, N. F., et al. (2023). Lost in the Middle. *TACL*.
- Ludwig, J. (2005). Psychologically inspired symbolic cognitive architectures. *University of Oregon Computer Science Reports*.
- Marcus, G. (2020). The next decade in AI: Four steps towards robust artificial intelligence. *arXiv preprint*.
- Novello, A., et al. (2025). A neuroscience-inspired dual-process model of compositional generalization. *arXiv preprint*.
- Plotkin, G. D. (1977). A structural approach to operational semantics. *University of Edinburgh*.
- Saanum, T., et al. (2024). Simplifying latent dynamics with softly state-invariant world models. *NeurIPS*.
- Salazar, E. (2025). Introducing COGENT3: An AI architecture for emergent cognition. *arXiv preprint*.
- Sandamirskaya, Y. (2014). Dynamic neural fields as a step toward cognitive neuromorphic architectures. *Frontiers in Neuroscience*, 7, 276.
- Shkursky, A. (2025). The distinction field: A unified architecture of cognition and reality. *PhilArchive*.
- Sinha, S., & d'Avila Garcez, A. (2025). Neuro-symbolic frameworks: Conceptual characterization and empirical comparative analysis. *Neuro-Symbolic Artificial Intelligence Journal*.
- Sukhobokov, A. (2024). A universal knowledge model and cognitive architecture for prototyping AGI. *arXiv preprint*.
- Tononi, G. (2004). An information integration theory of consciousness. *BMC Neuroscience*, 5, 42.
- Wadler, P. (2015). Propositions as Types. *Communications of the ACM*, 58(12), 75–84.
- Wu, S., et al. (2025). Toward human-like artificial intelligence by integrating cognitive architectures and large language models. *Neuro-Symbolic AI Journal*.
- Yang, X. W., Liu, J. Y., Wang, Y., & Chen, Y. (2025). Neuro-symbolic artificial intelligence. *IJCAI*.
- Zhang, C., yu, Y., Zhang, Z., & Cao, Z. (2022). Learning algebraic representation for systematic generalization in abstract reasoning. *European Conference on Computer Vision (ECCV)*.
