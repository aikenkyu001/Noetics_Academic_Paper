# **A Systematic Approach to Deterministic Code Generation in Large Language Models: A Study on the Effectiveness of Scaffolding Strategies**

**Author:** Fumio Miyata https://orcid.org/0009-0008-8797-5578  
**DOI:** [https://doi.org/10.5281/zenodo.18678188](https://doi.org/10.5281/zenodo.18678188)

---

## **Abstract**

This paper reports the results of an empirical investigation into improving the reliability of code generation in Large Language Models (LLMs), focusing on the challenge of *functional non-determinism*. We design a benchmark that evaluates semantic consistency between the formal language **Sigma-Lisp** and Python code, and we test two hypotheses. First, we examine the effectiveness of an **introspective approach**, in which the LLM analyzes and attempts to correct its own errors. Under our experimental conditions, this approach yields no significant improvement. Second, we evaluate an **external scaffolding approach**, in which model weaknesses are compensated through structured guidance. We find that programmatic error normalization and detailed implementation prompts effectively correct specific classes of logical errors.

Integrating these components, we construct a methodology combining the **Scaffolding Trinity** with a **two-stage temperature setting** (T=1.0 for NL→Lisp and T=0.0 for Lisp→Code). Applied to the most challenging NL→Lisp→Code pipeline, this method enables **gemma3:12b** to achieve an average success rate of 100% across 30 tasks (30/30; Clopper–Pearson 95% CI: [88.4%, 100%]).

This study demonstrates that, under precise external guidance, LLMs can consistently generate executable code under reproducible experimental conditions.

# **1 Introduction**

## **1.1 Background**

Large Language Models (LLMs) have demonstrated remarkable capabilities in software development support. However, their tendency to produce different outputs for the same input—*functional non-determinism*—remains a practical challenge. As illustrated in **Figure 1**, a single prompt may yield multiple code variants, some of which are incorrect. This variability is particularly problematic in engineering contexts, where reproducibility and stability are essential.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "Conceptual illustration of functional non-determinism in LLMs",
  "title": { "text": "Figure 1: Functional Non-Determinism in LLMs.", "anchor": "start" },
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

## **1.2 Research Objectives**

This study aims to answer two questions, based on the contrasting approaches illustrated in **Figure 2**:

1. Can LLMs autonomously correct logical errors through introspective prompting?  
2. Does external structural intervention (scaffolding) contribute to performance stabilization?

This work reports empirical observations rather than asserting theoretical generality.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "Conceptual comparison of introspection and external scaffolding",
  "title": {
    "text": "Figure 2: Introspection vs. External Scaffolding.",
    "anchor": "start"
  },
  "spacing": 40,
  "align": "all",
  "bounds": "flush",

  "hconcat": [
    {
      "title": {"text": "Introspective Approach", "fontSize": 14, "anchor": "middle"},
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
  "title": {"text": "External Scaffolding", "fontSize": 14, "anchor": "middle"},
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

# **1.3 Related Work**

Research on the reliability of LLM-based code generation can be broadly divided into two categories.

### **1.3.1 Self-Correction Approaches**

The first category investigates introspective methods in which LLMs attempt to detect and correct their own errors. Prior studies have highlighted significant limitations in this approach. In complex tasks such as multi-step reasoning and code generation, LLMs rarely succeed in self-correction without external feedback. Kamoi et al. (2024) report that models frequently fail to identify their own mistakes, exhibiting a “self-correction blind spot.” The Self-Correction Bench (2025) further shows that LLMs fail to correct errors in approximately 64.5% of cases. Some studies even observe performance degradation when introspection is applied to reasoning tasks (Huang et al., 2024). Other work suggests that external knowledge sources, such as retrieval-augmented generation, provide more reliable improvements (Failure-Aware Enhancements, 2026). The failures observed in Phases 4–6 of our study align with and extend these findings to the domain of code generation.

### **1.3.2 External Structure, Prompt Engineering, and Agent-Based Approaches**

The second category focuses on stabilizing LLM behavior through external structure, including prompt engineering, tool use, and agent frameworks. Empirical evidence shows that providing detailed I/O specifications, examples, and disambiguation instructions significantly improves code reliability (Guidelines, 2026; Prompt Engineering, 2025). Agent-based systems also leverage external tools and iterative loops to enhance task completion rates (A Survey on Code Generation with LLM-based Agents, 2025).

Our work belongs to this second category. Prior research highlights the importance of formal languages and meta-programming loops, such as Lisp-based symbolic reasoning (From Tool Calling to Symbolic Thinking, 2025), as well as the need for compositional reasoning in code translation (LLM-Based Code Translation, 2025). The **Scaffolding Trinity** proposed in this study integrates these ideas into a unified framework. A key novelty of our approach is that it achieves stability comparable to agent systems **without** relying on dynamic execution loops—using only static prompts and external scripts.

Code generation is particularly sensitive to functional non-determinism because code must satisfy strict syntactic and semantic constraints. Even minor deviations can lead to compilation or runtime errors. Unlike natural language generation, where variation is acceptable, code generation demands exact correctness. This inherent discreteness, combined with the probabilistic nature of LLMs, makes stabilization especially challenging.

---

# **1.4 Research Purpose**

This study aims to empirically evaluate whether external scaffolding can stabilize LLM code generation more effectively than introspective methods. We focus on two contrasting approaches:

- **Introspective control**, in which the model attempts to correct its own errors.  
- **External structural control**, in which the model is guided by formal specifications, grammar constraints, and explicit implementation instructions.

Our goal is not to propose a universal theory but to report reproducible empirical findings under controlled experimental conditions.

---

# **2 Experimental Design**

## **2.1 Benchmark Pipelines**

This study employs two types of pipelines:

- **Lisp⇔Code Pipeline (Phases 1–11)**  
  Used to evaluate round-trip translation between the formal language Sigma-Lisp and Python code, as well as the model’s self-correction capabilities.

- **NL→Lisp→Code Pipeline (Phase 12)**  
  The final evaluation pipeline, which generates code from natural language through an intermediate formal specification.

---

## **2.2 Task Set**

- Total tasks: **30**  
- Categories: dynamic programming, graph theory, backtracking, string processing, and others  
- Average number of test cases: **approximately 10 per task**  
- All experimental resources (definitions, scripts, and prompts) are publicly available at https://github.com/aikenkyu001/iterative_self_healing_benchmark

---

## **2.3 Evaluation Metrics**

- **Success definition:** Passing all test cases within a maximum of 10 cycles  
- **Trials:** 30 independent runs per task  
- **Success rate:** Average success rate across 30 trials

---

## **2.4 Operational Definition of Deterministic Behavior**

In this study, “deterministic” behavior is defined operationally rather than theoretically. A model is considered deterministic if it satisfies the following conditions:

- Under temperature **0.0**, the generated code is **token-identical** for the same input  
- The generated code **consistently passes all test cases**, producing identical execution results  
- The model achieves a **100% success rate across 30 independent trials**

This definition does not eliminate implementation dependencies such as differences in Ollama’s runtime or GPU hardware.

---

## **2.5 Two-Stage Temperature Setting**

To balance diversity and determinism, we adopt a two-stage temperature strategy:

- **T = 1.0** for the natural language → Sigma-Lisp stage, allowing expressive variability  
- **T = 0.0** for the Sigma-Lisp → Python code stage, maximizing determinism

The overall structure is shown in **Figure 3**.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",

  "title": {
    "text": "Figure 3: Two-Stage Temperature Pipeline.",
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

---

## **2.6 Reproducibility**

To ensure reproducibility, all experimental settings are explicitly documented. Inference was performed using Ollama with the model versions specified in this paper. Random seeds were fixed, and all LLM parameters except temperature (T=1.0 and T=0.0) were left at default values. All experimental resources, including prompts, scripts, and task definitions, are publicly available at https://github.com/aikenkyu001/iterative_self_healing_benchmark

---

# **3 Results**

## **3.1 Introspective Approach (Phases 4–6)**

Under the experimental conditions of this study, no successful cases were observed when introspective prompts were introduced. As shown in **Table 1**, the success rate across 30 tasks × 30 trials (900 total trials) was **0%**, representing a substantial degradation in performance. The overall trend in success rates across phases is illustrated in **Figure 4**.

**Table 1.Success Rate of the Introspective Approach.**

| Phase | Strategy        | Success Rate |
|-------|-----------------|--------------|
| 1–3   | Baseline        | 100%         |
| 4–6   | Introspection   | 0%           |

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "Success rate transitions across experimental phases",
  "title": {
    "text": "Figure 4: Success Rate Across Experimental Phases.",
    "anchor": "start"
  },
  "width": 500,
  "height": 300,
  "data": {
    "values": [
      {"phase_group": "Phase 1-3", "strategy": "Baseline", "success_rate": 100},
      {"phase_group": "Phase 4-6", "strategy": "Introspection", "success_rate": 0},
      {"phase_group": "Phase 7-12", "strategy": "External Scaffolding", "success_rate": 100}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {
      "field": "phase_group",
      "type": "ordinal",
      "title": "Phase Group",
      "sort": null
    },
    "y": {
      "field": "success_rate",
      "type": "quantitative",
      "title": "Success Rate (%)",
      "axis": {"titleOrient": "bottom"},
      "scale": {"domain": [0, 100]}
    },
    "color": {
      "field": "strategy",
      "type": "nominal",
      "title": "Strategy",
      "scale": {
        "domain": ["Baseline", "Introspection", "External Scaffolding"],
        "range": ["#1f77b4", "#ff7f0e", "#2ca02c"]
      }
    },
    "tooltip": [
      {"field": "phase_group", "title": "Phase Group"},
      {"field": "strategy", "title": "Strategy"},
      {"field": "success_rate", "title": "Success Rate", "format": ".1f"}
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

## **3.2 External Scaffolding (Phases 7 and 9)**

After introducing external correction scripts, performance returned to baseline levels, as shown in **Table 2**.

**Table 2.Performance Recovery Through External Intervention.**

| Phase | Strategy          | Success Rate |
|-------|-------------------|--------------|
| 4–6   | Introspection     | 0%           |
| 7, 9  | External Support  | 100%         |

---

## **3.3 Final Pipeline (Phase 12)**

The performance of each model in the final NL→Lisp→Code pipeline is shown in **Table 3**.

**Table 3.Model Performance in the Final Pipeline.**

| Model                 | Success (30 Trials) | Success Rate |
|-----------------------|----------------------|--------------|
| gemma3:12b            | 30/30                | 100%         |
| llama3.2-vision:11b   | 25/30                | 83%          |
| llama3:8b             | 22/30                | 73%          |

The gemma3:12b model succeeded in all trials (30/30), with a Clopper–Pearson 95% confidence interval of **[88.4%, 100%]**, computed using the exact method for the binomial distribution.

---

# **4 Discussion**

The results indicate that external structural guidance is more effective than introspective mechanisms for stabilizing LLM behavior. The most significant finding of this study is the contrast between **internal control** (introspection) and **external control** (scaffolding): introspection degrades performance, whereas external structure restores and stabilizes it. This contrast resembles principles in control theory, where external constraints can compensate for internal instability.

In particular, the **Scaffolding Trinity**, shown in **Figure 5**, supports the hypothesis that structured external guidance contributes to improved stability:

- **Specification Scaffold:** Structured design documents  
- **Grammar Scaffold:** Formal language extensions using Sigma-Lisp  
- **Execution Scaffold:** Explicit implementation instructions and the two-stage temperature strategy  

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "Components of the Scaffolding Trinity",
  "title": {"text": "Figure 5: Components of the Scaffolding Trinity.", "anchor": "start"},
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

These findings are specific to the models and settings used in this study and are not intended to generalize across all LLMs. Prior work on Lisp-based meta-programming loops (From Tool Calling to Symbolic Thinking, 2025) suggests that formal languages can enhance symbolic reasoning in LLMs. Other studies report that many LLM-generated code errors stem from insufficient domain knowledge and can be mitigated through external structure (Understanding and Mitigating Errors, 2025). The Scaffolding Trinity applies similar insights to general algorithmic tasks and demonstrates their effectiveness.

Research on code translation emphasizes the need for formal compositional reasoning (LLM-Based Code Translation, 2025). The two-stage pipeline using Sigma-Lisp enforces such formality, contributing to deterministic code generation in this study.

Overall, this work highlights the potential of structural design—not model improvement—to control LLM behavior.

---

# **5 Limitations**

This study has several limitations.  
First, the experiments focus primarily on the gemma and llama model families.  
Second, all prompts were evaluated only in English.  
Third, the specification scaffold was manually constructed.  
Fourth, the scaffolding components were tailored to the specific tasks used in this study, and additional design work would be required for broader generalization.  
Finally, the automation of the proposed methodology has not yet been examined.

---

# **6 Conclusion**

Under the experimental conditions of this study, introspection alone did not stabilize LLM behavior. In contrast, the introduction of external scaffolding resulted in consistently successful outcomes. With the Scaffolding Trinity and the two-stage temperature strategy, **gemma3:12b** achieved operationally defined deterministic success across 30 diverse algorithmic tasks.

This paper reports empirical observations rather than asserting theoretical universality. Future work includes automating the methodology and evaluating its applicability to other model families. The findings highlight the effectiveness of external structural approaches for deterministic code generation in LLMs and provide foundational insights for future research on LLM reliability.

---

# **References**

Kamoi, R., et al. (2024). *When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs.* Transactions of the Association for Computational Linguistics. arXiv:2406.01297

Huang, J., et al. (2024). *Large Language Models Cannot Self-Correct Reasoning Yet.* ICLR 2024. arXiv:2310.01798

Self-Correction Bench. (2025). *Self-Correction Bench: Uncovering and Addressing the Self-Correction Blind Spot in Large Language Models.* arXiv:2507.02778

Failure-Aware Enhancements. (2026). *Failure-Aware Enhancements for Large Language Model (LLM) Code Generation: An Empirical Study on Decision Framework.* arXiv:2602.02896

Jiang, J., et al. (2025). *A Survey on Large Language Models for Code Generation.* arXiv:2406.00515 (v2 updated 2024/11)

Guidelines. (2026). *Guidelines to Prompt Large Language Models for Code Generation: An Empirical Characterization.* arXiv:2601.13118

Prompt Engineering. (2025). *Prompt Engineering and Framework: Implementation to Increase Code Reliability Based on Guidelines for LLMs.* arXiv:2506.10989

A Survey on Code Generation with LLM-based Agents. (2025). *A Survey on Code Generation with LLM-based Agents.* arXiv:2508.00083

From Tool Calling to Symbolic Thinking. (2025). *From Tool Calling to Symbolic Thinking: LLMs in a Persistent Lisp Metaprogramming Loop.* arXiv:2506.10021

Understanding and Mitigating Errors. (2025). *Understanding and Mitigating Errors of LLM-Generated RTL Code.* arXiv:2508.05266

LLM-Based Code Translation. (2025). *LLM-Based Code Translation Needs Formal Compositional Reasoning.* EECS-2025-174, UC Berkeley
