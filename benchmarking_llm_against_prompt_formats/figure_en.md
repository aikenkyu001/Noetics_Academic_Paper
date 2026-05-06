```mermaid
graph TD
    A["Input: Natural Language Prompt<br>(en, ja, eo, jbo) x (Imperative/Conversational)"] --> B{LLM};
    B --> C["Output: Python Function Code"];
    C --> D{Automated Verification by Pytest};
    D --> E["Result: Success / Failure"];
```

```mermaid
graph TD
    A["Input: Prompt specifying filter conditions and strict output format<br>e.g., 'Return a list string of even numbers that are not 8'"] --> B{LLM};
    B --> C["Output: A string, not Python code<br>e.g., '[2, 4, 6, 10, ...]'"];
    C --> D{Exact Match Verification with Expected String};
    D --> E["Result: Success / Failure"];
```

```mermaid
graph TD
    subgraph Input Prompt
        A1["Rule Set (S-expression format)"]
        A2["Rule Set (JSON format)"]
        A3["Rule Set (TSV format, etc.)"]
    end
    A1 --> B{LLM};
    A2 --> B;
    A3 --> B;
    B --> C["Output: Python function implementing the rules"];
    C --> D{Automated Verification by Pytest};
    D --> E["Result: Success / Failure"];
```

```mermaid
graph TD
    A["<b>Input: A single, long prompt</b><br>Containing: 1. A puzzle in an unknown token language, 2. Grammar rules for the language, and 3. An example solution using a backtracking algorithm"] --> B{LLM};
    subgraph "Internal Tasks for the LLM"
        B1["<b>Task 1: Grammar Learning</b><br>Interpret token language rules"]
        B2["<b>Task 2: Algorithm Learning</b><br>Extract backtracking structure from the example"]
        B3["<b>Task 3: Code Implementation</b><br>Combine grammar and algorithm to implement a Python solver"]
    end
    B --> B1 --> B2 --> B3;
    B3 --> C["Output: Final Python solver code"];
    C --> D{Automated Verification by Pytest};
    D -- "Runtime Error (e.g., KeyError)" --> E["Result: Failure"];
```

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Overall Performance Ranking",
  "height": 500,
  "data": {
    "values": [
      {"Model": "yi:6b", "OverallSuccessRate": "74.42%"},
      {"Model": "gemma3:4b", "OverallSuccessRate": "73.75%"},
      {"Model": "llama3.2:3b", "OverallSuccessRate": "70.42%"},
      {"Model": "falcon3:3b", "OverallSuccessRate": "70.00%"},
      {"Model": "gemma:7b", "OverallSuccessRate": "70.00%"},
      {"Model": "deepseek-r1:8b", "OverallSuccessRate": "68.17%"},
      {"Model": "llama3:8b", "OverallSuccessRate": "67.42%"},
      {"Model": "mistral:7b", "OverallSuccessRate": "52.50%"},
      {"Model": "llama2:7b", "OverallSuccessRate": "45.00%"},
      {"Model": "deepseek-r1:1.5b", "OverallSuccessRate": "40.00%"},
      {"Model": "deepseek-llm:7b", "OverallSuccessRate": "35.00%"},
      {"Model": "stablelm2:1.6b", "OverallSuccessRate": "33.17%"},
      {"Model": "smollm:360m", "OverallSuccessRate": "32.50%"},
      {"Model": "gemma:2b", "OverallSuccessRate": "30.00%"},
      {"Model": "gemma3:270m", "OverallSuccessRate": "27.50%"},
      {"Model": "tinyllama:1.1b", "OverallSuccessRate": "15.00%"},
      {"Model": "qwen:4b", "OverallSuccessRate": "12.50%"},
      {"Model": "phi3:mini", "OverallSuccessRate": "7.50%"},
      {"Model": "qwen:1.8b", "OverallSuccessRate": "5.08%"},
      {"Model": "qwen:0.5b", "OverallSuccessRate": "5.00%"}
    ]
  },
  "transform": [
    {"calculate": "toNumber(replace(datum.OverallSuccessRate, '%', '')) / 100", "as": "SuccessRate"}
  ],
  "mark": "bar",
  "encoding": {
    "y": {
      "field": "Model",
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
      {"field": "Model", "type": "nominal", "title": "Model"},
      {"field": "SuccessRate", "type": "quantitative", "format": ".2%"}
    ]
  }
}
```