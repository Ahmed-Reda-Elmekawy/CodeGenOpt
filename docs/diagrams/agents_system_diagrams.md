# CodeGenOpt Agents System — Comprehensive Diagrams

This document contains multiple diagrams describing the agents system located at `core/agents` (both cloud and local variants). Diagrams are authored in Mermaid to simplify rendering in Markdown previewers and the Mermaid Live Editor.

Contents:

- Context diagram
- Component diagram
- Sequence diagram (pipeline run)
- Activity diagram (control flow)
- Class diagram (key classes)
- Deployment diagram (local vs cloud)
- Data flow diagram
- Coordinator state machine

Render tips:

- VS Code: Install “Markdown Preview Mermaid Support” and open preview.
- Web: Copy a diagram block into https://mermaid.live/ to render.

---

## 1) Context Diagram

```mermaid
graph TD
    %% Actors
    U[User] -->|Task description| C[Coordinator System]

    %% Coordinator and Internal Agents
    subgraph Internal_Agents [Coordinator & Internal Agents]
        C --> TT[Technical Translator - optional]
        C --> PE[Prompt Engineer]
        C --> CG[Code Generator]
        C --> CO[Code Optimizer - optional]
    end

    %% External Systems
    subgraph External_Services [External SLM Services]
        LCL[Local Ollama SLM]
        CCL[Cloud SLM via Ollama Proxy]
    end

    subgraph Optimization_Tools [External Python Tools]
        OPT[Formatting & Static Analysis Tools]
    end

    %% Flows to LLMs
    TT --> LCL
    PE --> LCL
    CG --> LCL

    TT --> CCL
    PE --> CCL
    CG --> CCL

    %% Optimizer tools
    CO --> OPT

    %% Output back to user
    C -->|Final Python code| U

```

---

## 2) Component Diagram (Agents and Interactions)

```mermaid
graph LR
    C[Coordinator]
    TT[Technical Translator]
    PE[Prompt Engineer]
    CG[Code Generator]
    CO[Code Optimizer]
    LLM[Ollama LLM local or cloud]
    Tools[black, isort, autoflake, autopep8, pyupgrade, mypy]
    U[User]

    C --> TT
    C --> PE
    C --> CG
    C --> CO

    TT --> LLM
    PE --> LLM
    CG --> LLM
    CO --> Tools

    U --> C
    C --> U
```

---

## 3) Sequence Diagram (Coordinator.run)

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant C as Coordinator
    participant TT as TechnicalTranslator (opt)
    participant PE as PromptEngineer
    participant CG as CodeGenerator
    participant CO as CodeOptimizer (opt)

    U->>C: run(task_description)
    alt Translator enabled
        C->>TT: run(task_description)
        TT-->>C: translated_text
    else Translator disabled
        C-->>C: translated := task_description
    end

    C->>PE: run(translated)
    PE-->>C: spec (JSON)

    C->>CG: run(spec)
    CG-->>C: code (str)

    alt Optimizer enabled
        C->>CO: run(code)
        CO-->>C: optimized_result (optimized_code, stats, ...)
        C-->>U: final_code := optimized_result
    else Optimizer disabled
        C-->>U: final_code := code
    end
```

---

## 4) Activity Diagram (Pipeline Control Flow)

```mermaid
stateDiagram-v2
    [*] --> CheckTranslator

    state CheckTranslator {
        [*] --> Decision
        Decision: Translator enabled?
        Decision --> Translate: Yes
        Decision --> Bypass: No

        Translate: Translate input to English
        note right of Translate
            📥 Input: Raw user request (any language)
            📤 Output: English request
        end note

        Bypass: Bypass translation
        note left of Bypass
            📥 Input: Raw user request (English)
            📤 Output: English request (unchanged)
        end note


    }
    Translate --> BuildSpec
    Bypass --> BuildSpec
    BuildSpec: Build structured JSON spec
    note left of BuildSpec
        📥 Input: English request
        📤 Output: JSON specification
    end note

    BuildSpec --> Generate

    Generate: Generate Python function code
    note left of Generate
        📥 Input: JSON specification
        📤 Output: Python code (initial version)
    end note

    Generate --> CheckOptimizer

    state CheckOptimizer {
        [*] --> DecisionO
        DecisionO: Optimizer enabled?
        DecisionO --> Optimize: Yes
        DecisionO --> Finalize: No

        Optimize: Optimize code
        note right of Optimize
            📥 Input: Initial Python code
            📤 Output: Improved Python code
        end note
        Finalize: Bypass optimization

    }

    Optimize --> [*]
    Finalize --> [*]




