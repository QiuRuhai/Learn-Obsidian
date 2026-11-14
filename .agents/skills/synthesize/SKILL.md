---
name: synthesize
description: >-
  Use this skill when the user wants to answer a cross-note comparative or
  diagnostic question grounded strictly in the vault (`wiki-query`), or to
  synthesize, map out, and resolve conflicts across multiple existing notes in
  notes/ into a `type: synthesis` note with `wiki-fold` contradiction folding
  and post-compilation linting via scripts/lint-vault.py.
---

# Synthesize Skill (Vault Query × Cross-Source Compilation)

Synthesizing across notes is **not** concatenating summaries into a long table or answering from unverified memory. Depending on the learner's intent, route cleanly between **read-only evidence-grounded querying (`wiki-query`)** and **diagnostic cross-source synthesis (`wiki-fold` compilation)**—helping the learner surface the shared root bottleneck, exact bifurcation points, trade-offs, and contradictions across vault notes. Conduct all dialogue and note writing primarily in **Simplified Chinese**, naturally retaining standard **English technical terms**.

## Entry Routing: `wiki-query` vs. `wiki-fold` Synthesis

- **Mode A｜跨笔记证据问答 (`wiki-query`)**: Use when the learner asks a comparative, diagnostic, or "what does my vault currently hold about X vs. Y?" question without asking to compile a permanent synthesis note. Keep `notes/` and `index.md` read-only.
- **Mode B｜跨源综合编译 (`wiki-fold` Synthesis Compilation)**: Use when the learner wants to systematically compare, map lineage, resolve contradictions across 3–8 existing notes, and compile a durable `type: synthesis` note (plus fold corrections back into affected source notes).

---

## Mode A: Evidence-Grounded Vault Query (`wiki-query` 跨笔记检索问答)

1. **Read `index.md` First (Progressive Context)**:
   - Never scan all files in `notes/` blindly.
   - Select only the 2–8 relevant `[[概念]]`, `[[论文]]`, or `[[专题]]` notes matching the query, plus inspect `inbox/` filenames only if checking what unread sources could close a gap.
2. **Read Targeted Notes & Verify Provenance**:
   - Inspect each selected note's core proposition (`>`), `## 机制与推导` / `## 问题与方法`, failure boundaries, and `## 顿悟与误区`.
3. **Answer Strictly From Vault Evidence**:
   - **Provenance on Every Claim**: Cite exact source notes via `[[笔记名称]]` (and original page/equation anchors when recorded, e.g., `[[DiffPD]] p.4, Eq.(12)`).
   - **Separate Coverage From Gaps**: Explicitly divide the response into:
     - **`[Vault 已覆盖证据]`**: claims directly supported by existing `notes/` entries (or elementary algebraic deductions explicitly marked as inferred from them);
     - **`[Vault 未覆盖 / 待验证缺口]`**: questions, edge regimes, or papers not yet verified in `notes/` (naming any relevant unread PDFs in `inbox/` rather than padding with ungrounded claims).
   - **Optional Escalation**: If the query exposes a deep cross-note contradiction or high-value comparison axis across 3+ notes, ask whether to escalate into **Mode B** to compile a `type: synthesis` note; otherwise leave files untouched.

---

## Mode B: Cross-Source Synthesis Compilation (`wiki-fold`)

### Phase 1: Scope & Guiding Question (`index.md` first)

1. **Read `index.md` first**:
   - Never scan all files in `notes/` blindly.
   - Identify 3–8 relevant `[[概念]]` or `[[论文]]` notes matching the user's topic or domain.
2. **Pin Down Scope & Guiding Question (STOP)**:
   - Propose the candidate list of source notes and 1–2 concrete guiding comparison questions (e.g., *"Compare these 4 approaches along memory cost, contact smoothness, and gradient unbiasedness"*).
   - **End your turn** and wait for the learner to confirm which notes and comparison axes to include before reading them.

### Phase 2: Targeted Read & Conflict Scan

1. **Read Only the Confirmed Source Notes (3–8 max)**:
   - Focus on the core proposition (`>`), `## 机制与推导` / `## 问题与方法`, failure boundaries, and `## 自测与关联`.
2. **Spot Roots, Bifurcations & Contradictions**:
   - Identify: (a) the common bottleneck and unconditional premises they share, (b) the exact constraint, dataflow choice, or trade-off where each route splits, and (c) any implicit contradictions, missing failure boundaries, or outdated assumptions between older and newer notes.

### Phase 3: Diagnostic Synthesis (Check Before Compiling)

Do **not** dump the full comparison table all at once:
1. **Surface the Common Root**:
   - Briefly state the shared starting problem in 2–4 lines.
2. **Test the Key Bifurcations (1–2 Turns)**:
   - Ask 1–2 focused diagnostic questions asking the learner to predict or distinguish why Route A had to give up property X while Route B kept X at the cost of Y (or where two notes seem to conflict).
   - If the learner conflates two routes, give a 1-sentence structural hint pointing to the separating constraint before revealing the split, and repair any blurred distinction on the spot.

### Phase 4: Compile, Fold Contradictions (`wiki-fold`) & Lint (`notes/` + `index.md`)

Only when the global distinctions feel clear to the learner (or when asked to save):
1. **Write or Update `notes/<专题综合名称>.md`**:
   - Follow `_templates/synthesis-note.md`.
   - Maintain strict Obsidian MathJax × `[[双链]]` formatting rules (`[[wikilinks]]` never inside `$...$`/`$$...$$`, `$...$` never inside `**...**`, quoted YAML wikilinks in `sources: [...]` and `related: [...]`, prose reasoning chains written with `⟹` rather than `$\implies$`, clean readable prose and comparison tables).
2. **Contradiction Folding (`wiki-fold` 反哺源笔记)**:
   - Whenever synthesis uncovers an assumption conflict, narrowed scope boundary, counterexample, or asymmetric relation in existing source notes, fold a crisp boundary/conflict update back into the affected source note(s) (`## 机制与推导` / `## 顿悟与误区` / `## 自测与关联`, adding `"[[专题综合名称]]"` to `related` and bumping `updated:`). Preserve each source note's valid provenance and structure—never leave stale contradictory claims silently unlinked.
3. **Update `index.md`**:
   - Append or update the synthesis entry under `## 专题与综合 (Syntheses)` (and update a modified source note's one-line summary only if its core proposition shifted).
4. **Optional Spatial Visual Board (`.canvas`, Opt-In Only)**:
   - **Only** when the learner explicitly asks for a visual spatial board (e.g., requesting an Obsidian Canvas / 白板), generate valid Obsidian JSON Canvas (`notes/<专题>.canvas` or root `<专题>.canvas`) linking the relevant `notes/*.md` files into a clean root → bifurcation → trade-off layout. Never create `.canvas` files unsolicited.
5. **Run Deterministic Vault Lint**:
   - Execute `python3 scripts/lint-vault.py` after writing the synthesis note, folding updates back into source notes, and updating `index.md`. Fix any reported errors before closing.
