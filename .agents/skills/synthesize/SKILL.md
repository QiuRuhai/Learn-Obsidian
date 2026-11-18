---
name: synthesize
description: >-
  Use this skill when the user wants to answer a cross-note comparative or
  diagnostic query grounded strictly in existing notes (`wiki-query`), or to
  synthesize, map lineage, and fold contradictions across 3–8 existing notes in
  notes/ into a `type: synthesis` note (`wiki-fold`). Do NOT use when target
  concepts are absent from notes/ (`learn`), for reading a single paper
  (`paper`), or for blind recall quizzes (`review`).
---

# Synthesize Skill (Vault Query × Cross-Source Compilation)

Synthesizing across notes is **not** concatenating summaries into a long table or answering from unverified memory. Route cleanly between **read-only evidence-grounded querying (`wiki-query`)** and **diagnostic cross-source synthesis (`wiki-fold` compilation)**—surfacing the shared root bottleneck, exact bifurcation points, trade-offs, and contradictions across vault notes. Conduct all dialogue and note writing in **Simplified Chinese**, keeping standard **English technical terms**.

## Entry Routing: `wiki-query` vs. `wiki-fold` Synthesis

- **Mode A｜跨笔记证据问答 (`wiki-query`)**: Use when the learner asks a comparative, diagnostic, or "what does my vault hold about X vs. Y?" question without requesting a new synthesis note. Keep `notes/` and `index.md` read-only unless the learner accepts an optional 1–2 note file-back.
- **Mode B｜跨源综合编译 (`wiki-fold` Synthesis Compilation)**: Use when the learner wants to systematically compare, map lineage, or resolve contradictions across 3–8 existing notes into a durable `type: synthesis` note (folding corrections back into source notes).

---

## Mode A: Evidence-Grounded Vault Query (`wiki-query` 跨笔记检索问答)

1. **Read `index.md` First (Progressive Context)**:
   - Never scan `notes/` blindly. Select the 2–8 relevant `[[笔记]]` matching the query (check `inbox/` filenames and `## 待沉淀支线 (Backlog)` to flag unread/uncompiled gaps).
2. **Read Targeted Notes & Verify Provenance**:
   - Inspect each selected note's core proposition (`>`), mechanism/boundary sections (especially `> [!tip]`, `> [!warning] 易错陷阱：` / `常见误区：`, `> [!question]`), and `## 自测与关联`.
3. **Answer Strictly From Vault Evidence + Actionable Handoff**:
   - Cite exact provenance via `[[笔记名称]]` paired with clickable `[笔记名称.md](file:///Users/choutelei/01_Learn/MyVault/notes/笔记名称.md)` anchors in live chat (and page/equation anchors when recorded; keep any file-back written into `notes/` pure `[[wikilinks]]`). Separate explicitly:
     - **`[Vault 已覆盖证据]`**: claims strictly grounded in existing `notes/` (plus clearly labeled elementary deductions from them);
     - **`[Vault 未覆盖 / 待验证缺口]`**: edge regimes, `Backlog` items, or unread `inbox/` sources not yet verified in `notes/`.
   - **Close With 1-Line Handoff or Escalation (Optional)**:
     - If a sharp 1–2 note boundary emerged, offer 1 line to file it back (`updated:` + `python3 -B scripts/lint-vault.py`);
     - If `[Vault 未覆盖]` maps to an `inbox/` PDF or `Backlog` entry, give a 1-line handoff prompt into `paper` or `learn`;
     - If the insight spans ≥3 existing notes and needs a durable matrix, offer escalating to **Mode B**. Otherwise leave all files untouched.

---

## Mode B: Cross-Source Synthesis Compilation (`wiki-fold`)

### Phase 1: Scope & Guiding Question (`index.md` first)