```

---

## 5) Class Diagram (Key Classes and Relations)

```mermaid
classDiagram
    class Coordinator {
      - debug_mode: bool
      - llm_config: Dict
      - translator: TechnicalTranslator
      - prompt_engineer: PromptEngineer
      - generator: CodeGenerator
      - optimizer: CodeOptimizer
      + run(task_description: str) Dict
    }

    class TechnicalTranslator {
      - llm: OllamaLLM
      - template: ChatPromptTemplate
      + run(input_text: str) str
    }

    class PromptEngineer {
      - llm: OllamaLLM
      - parser: JsonOutputParser
      - template: ChatPromptTemplate
      + run(problem_description: str) Dict
    }

    class CodeGenerator {
      - llm: OllamaLLM
      - template: ChatPromptTemplate
      + run(function_spec: Dict) str
      - _prepare_spec(spec: Dict) Dict
      - _postprocess_code(code: str) str
    }

    class CodeOptimizer {
      - debug_mode: bool
      - target_python_version: str
      + run(code: str) Dict
      + get_config() Dict
      + get_optimization_report(result: Dict) str
      - _is_valid_syntax(code: str) bool
      - _apply_*() helpers
      - _fix_*() helpers
      - _run_mypy_*() helpers
    }

    Coordinator --> "0..1" TechnicalTranslator
    Coordinator --> "1" PromptEngineer
    Coordinator --> "1" CodeGenerator
    Coordinator --> "0..1" CodeOptimizer

```

---

## 6) Deployment Diagram (Local vs Cloud)

```mermaid
graph TD
    %% USER LAYER
    U[User or Researcher - Gradio UI or CLI] -->|Task Request| C

    %% LOCAL ENVIRONMENT
    subgraph LOCAL["Local Environment - HP ZBook G6 Ubuntu 24.04"]

        %% DEPLOYMENT ABSTRACTION LAYER
        subgraph ABSTRACTION["Deployment Abstraction Layer"]
            API[Ollama]
        end
        subgraph LOCAL_APP["Core Services"]
            C[Agent Service]

        end

        subgraph LOCAL_INFRA["Local Ollama Runtime"]
            LOLLAMA[Ollama Runtime]

            subgraph MODELS_LOCAL["Deployed Local Models"]
                M[llama3.2 3b]
            end

            LOLLAMA --> M
        end
    end



    %% CLOUD ENVIRONMENT
    subgraph CLOUD["Privacy Preserving Cloud Environment"]
        subgraph CLOUD_PROXY["Ollama Cloud Proxy"]
            M6[qwen3 coder 480b cloud]
        end
    end

    %% CONNECTIONS & FLOWS
    C -->|Model Call| API
    API -->|Local Mode| LOLLAMA
    API -->|Cloud Mode| M6

    LOLLAMA -->|Inference Response| API
    M6 -->|Cloud Response| API
    API -->|Model Output| C
    C -->|Task Response| U


```

---

## 7) Data Flow Diagram

```mermaid
flowchart TD
    D1[(Task Description)] --> TT{{Translator?}}
    TT -- Yes --> T1[Translated Text]
    TT -- No --> T1a[Original Text]

    T1 --> P[PromptEngineer]
    T1a --> P
    P -->|JSON Spec| S1[(Spec: function_name, signature, constraints, examples...)]

    S1 --> CG[CodeGenerator]
    CG -->|Python code| C1[(Generated Code)]

    C1 --> O{{Optimizer?}}
    O -- Yes --> O1[Apply: black, isort, autoflake, autopep8, pyupgrade, mypy]
    O1 --> R1[(Optimized Code + Report)]
    O -- No --> R2[(Final Code)]

    R1 --> OUT[(Output to User)]
    R2 --> OUT
```

---

## 8) Coordinator State Machine

```mermaid
stateDiagram-v2
    [*] --> Initialized
    Initialized --> LLMConfigured: build shared LLM (optional)
    Initialized --> Translating: skip LLM config

    LLMConfigured --> Translating: translator enabled
    LLMConfigured --> Specifying: translator disabled

    Translating --> Specifying: translation ok
    Translating --> Error: translation failed

    Specifying --> Generating: spec ok
    Specifying --> Error: spec failed

    Generating --> Optimizing: optimizer enabled
    Generating --> Completed: optimizer disabled
    Generating --> Error: generation failed

    Optimizing --> Completed: success / fallback
    Optimizing --> Error: optimizer failed

    Error --> Initialized: retry / recover
    Completed --> [*]
    Error --> [*]

```

---

Notes:

- Translator and Optimizer are optional stages based on configuration.
- Local vs Cloud variants differ primarily by the LLM configuration and availability; class structure remains the same.
- Optimizer returns a rich result payload (optimized_code, stats, tools used, mypy suggestions). The Coordinator currently treats the optimizer output as final; ensure downstream usage considers its structure.
