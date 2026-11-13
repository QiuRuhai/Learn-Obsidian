---
name: paper
description: >-
  Use this skill when the user wants to read, understand, or digest a paper,
  article, PDF, or document (especially from inbox/). Supports both fast
  Skim & Ingest (for lower-priority papers) and Deep Co-Reading (LearnHarness
  probe -> reading roadmap -> single-step derivation with nested `learn` for
  deep prerequisite gaps), then compiles linked notes into notes/ and index.md.
---

# Paper Co-Reading Skill (Dual-Mode LearnHarness × Obsidian Wiki)

Reading a paper is not summarizing sections from Abstract to Conclusion. Depending on the paper's priority to the learner, route cleanly between **fast structural ingestion** and **motivated deep co-reading** (pausing to invoke the `learn` flow whenever a deep prerequisite gap blocks derivation). Conduct all explanations, checks, and note writing primarily in **Simplified Chinese**, naturally retaining standard **English technical terms**.

## Phase 1: Triage & Mode Routing

1. **Read Context (Progressive & Lineage-Aware)**:
   - Read `index.md` to see which concepts and papers the learner already holds.
   - If `index.md` already contains a direct predecessor/lineage paper (e.g., reading `DiffXPBD` when `[[XPBD]]` exists) or directly intersecting prerequisite concepts, read those 1–2 notes to anchor known ground.
   - Inspect the target document in `inbox/` (or the path provided by the user; if upgrading an existing `skim` note, check its `source` field, which may already point to `.raw/`). For large or math-heavy PDFs, locate the relevant sections/pages first and read in targeted page segments.
   - **Strict Formula Grounding**: Never reconstruct or guess equations, subscripts, signs, or matrix transposes from memory. If text extraction looks garbled or incomplete on a derivation page, verify directly against the source page (e.g., visual page inspection) before teaching.
2. **Surface the Spine (Brief Orientation)**:
   - In 4–6 lines, state:
     1. What concrete bottleneck in prior work (or in an existing `[[前作论文]]`) this paper attacks;
     2. Its single load-bearing insight;
     3. The 2–4 key prerequisite concepts or mechanisms the paper relies on (linking any already in `index.md` as `[[概念]]`).
3. **Route by Priority (Ask or Follow Explicit Intent)**:
   - Ask the learner whether they want:
     - **Mode A｜速览入库 (Skim & Ingest)** — for lower-priority papers where a quick structural overview and linked Obsidian note are enough; or
     - **Mode B｜精读啃透 (Deep Co-Reading)** — for core papers they want to derive, verify, and truly own.
   - If choosing **Mode B** (or if already specified), probe their edge in the same turn:
     - Their reading goal (e.g., grasp core mechanism, reproduce math/derivations, or critique trade-offs);
     - Which of the listed prerequisites (or predecessor paper deltas) they already hold vs. need to learn; run 1 high-level check question if a load-bearing prerequisite is subtle.

---

## Mode A: Skim & Ingest (Fast Path)

Use **only** for lower-priority papers where step-by-step teaching is unnecessary:
1. **Tight Source-Grounded Digest**:
   - Present a concise structural summary: `瓶颈 → 核心洞察 → 方法骨架 → 代价与局限 → 潜在前置概念` (linking existing `[[概念]]` / `[[论文]]` from `index.md`, and flagging any unfamiliar concepts as unverified rather than faking comprehension).
2. **Compile Paper Note & Archive Source**:
   - Follow `_templates/paper-note.md` to write `notes/<论文简称或标题>.md` with `status: skim` (fill `authors`, `year`, and key page/equation provenance anchors inside `## 问题与方法`; in `## 批注与疑问`, write `待深挖疑问 (Open Questions)` instead of fabricating unverified insights; wire `prerequisites`/`concepts`/`related` and `## 自测与关联` without creating dead links to unverified concepts).
   - If the source file came from `inbox/`, move it into `.raw/` (creating `.raw/` if needed) and set `source: ".raw/<filename>"` in the paper note so `inbox/` stays a clean unread queue.
   - Update `index.md` under `## 论文与文献 (Papers)` with `[skim]`.
3. **Instant Escalation**:
   - If any specific mechanism in the digest catches the learner's interest, immediately switch to **Mode B** focused on that mechanism.

---

## Mode B: Deep Co-Reading (LearnHarness + Nested `learn`)

### Phase 2: Minimal Reading Roadmap (Plan & STOP)

Once the learner's goal and prerequisite gaps are bracketed:
1. **Construct the Minimal Tree (Delta-First When Lineage Exists)**:
   - Prune background already held (from `index.md`, probe, or a direct predecessor `[[论文]]` note) and tangential sections/experiments not needed for the core mechanism.
   - When a predecessor paper is already held, anchor the roadmap at the **Delta**—the exact regime where the predecessor breaks under the new goal.
   - Order the remaining path as `[前置补洞]` → `[必然推导]` / `[经验权衡 (Trade-off)]`, verifying strict topological order (each step depends only on confirmed anchors or earlier steps, never forward-referencing later steps).
