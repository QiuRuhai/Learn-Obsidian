---
name: review
description: >-
  Use this skill when the user wants to review, test retention, quiz
  themselves, or warm up prerequisites across existing notes in notes/ via
  blind cue retrieval and targeted trap probes. Do NOT use to learn brand-new
  concepts (`learn`), upgrade `[skim]` concepts/papers to `evergreen` or
  `deep` (`learn` / `paper`), or run comparative/conflict syntheses
  (`synthesize`).
---

# Review Skill (Active Retrieval, Discrimination & Targeted Repair)

Reviewing a note does **not** mean summarizing it back to the learner. Pull the learner's `自测线索` and `> [!warning] 易错陷阱：` history, test condition-action discrimination and causal reconstruction on demand, reject vague hand-waving, and update notes only when genuine new signal emerges. Conduct all dialogue and edits in **Simplified Chinese**, keeping standard **English technical terms**.

## Phase 1: Locate Target & Error-Weighted Selection

1. **Read `index.md` first**:
   - Never scan `notes/` blindly.
   - **Single-Note Request**: Locate the named `[[概念]]`, `[[论文]]`, or `[[专题]]` note (routes to **Mode 2**).
   - **Multi-Note Review / Pre-Paper Warm-Up**: Silently select 2–3 high-leverage notes without leaking their titles upfront (routes to **Mode 1**). Weight selection heavily toward `evergreen`/`deep` notes carrying **`> [!warning] 易错陷阱：`** (proven personal blind spots) and **older `updated:` dates** (Bjork New Theory of Disuse); **deprioritize `[skim]` notes** in general Mode 1 draws (include `[skim]` only when named directly in Mode 2 or needed as a pre-paper prerequisite warm-up). Only use `ask_question` for domain selection when the user says bare `"复习"` across `≥2` vault domains (show domain names only, never note titles).
2. **Read Only Target Note(s) (1–3 max)**:
   - Focus on core propositions (`>`), mechanism/boundary sections (especially `> [!tip]`, `> [!warning] 易错陷阱：` / `常见误区：`, `> [!question]`), and `## 自测与关联`.
3. **Frame Lightweight Scope Upfront**:
   - On entering **Mode 1**, announce the cap in 1 short clause at the top (`本次快速盲测 2–3 题，一次一题`) and ask Question 1 inside the isolated prompt box below, then **STOP**.

## Phase 2: Active Diagnostic Check (`Anti-Hand-Waving` + Dual Modes)

Never recap the note before asking. Ask **1 free-text question per turn** (never `ask_question`), isolate the prompt cleanly with `---` + `> **Review｜<纯文字短标题>**` (never `$...$` inside `**...**`), require causal reasoning (*why* + *governing condition*), and **STOP** cleanly after asking (**NEVER** answer in the same turn). **Mode 1 Spoiler Ban**: strictly forbid `file://` links during Mode 1 questions or hints until the learner answers and locks the note.

1. **Mode 1: Blind Condition-Action Discrimination (`盲测情境与干扰辨析`)**:
   - **When**: Reviewing multiple notes, running a general check, or warming up prerequisites before reading a paper.
   - **How**: Present a concrete problem symptom paired with **competing plausible methods (decoys)**—**NEVER** naming the target `[[笔记]]` or telegraphing the winning mechanism in the question stem. Ask **only 1 scenario question** per turn.
   - *Example*: “前向弹性仿真收敛了 200 步、设计参数有 $10^5$ 维而损失是标量：应选择保留 200 步状态做 Unrolled BPTT、前向求状态灵敏度矩阵，还是另一条低内存路线？为什么？”
2. **Mode 2: Targeted Deep Probe (`定点深挖`)**:
   - **When**: Reviewing a single user-named note.
   - **How**: Probe with its `自测线索`, invert a governing premise, or re-test a recorded `> [!warning] 易错陷阱：` / `常见误区：`.
3. **For `status: skim` Notes (`concept` & `paper` Protection Ceiling)**:
   - **NEVER** blind-quiz unencoded algebra or derivations past `> [!question] 待深挖断点`. Test only `已验直觉` + black-box applicability (for `concept`) or trigger conditions + suspect assumptions (for `paper`), or offer seamless upgrade via `learn` (`[skim]` → `evergreen`) / `paper` (`[skim]` → `[deep]`).
4. **Anti-Hand-Waving Rule**:
   - Never pass an answer that only drops a `[[概念]]` name without specifying the governing condition, invariant, or object signature. Confirm the landed piece factually and probe specifically for the missing structural piece (zero yes/no spoiler).

## Phase 3: Bounded Repair (1–2 Turns Max), Transfer & Seamless Handoff

1. **If Recall Fails or Is Shaky (`Fading Hint → Bounded Repair`)**:
   - *Turn 1 — 1-Line Structural Hint*: Give **1 single-sentence hint** pointing to the governing premise or object signature (withholding target title and `file://` links in Mode 1) and wait.
   - *Turn 2 (Hard Cap)*: If still stuck or `"不会"`, explain cleanly in ≤1 short block (now pairing the revealed note with `[basename.md](file:///Users/choutelei/01_Learn/MyVault/notes/basename.md)` in chat). Log this blind spot for Phase 4 (`> [!warning] 易错陷阱：`) **only if** the note is `evergreen`/`deep` (or the mistake sits inside `status: skim`'s already-encoded `已验直觉`)—**NEVER** record an unencoded breakpoint gap in a `[skim]` note as an `易错陷阱`. Never turn `review` into a 10-turn lecture; if full re-derivation or `[skim]` completion is needed, offer handing off to `learn` (for concepts) or `paper` `Mode B` (for papers)—**handoff contract**: pass the localized gap directly into Phase 2, **skipping** Phase 1 probing in both skills.
2. **If Solid (`Composition / Regime-Flip Check`)**:
   - Confirm in 1 plain factual sentence which exact condition landed (zero praise; link the revealed note via `[basename.md](file:///Users/choutelei/01_Learn/MyVault/notes/basename.md)`). For `evergreen`/`deep` notes, ask **1 one-step transfer check** inside `---` + `> **Review｜<纯文字短标题>**` combining two concepts (`Composition`) or testing what parameter/scale shift flips the Mode 1 choice (`Regime-Flip`), then **STOP**; for `[skim]` notes, skip stretching into unencoded derivations, confirm the skeleton holds cleanly, and offer 1-line `learn` / `paper` upgrade if desired.
3. **Pre-Paper Warm-Up Handoff**: When warming up before `paper` `Mode B`, hand the verified diagnostic floor (carrying any exposed prerequisite gap as `[前置补洞]` or routing to `learn` if blocking) straight into `paper` Phase 2 (`skip` duplicate Phase 1 probing), or trigger `paper` `[skim]` → `[deep]` upgrade cleanly.

## Phase 4: Evolve Only on New Signal & Lint

1. **No Busywork Edits**: Leave `notes/` and `index.md` untouched when recall is clean and nothing changed.
2. **Promote/Record New Blind Spots**: If review exposed a new misconception, upgrade or write `> [!warning] 易错陷阱：<盲点短标题>` in objective, third-person technical language (never chat transcripts), add/adjust a blind `自测线索` targeting it (without leaking `title`/`aliases` and grounded in body prose), bump `updated:`, and preserve disjoint YAML + `GEMINI.md` formatting rules.
3. **Deterministic Lint**: Run `python3 -B scripts/lint-vault.py` after any edit and resolve all errors and warnings before finishing.
