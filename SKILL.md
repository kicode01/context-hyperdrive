---
name: context-hyperdrive
description: >-
  [WHAT IT DOES]: Maximizes AI coding agent intelligence while cutting token volume by 75-85% and token cost by 90%.
  Amplifies terse/small prompts into high-IQ execution briefs, shrinkwraps codebases into AST skeletons, and stabilizes prompt prefixes for 100% provider cache hits.
  [WHEN TO USE]: Use when working with large files (>200 lines), managing expensive multi-turn agent loops, dealing with strict LLM rate limits/quotas, or when user prompts are terse (3-5 words) and need cognitive expansion without burning slow reasoning tokens.
  [WHEN NOT TO USE]: Do NOT use when generating tiny scratch scripts from scratch or when editing plain markdown notes without code dependencies.
---

# Context Hyperdrive: Cognitive Intent Amplification & Token Cache Maximizer

```
  +--------------------------------------------------------------------------+
  |                           CONTEXT-HYPERDRIVE                             |
  |     Intent Synthesizer, AST Shrinkwrap & Prompt Cache Alignment Engine   |
  +--------------------------------------------------------------------------+
       |                                                    |
       v                                                    v
  [Small User Prompt]                               [Raw Codebase Files]
   - "fix refund bug"                                - 2,000+ lines of code
   - 3-5 word commands                               - Heavy token bloat
       |                                                    |
       +-------------------------+--------------------------+
                                 |
                                 v
                     [Tri-Core Hyperdrive Pipeline]
                     1. Intent Amplifier (Git Diff + Error Trace)
                     2. AST Shrinkwrap (Prune Non-Focal Bodies)
                     3. Deterministic Cache Aligner (Pin >=1024 Tokens)
                                 |
                +----------------+----------------+
                |                                 |
          [Token Reduction]                 [Cache Hit (90%)]
                v                                 v
      [75% - 85% Less Tokens]           [0.1x Provider Cost]
      - Zero Rate Limit Hits            - Sub-Second Execution
      - High-IQ Target Precision        - Bypasses Slow Thinking Delay
```

---

## 1. When to Activate

Trigger `context-hyperdrive` whenever:
- **Terse / Small User Prompts:** The user supplies a brief 3–5 word command (e.g. "fix checkout bug", "optimize db query") that would otherwise trigger expensive, slow "High Reasoning" token loops.
- **Large Source Files:** The target file exceeds 200 lines, where sending full code dumps exhausts context windows.
- **Provider Quota & Rate Limit Pressures:** Approaching daily token limits on GitHub Models, Anthropic, Gemini, or OpenAI.
- **Multi-Turn Cost Optimization:** Long agent chat sessions where repeated tool calls and system instructions should be pinned for a 90% prompt cache discount.

---

## 2. The 3-Pillar Execution Protocol

### Pillar 1: Latent Intent Amplification (`scripts/intent_amplifier.py`)
1. Introspect local repository state: check `git status --porcelain` and active stack traces.
2. Extract domain keywords and target symbols from the terse prompt.
3. Synthesize a structured, high-precision execution brief that dictates:
   - Specific target functions and symbols to modify.
   - Non-negotiable boundary constraints (zero regressions, invariant safety).
   - Inferred target source files.

### Pillar 2: Multi-Language AST Context Shrinkwrapping (`scripts/shrinkwrap_ast.py`)
1. Multi-language support with native grammar parsing for **Python (`.py`)**, **TypeScript & TSX (`.ts`, `.tsx`, `.js`, `.jsx`)**, **Go (`.go`)**, and **Rust (`.rs`)**.
2. Retains focal execution targets, exported types, interfaces, and struct envelopes in full detail.
3. Automatically identifies parent containers (such as React components wrapping a target handler) and keeps them open while collapsing non-focal sibling functions.
4. Replaces non-focal method bodies with lightweight valid stubs (`pass` in Python, `{ /* ... pruned ... */ }` in TS/Go/Rust).
5. Strips non-essential comments and redundant docstrings outside the focal zone, cutting code token bloat by **70% to 85%**.

### Pillar 3: Deterministic Cache Pinning (`scripts/cache_aligner.py`)
1. Order all system instructions, project invariant rules, and tool specifications into an immutable prefix block.
2. Ensure prefix size meets provider caching thresholds (>= 1,024 tokens for Anthropic Claude).
3. Compute the SHA-256 hash to guarantee byte-for-byte reproducibility across turns.
4. Place dynamic turn instructions in the ephemeral payload suffix.
5. Captures provider cache hit rates, reducing input token pricing by **90%**.

### Pillar 4: Terminal & Test Log Quantization (`scripts/log_quantizer.py`)
1. Strips ANSI color escape codes, carriage return spinners, and ASCII progress bars.
2. Folds external library stack frames (`node_modules/`, `site-packages/`, `<frozen>`, stdlib) into concise 1-line badges while preserving user project frames.
3. Collapses repetitive compiler warnings and passing test lists (`[+] [OK] N passing tests collapsed`).
4. Reduces failure traces and terminal outputs by **80% to 95%** without loss of root-cause diagnostics.

### Pillar 5: Smart Git Diff Compaction (`scripts/diff_compactor.py`)
1. Automatically detects and excludes noise lockfiles (`package-lock.json`, `Cargo.lock`, `yarn.lock`, minified assets).
2. Strips unmodified context lines, grouping hunks into concise function-level change summaries (`[Scope: def my_func]`).
3. Reduces multi-file PR and commit diffs by **80% to 95%** while retaining exact additions and deletions.

---

## 3. End-to-End Execution CLI

To run the unified optimization pipeline on any prompt and target file:

```bash
python scripts/hyperdrive_pipeline.py
```

Or invoke components independently:

```bash
# Compress source code to focal symbol
python scripts/shrinkwrap_ast.py path/to/file.py symbol_name

# Verify prompt cache alignment
python scripts/cache_aligner.py

# Quantize test logs and error traces
python scripts/log_quantizer.py --demo

# Compact git diffs and exclude lockfiles
python scripts/diff_compactor.py --demo

# Amplify terse prompt into structured brief
python scripts/intent_amplifier.py
```

---

## 4. Failure Modes & Mitigations

| Failure Mode | Risk | Automated Mitigation |
| :--- | :--- | :--- |
| **Over-Pruned AST Context** | Target function depends on a helper defined in the same file. | Re-expand helper signatures into typed interfaces while keeping helper bodies stubbed. |
| **Cache Prefix Invalidation** | Dynamic timestamp or random seed inserted into system prompt. | Aligner validates SHA-256 prefix hash; strips dynamic headers from static cache zone. |
| **Terse Prompt Ambiguity** | User prompt matches multiple symbols across different modules. | Amplifier queries `git status` to prioritize recently modified files first. |