1. **Read `index.md` first (+ `inbox/` & `Backlog` Scan)**: Identify 3–8 problem/axis-related `[[概念]]` or `[[论文]]` notes, checking `inbox/` filenames and `## 待沉淀支线 (Backlog)` so unread rival/source papers are surfaced upfront (keep `type: synthesis` strictly problem/mechanism-driven rather than flat catalogs; if core targets aren't in `notes/` yet, hand off to `learn` / `paper` first).
2. **Pin Down Scope & Guiding Question (STOP)**: Propose candidate source notes (noting any unread `inbox/` counterparts) and 1–2 comparison axes using `ask_question` (`is_multi_select: true`) to confirm the 3–8 notes and comparison axis cleanly before reading them.

### Phase 2: Targeted Read & Conflict Scan

1. **Read Only Confirmed Source Notes (3–8 max) with `[skim]` Ceiling**: Inspect core propositions, mechanism/boundary sections, callouts, and `## 自测与关联`. For any `status: skim` source note, bound claims strictly to its verified `已验直觉` / skeleton—**NEVER** treat unverified `> [!question] 待深挖断点` / `待深挖疑问` algebra as settled fact.
2. **Spot Roots, Bifurcations & Contradictions**: Identify shared unconditional premises, exact bifurcation constraints, assumption conflicts, narrowed boundaries, or superseded claims.

### Phase 3: Diagnostic Synthesis (Check Before Compiling)

Do **not** dump the full comparison table upfront:
1. Briefly state the shared root bottleneck in 2–4 plain sentences (link confirmed notes via clickable `file://` anchors in chat).
2. Ask **1 focused free-text diagnostic question** (never `ask_question`, never quizzing unencoded `[skim]` breakpoints) isolated inside `---` + `> **Check｜<纯文字短标题>**` testing why Route A traded property X while Route B kept X at cost Y, then **STOP**. Track any exposed learner conflation silently for `> [!warning] 易错陷阱：`. Give max 1 Level-1 hint if conflated before clarifying cleanly.

### Phase 4: Compile, Fold Contradictions (`wiki-fold`) & Lint (`notes/` + `index.md`)

Only when distinctions hold (or learner says `"存笔记"`):
1. **Write or Update `notes/<专题综合名称>.md`**:
   - Follow `_templates/synthesis-note.md` (`status: evergreen`, `evergreen | superseded`, 2–3 lowercase `kebab-case` `tags`, optional `prerequisites: []`).
   - Keep YAML `prerequisites`, `sources` (3–8 source notes), and `related` (lateral syntheses only—never repeating `sources`) strictly disjoint with quoted `"[[...]]"`.
   - Maintain `GEMINI.md` formatting rules, smooth prose + contrast table, `> [!tip] 全局结构感`, optional `> [!warning] 易错陷阱：` / `常见误区：` if a boundary conflation occurred, and 2 zero-spoiler `自测线索` under `## 自测与关联` (never leaking note titles, grounded in table/prose, no bottom YAML link dump).
2. **Standardized Contradiction Folding (`wiki-fold` 反哺源笔记)**:
   - Whenever synthesis reveals a narrowed scope, counterexample, or superseded claim in a source note, fold `> [!warning] 跨文献冲突：<简要结论与 [[专题综合名称]] 关联>` into that source note's boundary section (setting `status: superseded` only when its core claim/method is fully superseded), add `"[[专题综合名称]]"` to its `related` list, and bump `updated:`. Even without conflict, wire `"[[专题综合名称]]"` into each `sources` note's `related` list for symmetric provenance.
3. **Update `index.md` & Lint**:
   - Add/update `- [[<专题综合名称>]] — ~20–30 字选型或演化命题 (YYYY-MM-DD)` under `## 专题与综合 (Syntheses)`, and sync `[superseded]` tag or 1-line summary on any affected source note.
   - (Opt-In Only): Generate a `.canvas` file (JSON Canvas 1.0, `notes/<Name>.md`) *only* if explicitly asked for a visual board.
   - Run `python3 -B scripts/lint-vault.py` and fix all errors/warnings before finishing.
