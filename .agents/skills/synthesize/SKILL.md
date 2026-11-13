---
name: synthesize
description: >-
  Use this skill when the user wants to synthesize, compare, map out, or
  integrate multiple existing notes in notes/ (papers and/or concepts) into a
  cross-source synthesis, lineage, or decision note. Combines LearnHarness
  bifurcation probing with claude-obsidian style cross-source compilation.
---

# Synthesize Skill (Cross-Source Compilation × Global Clarity)

Synthesizing multiple notes is **not** concatenating summaries into a long table. Your job is to help the learner see the **shared root bottleneck, exact bifurcation points, trade-offs, and contradictions** across 3–8 existing notes, verify that global mental model, compile a `type: synthesis` note, and feed any discovered corrections back into the source notes. Conduct all dialogue and note writing primarily in **Simplified Chinese**, naturally retaining standard **English technical terms**.

## Phase 1: Scope & Guiding Question (`index.md` first)

1. **Read `index.md` first**:
   - Never scan all files in `notes/` blindly.
   - Identify 3–8 relevant `[[概念]]` or `[[论文]]` notes matching the user's topic or domain.
2. **Pin Down Scope & Guiding Question (STOP)**:
   - Propose the candidate list of source notes and 1–2 concrete guiding comparison questions (e.g., *"Compare these 4 approaches along memory cost, contact smoothness, and gradient unbiasedness"*).
   - **End your turn** and wait for the learner to confirm which notes and comparison axes to include before reading them.

## Phase 2: Targeted Read & Conflict Scan

1. **Read Only the Confirmed Source Notes (3–8 max)**:
   - Focus on the core proposition (`>`), `## 机制与推导` / `## 问题与方法`, and `## 自测与关联`.
2. **Spot Roots, Bifurcations & Contradictions**:
   - Identify: (a) the common bottleneck they all start from, (b) the exact constraint or trade-off where each route splits, and (c) any implicit contradictions or outdated assumptions between older and newer notes.

## Phase 3: Diagnostic Synthesis (Check Before Compiling)

Do **not** dump the full comparison table all at once:
1. **Surface the Common Root**:
   - Briefly state the shared starting problem in 2–4 lines.
2. **Test the Key Bifurcations (1–2 Turns)**:
   - Ask 1–2 focused diagnostic questions asking the learner to predict or distinguish why Route A had to give up property X while Route B kept X at the cost of Y (or where two notes seem to conflict).
   - Repair any conflation where two distinct mechanisms were blurred together.

## Phase 4: Compile Synthesis Note & Feed Back (`notes/` + `index.md`)

Only when the global distinctions feel clear to the learner (or when asked to save):
1. **Write or Update `notes/<专题综合名称>.md`**:
   - Follow `_templates/synthesis-note.md`.
   - Maintain strict Obsidian formatting rules (`[[wikilinks]]` never inside `$...$`/`$$...$$`, quoted YAML wikilinks in `sources: [...]`, clean readable prose and tables).
2. **Cross-Source Feed-Back (Contradiction & Boundary Repair)**:
   - If synthesis exposed a contradiction, missing scope boundary, or sharper link in any existing source note, ask or apply that targeted update to the affected source note (`updated:` bumped) rather than leaving stale claims behind.
3. **Update `index.md`**:
   - Append or update the synthesis entry under `## 专题与综合 (Syntheses)`.
