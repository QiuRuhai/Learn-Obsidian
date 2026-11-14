---
name: review
description: >-
  Use this skill when the user wants to review, test retention, refresh memory,
  or quiz themselves on existing concepts or papers in notes/ (or warm up
  prerequisites before starting a new paper). Uses Blind Cue-Driven Cold
  Retrieval, Targeted Deep Probes, Retrieval Cues, and recorded Misconceptions
  for active diagnostic questioning rather than passive re-reading.
---

# Review Skill (Active Retrieval, Blind Cue Recognition & Targeted Repair)

Reviewing a note does **not** mean summarizing it back to the learner. Reading a clean summary creates fluency without testing retrieval. Your job is to pull the learner's `自测线索` (Retrieval Cues) and `容易踩的坑` (Misconceptions), test whether the underlying reasoning still reconstructs on demand, give fading hints before full repair, and evolve notes only when new signal emerges. Conduct all questioning, repair, and note updates primarily in **Simplified Chinese**, naturally retaining standard **English technical terms**.

## Phase 1: Locate Target & Read Retrieval Hooks

1. **Read `index.md` first**:
   - Never scan all files in `notes/` blindly.
   - **Single-Note Request**: If the user names a specific `[[概念]]`, `[[论文]]`, or `[[专题综合]]`, locate it in `index.md` (routes to **Mode 2**).
   - **Multi-Note Review / Pre-Paper Warm-Up**: If the user asks for a general review, domain quiz, or pre-paper warm-up, silently select 2–3 high-leverage notes from `index.md` (prioritizing direct prerequisites, older entries, or `skim` papers) without spoiling their titles upfront (routes to **Mode 1**). If the vault scope is ambiguous, confirm only the *domain/topic scope* rather than leaking the target note names.
2. **Read Only the Target Note(s) (1–3 max)**:
   - Focus on the core proposition (`>` blockquote), `## 顿悟与误区` / `## 批注与疑问` / `## 顿悟与自测`, and `## 自测与关联`.

## Phase 2: Active Diagnostic Check (Dual Retrieval Modes)

Jump straight into retrieval—**never** recap or summarize the note before asking. Always ask one question at a time and require the learner to explain *why* (`thinking`), not just drop a term or formula.

1. **Mode 1: Blind Cue-Driven Cold Retrieval (盲测情境触发)** *(inspired by LearnHarness `Practice`)*:
   - **When**: Reviewing multiple notes, running a general check, or warming up prerequisites before a paper.
   - **How**: Present a concrete problem scenario, engineering bottleneck, or failure symptom **without naming which `[[概念]]` or `[[论文]]` is being tested** (and without quoting its title or signature equation). Require the learner to first **identify which concept/tool applies and why** its assumptions match the situation, then sketch the key reasoning step.
   - *Example contrast*: Instead of “回顾 [[伴随法]]”, ask “前向仿真收敛花了 200 步、设计参数有 $10^5$ 维而目标是标量损失，为什么直接求隐式灵敏度会炸掉？该切换成什么思路把代价压成 1 次线性求解？”
2. **Mode 2: Targeted Deep Probe (定点深挖)**:
   - **When**: Reviewing a single user-named note.
   - **How**: Probe directly using its `自测线索`, test whether a recorded trap in `容易踩的坑` stays fixed under a boundary variation, or invert a core assumption (e.g., “前向残差未归零时哪条等式最先失效？”).
3. **For `status: skim` Paper Notes**:
   - Test only the high-level bottleneck and insight actually recorded in the note—or ask if the learner wants to escalate it into `paper` **Mode B** for full derivation.

## Phase 3: Diagnose, Fading Hints & Cross-Note Interleaving

1. **If Recall Fails or Is Shaky (`Fading Hint → Targeted Repair`)**:
   - Do **not** immediately dump the answer or re-lecture the entire note.
   - **Step 1 — 1-Line Structural Hint**: Give **one 1-line structural or constraint hint** pointing back to the underlying `Unconditional Truth` or symptom cue (in Mode 1, narrow down the cue without naming the target note yet if possible) and give the learner a second chance to reconstruct it.
   - **Step 2 — Pinpoint Repair**: Only if they remain stuck after the hint, identify the exact broken reasoning link and run 1–2 focused `Predict → Teach → Check` turns until they re-derive it cleanly.
2. **If Solid (`Cross-Note Interleaving`)**:
   - Acknowledge briefly (dry register, no empty praise).
   - Offer **one 1-step cross-note transfer check** linking two `[[笔记]]` (e.g., how `[[概念A]]` accelerates or constrains `[[概念B]]`, or what flips the choice between two approaches), or advance to the next target / conclude if the warm-up goal is met.

## Phase 4: Evolve the Note & Lint (`notes/` + `index.md`)

1. **No Busywork Edits**:
   - If the learner recalled cleanly and nothing changed, leave `notes/` and `index.md` untouched.
2. **Capture New Signal**:
   - If review uncovered a *new* misconception (`容易踩的坑`), a sharper analogy for `想通的关键`, a missing `[[wikilink]]`, a boundary caveat, or a stronger `自测线索`, update `updated:` and that specific section in the existing note (strictly preserving `GEMINI.md` MathJax × `[[wikilink]]` rules: `[[...]]` never inside `$...$`/`$$...$$`, no `$...$` inside `**...**`, quoted YAML wikilinks).
   - Update `index.md` only if the one-line summary itself changed (or if a `skim` note was escalated and upgraded via `paper` **Mode B**).
3. **Vault Lint Verification**:
   - Whenever any note in `notes/` or `index.md` is updated, run `python3 scripts/lint-vault.py` to confirm zero broken links, YAML issues, or MathJax formatting errors before concluding.