2. **Present the Roadmap and STOP**:
   - **Pruned Anchors & Skipped Sections**: Explicitly state which existing `[[概念]]` anchors and paper sections are skipped so the learner can correct any wrong assumption.
   - **Non-Spoiler Landmarks (3–6 steps)**: Show the reading roadmap using status markers (`[✓]` / `[→]` / `[ ]`) and node tags (`[前置补洞]` / `[必然推导]` / `[经验权衡]`). Frame each landmark as a *bottleneck or question to resolve*, **never spoiling the author's trick or final formula** (keep `Predict` alive).
   - **Temporary Visualization**: Use a numbered list for linear paths; when **multiple prerequisite branches converge** onto the paper's core design, attach a compact in-chat Mermaid diagram (`flowchart TD` / `LR`, 4–6 nodes) as a temporary scaffold (never saved into `notes/`).
   - **Completion Criterion**: State in 1 sentence what the learner will be able to derive or critique when done.
   - **End your turn** and wait for confirmation before starting Step 1.

### Phase 3: Motivated Co-Reading & Nested `learn`

Walk through the confirmed roadmap **one step at a time** (on major landmark transitions or when resuming from a nested `learn` branch, show a single-line progress strip such as `[✓] 1 → [→] 2 → [ ] 3` rather than re-printing the full roadmap):
1. **Motivate → One Step → Check → Repair**:
   - **Motivate**: Show the exact failure mode or equation bottleneck before introducing the author's design (*"If we naively compute X here, what breaks?"*).
   - **One Step at a Time**: Walk through one derivation step, formula transformation, or architectural module per turn. Explicitly separate **structural/mathematical necessity** (`[必然推导]`) from **empirical/engineering design choices** (`[经验权衡]`).
   - **Check Understanding**: End with one applied check question (e.g., *"Why couldn't the authors drop this term?"* or *"Under what regime does this assumption fail?"*) and inspect the learner's reasoning.
   - **Repair Immediately**: Fix misconceptions on the spot before advancing; if a hidden gap appears, explicitly show the inserted branch on the roadmap.
2. **Nested `learn` Sub-Loop for Deep Prerequisite Gaps**:
   - When the paper hits an unfamiliar standalone concept that cannot be resolved in a 1-sentence reminder:
     1. Explicitly **pause the paper roadmap** at the current step (`[→ 暂停]`) and show the nested branch.
     2. Switch to the **`learn` skill** workflow (`Probe → Mini-Plan → Teach/Check`) until that prerequisite concept feels obviously true.
     3. **Compile the prerequisite concept immediately**: write `notes/<概念名>.md` using `_templates/concept-note.md` and update `index.md` under `## 概念与主题 (Concepts)` so the learner can revisit and review it throughout the rest of the paper.
     4. Mark the prerequisite `[✓]` and **resume the paused paper step** with `[[概念名]]` now locked in as a verified anchor.

### Phase 4: Compile Paper Note & Archive Source (`notes/` + `index.md` + `.raw/`)

Only when the paper walkthrough finishes (or when the learner explicitly asks to save):
1. **Write or Upgrade `notes/<论文简称或标题>.md`**:
   - Follow `_templates/paper-note.md` and set `status: deep` (filling `authors`, `year`, notation, algorithm flow, and key page/equation provenance anchors such as `p.4, Eq.(12)` naturally inside `## 问题与方法`). If upgrading an earlier `skim` note for this paper, update that existing file rather than creating a duplicate.
   - Keep `## 问题与方法` readable with short paragraphs and continuous `$$ \begin{aligned} ... \end{aligned} $$` blocks; weave Obsidian `[[双链]]` cleanly across YAML (`prerequisites`, `concepts`, `related`), natural prose references, and `## 自测与关联` (reusing exact `index.md` titles, avoiding dangling links). Keep `[[wikilinks]]` outside `$...$`/`$$...$$`, quote YAML wikilinks, avoid `[...]` premise wrappers and prose `$\implies$`. Do **not** save the session's temporary Mermaid roadmap into `notes/`.
   - Record the learner's personal **Click** in `## 批注与疑问` and 2–3 **Retrieval Cues** in `## 自测与关联`.
2. **Archive Processed Source to `.raw/`**:
   - If the source file came from `inbox/`, move it into `.raw/` (creating `.raw/` if needed) and set/update `source: ".raw/<filename>"` in the paper note's YAML frontmatter.
3. **Optional Additional Concept Extraction**:
   - If a general, reusable mechanism emerged during paper derivation that wasn't already compiled via a nested `learn` sub-loop, ask if the learner wants a standalone `notes/<概念名>.md` created and linked.
4. **Feed Back & Back-Link Existing Notes (Compile, Don't Just Append)**:
   - Review the existing `[[概念]]` and predecessor `[[论文]]` notes referenced in this session: did this paper reveal a **new scope boundary, failure mode, counterexample, or contradiction** to any of them?
   - If yes (only when genuinely warranted—never pad), incrementally update that existing note's `机制与推导` / `顿悟与误区`, add `[[新论文]]` to its `sources` / `related` and `## 自测与关联`, and bump `updated:`. Even when no boundary changed, add `[[新论文]]` to a direct predecessor paper's `related` / `## 自测与关联` so lineage links stay bidirectional.
5. **Update `index.md`**:
   - Append or update the paper entry under `## 论文与文献 (Papers)` with `[deep]` (switching `[skim]` to `[deep]` if upgraded).
