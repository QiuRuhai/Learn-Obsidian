# Learn-Obsidian

An AI-native learning harness built on top of an Obsidian vault—combining **LearnHarness** (gap probing, minimal dependency roadmaps, motivated single-step derivation, and active retrieval) with **Obsidian `[[wikilinks]]`** as a compounding personal knowledge graph.

> Click **Use this template** on GitHub (or clone this repo) to start your own vault.

## Why This Exists

Traditional LLM summaries produce fluent text without verifying whether you actually understand the underlying reasoning. **Learn-Obsidian** flips the workflow:

1. **Progressive Context (`index.md` first)**: The agent reads only the lightweight `index.md` on startup, pulling 1–2 existing `[[notes]]` only when dependencies intersect—keeping context lean.
2. **Understanding = "Obviously True"**: Instead of dumping summaries, the agent probes your boundary, builds a non-spoiler minimal dependency roadmap, and walks through **one reasoning step at a time** (`Predict → Teach → Check`), repairing misconceptions immediately.
3. **Obsidian `[[Wikilinks]]` as the Knowledge Graph**: Verified knowledge is lazily compiled into `notes/` using native `[[wikilinks]]` and `The Click & Misconceptions` + `Retrieval Cues`, rather than cluttering notes with temporary roadmap diagrams.

## Core Skills (`.agents/skills/`)

- **`learn`** ([SKILL.md](.agents/skills/learn/SKILL.md)) — General-purpose learning engine for any standalone concept (CS, math, finance, systems, etc.). Also acts as a nested sub-routine when a paper hits a deep prerequisite gap.
- **`paper`** ([SKILL.md](.agents/skills/paper/SKILL.md)) — Dual-mode workflow for reading documents in `inbox/`:
  - **Mode A · Skim & Ingest**: Fast structural digest (`瓶颈 → 核心洞察 → 方法骨架 → 代价与局限`) for lower-priority papers (`status: skim`).
  - **Mode B · Deep Co-Reading**: Minimal reading roadmap (`[前置补洞]` / `[必然推导]` / `[经验权衡]`) + single-step derivation + nested `learn` with immediate concept compilation (`status: deep`).
  - Finished sources in `inbox/` are archived to `.raw/` and linked via `source: ".raw/<filename>"`.
- **`review`** ([SKILL.md](.agents/skills/review/SKILL.md)) — Active recall and targeted repair driven by `Retrieval Cues` and previously recorded `Misconceptions` (no passive recap).

## Vault Structure

```text
.
├── GEMINI.md                  # Global learning harness rules for the AI agent
├── index.md                   # Lightweight one-line-per-note knowledge index
├── inbox/                     # Unread PDFs / papers waiting to be processed
├── .raw/                      # Hidden archive for processed source PDFs (gitignored)
├── notes/                     # Compiled evergreen concept & paper notes
├── _templates/
│   ├── concept-note.md        # Template for standalone concept notes
│   └── paper-note.md          # Template for paper notes (skim | deep)
└── .agents/skills/
    ├── learn/SKILL.md
    ├── paper/SKILL.md
    └── review/SKILL.md
```

## Quick Start

1. Create a **private** repository from this template (recommended so your personal notes and PDFs stay private), and clone it locally.
2. Open the folder as an **Obsidian Vault** and open it with an agentic coding assistant that reads `GEMINI.md` and `.agents/skills/`.
3. Try one of three prompts:
   - **Learn a concept**: *"我想学习 [某个概念]，请用 learn 流程带我推一遍。"*
   - **Read a paper**: Drop a PDF into `inbox/`, then say *"带我读一下 inbox/ 里的 [论文名]。"*
   - **Review**: *"用 review 帮我抽查一下 `[[某个笔记]]`。"*

## License

[MIT](LICENSE)
