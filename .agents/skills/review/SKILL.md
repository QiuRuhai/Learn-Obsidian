---
name: review
description: >-
  Use this skill when the user wants to review, test retention, refresh memory,
  or quiz themselves on existing concepts or papers in notes/ (or warm up
  prerequisites before starting a new paper). Uses Retrieval Cues and recorded
  Misconceptions for active diagnostic questioning rather than passive re-reading.
---

# Review Skill (Active Retrieval & Targeted Repair)

Reviewing a note does **not** mean summarizing it back to the learner. Reading a clean summary creates fluency without testing retrieval. Your job is to pull the learner's `Retrieval Cues` and `Misconceptions`, test whether the underlying reasoning still reconstructs on demand, repair only the broken links, and evolve the note if new insight surfaces. Conduct all questioning, repair, and note updates primarily in **Simplified Chinese**, naturally retaining standard **English technical terms**.

## Phase 1: Locate Target & Read Retrieval Hooks

1. **Read `index.md` first**:
   - Never scan all files in `notes/` blindly.
   - If the user names a specific `[[概念]]` or `[[论文]]`, locate it in `index.md`.
   - If the user asks for a general review or pre-paper warm-up, propose 1–3 high-leverage notes from `index.md` (prioritizing direct prerequisites, older entries, or `[skim]` papers to test what actually stuck) and confirm which to test.
2. **Read Only the Target Note(s) (1–3 max)**:
   - Focus on `Core Proposition` / `Core Claim`, `The Click & Misconceptions`, and `Retrieval Cues`.

## Phase 2: Active Diagnostic Check (One Question at a Time)

1. **No Spoiling / No Warm-Up Recap**:
   - Do not recap the note before asking. Jump straight into testing retrieval.
2. **Construct 1 Applied Probe**:
   - Draw from `Retrieval Cues`, invert an assumption, or design a fresh boundary case specifically aimed at testing whether an earlier trap in `Misconceptions` stays fixed.
   - Ask the learner to explain *why* (`thinking`), not just recite a name or formula.
   - If the target is a `status: skim` paper note, test only the high-level bottleneck/insight you actually covered—or ask if they now want to escalate it into `paper` Mode B for deep derivation.

## Phase 3: Diagnose & Targeted Repair

1. **If Solid**:
   - Acknowledge briefly and either move to one harder transfer/cross-note question (linking two `[[笔记]]`) or mark the node verified and conclude / advance to the next review target.
2. **If Shaky or Forgotten**:
   - Do **not** re-lecture the entire note from scratch.
   - Pinpoint the exact reasoning link that broke and run 1–2 focused `Motivate → Teach → Check` turns (using the note's `Unconditional Truths` and `The Click` only as diagnostic leverage) until the learner re-derives it cleanly.

## Phase 4: Evolve the Note (Only When Warranted)

1. **No Busywork Edits**:
   - If the learner recalled cleanly and nothing changed, leave `notes/` and `index.md` untouched.
2. **Capture New Signal**:
   - If review uncovered a *new* misconception, a sharper analogy for `The Click`, a missing `[[wikilink]]`, or a stronger `Retrieval Cue`, update `updated:` and that specific section in the existing note.
   - Update `index.md` only if the one-line summary itself changed (or if a `skim` note was escalated and upgraded via `paper` Mode B).
