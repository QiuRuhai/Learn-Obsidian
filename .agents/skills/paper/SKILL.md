---
name: paper
description: >-
  Use this skill when the user wants to read, understand, or digest a paper,
  article, PDF, or document (especially from inbox/). Supports inbox/ lineage
  triage, fast Skim & Ingest (Mode A), and Deep Co-Reading (Mode B: LearnHarness
  probe -> reading roadmap -> three-part derivation with computational dataflow
  and nested `learn`), then compiles linked notes into notes/, index.md,
  archives to .raw/, and verifies via scripts/lint-vault.py.
---

# Paper Co-Reading Skill (Dual-Mode LearnHarness × Obsidian Wiki)

Reading a paper is not summarizing sections from Abstract to Conclusion. Depending on the paper's priority to the learner, route cleanly between **fast structural ingestion** and **motivated deep co-reading** (pausing to invoke the `learn` flow whenever a deep prerequisite gap blocks derivation). Conduct all explanations, checks, and note writing primarily in **Simplified Chinese**, naturally retaining standard **English technical terms**.

## Phase 1: Triage, Lineage Radar & Mode Routing

1. **Read Context (Progressive & Lineage-Aware)**:
   - Read `index.md` to see which concepts and papers the learner already holds.
   - **Lineage Triage (`inbox/` 阅读雷达)**: When the user asks how to tackle `inbox/` (e.g., choosing reading order across multiple unread PDFs) **or** selects a paper whose foundational ancestor is also sitting unread in `inbox/`, perform a quick lineage triage by scanning `inbox/` filenames/titles alongside `index.md` (do **not** parse all PDFs in full):
     - Classify unread papers into 4 lineage buckets:
       1. **基座方法论文 (Root Method Papers)** — foundational forward formulations or solvers;
       2. **可微扩展论文 (Differentiable Extensions)** — works differentiating through or modifying a root solver;
       3. **接触 / 物理建模论文 (Contact & Physics Models)** — contact, friction, smoothing, or boundary formulations;
       4. **反思 / 诊断分析论文 (Critique & Analysis Papers)** — empirical or theoretical studies showing when gradients, surrogates, or solvers break.
     - Identify the missing ancestor(s) and explicitly advise whether to:
       - **先 `Mode A` 速览基座前作**：when only the baseline formulation, notation, and bottleneck are needed before reading the extension;
       - **先 `Mode B` 精读基座前作**：when the target paper directly differentiates through, re-factorizes, or modifies the root solver's inner loop; or
       - **直接读当前论文**：when `index.md` already holds the ancestor or core prerequisites.
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
     - **Mode A｜速览入库 (Skim & Ingest)** — for lower-priority papers or quick ancestor passes where a structural overview and linked Obsidian note are enough; or
     - **Mode B｜精读啃透 (Deep Co-Reading)** — for core papers they want to derive, verify, and truly own.
   - If choosing **Mode B** (or if already specified), probe their edge in the same turn (strictly **1–2 turns max** to avoid interrogation fatigue, calibrating across the 4 quadrants: solid reasoning → prune; guessed/recited → pseudo-fluency trap to verify; wrong with valid intuition → anchor & repair; blank/"不会" → set floor immediately):
     - Their reading goal (e.g., grasp core mechanism, reproduce math/derivations, or critique trade-offs);
     - Which of the listed prerequisites (or predecessor paper deltas) they already hold vs. need to learn; run 1 high-level check question if a load-bearing prerequisite is subtle.

---

## Mode A: Skim & Ingest (Fast Path)

Use **only** for lower-priority papers (or baseline ancestors needing only high-level framing) where step-by-step teaching is unnecessary:
1. **Tight Source-Grounded Digest**:
   - Present a concise structural summary: `瓶颈 → 核心洞察 → 方法骨架 → 计算代价与失效边界 → 潜在前置概念` (linking existing `[[概念]]` / `[[论文]]` from `index.md`, and flagging any unfamiliar concepts as unverified rather than faking comprehension).
2. **Compile Paper Note, Archive Source & Lint**:
   - Follow `_templates/paper-note.md` to write `notes/<论文简称或标题>.md` with `status: skim` (fill `authors`, `year`, and key page/equation provenance anchors inside `## 问题与方法`; in `## 批注与疑问`, write `待深挖疑问 (Open Questions)` instead of fabricating unverified insights; wire `prerequisites`/`concepts`/`related` with quoted YAML wikilinks and `## 自测与关联` without creating dead links to unverified concepts).
   - If the source file came from `inbox/`, move it into `.raw/` (creating `.raw/` if needed) and set `source: ".raw/<filename>"` in the paper note so `inbox/` stays a clean unread queue.
   - Update `index.md` under `## 论文与文献 (Papers)` with `[skim]` (using `### <领域名称>` subheadings whenever `Papers` spans multiple disciplines) and auto-assign `tags: [domain, subtag1, subtag2]` with a canonical primary domain first.
   - **Run Vault Lint**: Execute `python3 scripts/lint-vault.py` immediately after updating `notes/` and `index.md`, and fix any reported errors (dead links, `index.md` drift, unquoted YAML wikilinks, `.raw/` archive mismatch, or MathJax × `[[双链]]` collisions) before finishing.
3. **Instant Escalation**:
   - If any specific mechanism in the digest catches the learner's interest, immediately switch to **Mode B** focused on that mechanism.

---

## Mode B: Deep Co-Reading (LearnHarness + Nested `learn`)

### Phase 2: Minimal Reading Roadmap (Plan & STOP)

Once the learner's goal and prerequisite gaps are bracketed:
1. **Construct the Minimal Tree (Delta-First When Lineage Exists)**:
   - Prune background already held (from `index.md`, probe, or a direct predecessor `[[论文]]` note) and tangential sections/experiments not needed for the core mechanism.
   - When a predecessor paper is already held, anchor the roadmap at the **Delta**—the exact regime where the predecessor breaks under the new goal.
   - Order the remaining path as `[前置补洞]` → `[必然推导]` / `[经验权衡]` / `[计算数据流]`, verifying strict topological order (each step depends only on confirmed anchors or earlier steps, never forward-referencing later steps).
2. **Present the Roadmap and STOP**:
   - **Pruned Anchors & Skipped Sections**: Explicitly state which existing `[[概念]]` anchors and paper sections are skipped so the learner can correct any wrong assumption.
   - **Non-Spoiler Landmarks (3–6 steps)**: Show the reading roadmap using status markers (`[✓]` / `[→]` / `[ ]`) and node tags (`[前置补洞]` / `[必然推导]` / `[经验权衡]` / `[计算数据流]`). Frame each landmark as a *bottleneck or question to resolve*, **never spoiling the author's trick or final formula** (keep `Predict` alive).
   - **Temporary Visualization**: Use a numbered list for linear paths; when **multiple prerequisite branches converge** onto the paper's core design, attach a compact in-chat Mermaid diagram (`flowchart TD` / `LR`, 4–6 nodes) as a temporary scaffold (never saved into `notes/`).
   - **Completion Criterion**: State in 1 sentence what the learner will be able to derive or critique when done.
   - **End your turn** and wait for confirmation before starting Step 1.

### Phase 3: Motivated Co-Reading & Nested `learn`

Walk through the confirmed roadmap **one step at a time** (on major landmark transitions or when resuming from a nested `learn` branch, show a single-line progress strip such as `[✓] 1 → [→] 2 → [ ] 3` rather than re-printing the full roadmap):
1. **Motivate → One Step (Three-Part Separation) → Faded Check → Repair**:
   - **Motivate**: Show the exact failure mode or equation bottleneck before introducing the author's design (*"If we naively compute X here, what breaks?"*).
   - **One Step at a Time (Three-Part Separation)**: Walk through one derivation step, formula transformation, or algorithmic stage per turn, explicitly separating three distinct aspects:
     1. **`[必然推导]` (Structural / Mathematical Necessity)**: what follows strictly from base definitions, KKT / implicit differentiation, conservation laws, or linear algebra;
     2. **`[经验权衡]` (Empirical / Engineering Trade-off)**: heuristics, smoothing schedules, iteration truncation, or penalty choices made for speed/stability;
     3. **`[计算数据流]` (Computational Dataflow — Forward Once vs. Backward Reuse)**: explicitly trace what is computed, assembled, or pre-factored **once during forward** (e.g., Jacobian assembly, matrix factorization such as `[[Cholesky 预分解]]`, active-set masks, checkpointed states) vs. what is **reused, transposed, or re-solved during backward** (e.g., adjoint solve reuse, vector-Jacobian products, memory vs. recomputation trade-off).
   - **Worked-Example Fading & Check**: On key equation transitions, walk through a compact low-dimensional trace (e.g., $2 \times 2$ system or 2-step rollout) and fade out the critical algebraic step or backward-reuse step for the learner to complete in `Check` (alongside explaining *why*—never ask for passive recitation).
   - **Repair Immediately (With Fading Hints)**: Fix misconceptions on the spot before advancing. When the learner misses a faded step or boundary check, first give a 1-sentence structural/dimensional hint pointing back to the unconditional premise or dataflow invariant before giving away the full answer; if a deeper prerequisite gap surfaces, explicitly show the inserted branch on the roadmap.
2. **Non-Mainline Side-Note Routing (`Nested learn` vs. `📌 待沉淀支线`)**:
   - **Case 1 — Local notation / one-off trick**: explain in 1–2 sentences inline and keep inside the paper note; never nominate as a standalone note.
   - **Case 2 — Blocking foundational gap (`Nested learn` Sub-Loop)**: when a standalone prerequisite blocks derivation and cannot be cleared with a 1-sentence reminder:
     1. Explicitly **pause the paper roadmap** at the current step (`[→ 暂停]`) and show the nested branch.
     2. Switch to the **`learn` skill** workflow (`Probe → Mini-Plan → Teach/Check`) until that prerequisite concept feels obviously true.
     3. **Compile the prerequisite concept immediately**: write `notes/<概念名>.md` using `_templates/concept-note.md` (with auto-assigned `tags`), update `index.md` under `## 概念与主题 (Concepts)` (`### <领域名称>`), and verify with `python3 scripts/lint-vault.py` so the learner can revisit and review it throughout the rest of the paper.
     4. Mark the prerequisite `[✓]` and **resume the paused paper step** with `[[概念名]]` now locked in as a verified anchor.
   - **Case 3 — Non-blocking reusable concept (`📌 待沉淀支线` Side-Note Parking)**: when a brief explanation lets the learner keep moving cleanly on the paper, **and** either (a) it is a standard named tool that connects to existing `index.md` notes or future `inbox/` papers, **or** (b) the learner asked a follow-up question about it / said "记一下", do **not** derail co-reading; append a 1-line bookmark in chat (max 1–3 per paper):
     `📌 待沉淀支线：<概念名>（<1句跨场景价值或与已有[[笔记]]的关联>）`

### Phase 4: Compile Paper Note, Archive Source & Lint (`notes/` + `index.md` + `.raw/`)

Only when the paper walkthrough finishes (or when the learner explicitly asks to save):
1. **Write or Upgrade `notes/<论文简称或标题>.md`**:
   - Follow `_templates/paper-note.md` and set `status: deep` (filling `authors`, `year`, notation, forward-backward computational dataflow, concrete low-dimensional trace, explicit failure boundaries, and key page/equation provenance anchors such as `p.4, Eq.(12)` naturally inside `## 问题与方法`). If upgrading an earlier `skim` note for this paper, update that existing file rather than creating a duplicate.
   - Keep `## 问题与方法` readable with short paragraphs and continuous `$$ \begin{aligned} ... \end{aligned} $$` blocks; weave Obsidian `[[双链]]` cleanly across YAML (`prerequisites`, `concepts`, `related` with quoted `"[[...]]"`), natural prose references, and `## 自测与关联` (reusing exact `index.md` titles, avoiding dangling links). Keep `[[wikilinks]]` outside `$...$`/`$$...$$`, never wrap `$...$` inside `**...**`, avoid `[...]` premise wrappers and prose `$\implies$` (use `⟹` in prose chains). Do **not** save the session's temporary Mermaid roadmap into `notes/`.
   - Automatically assign YAML `tags: [domain, subtag1, subtag2]` (first tag = canonical primary domain such as `physics`, `math`, `finance`, `cs`, reusing existing vault tags) without asking the learner to invent tags, and populate `aliases` with common abbreviations / full title variants.
   - Record the learner's personal **Click** in `## 批注与疑问` and 2–3 blind scenario-based **Retrieval Cues** in `## 自测与关联` (framed as problem/failure scenarios that do not spoil the paper's trick).
2. **Archive Processed Source to `.raw/`**:
   - If the source file came from `inbox/`, move it into `.raw/` (creating `.raw/` if needed) and set/update `source: ".raw/<filename>"` in the paper note's YAML frontmatter.
3. **Resolve Parked Side-Notes (`📌 待沉淀支线`)**:
   - Present the parked `📌 待沉淀支线` items collected during Phase 3 (plus any reusable mechanism that surfaced). For each item, the learner decides:
     - **Learn & extract now**: run a compact `learn` loop, compile `notes/<概念名>.md`, and link bidirectionally with the paper note; or
     - **Defer**: record `- **待沉淀支线**：<概念名>（<理由>）` under `## 批注与疑问` so it stays discoverable for a future session.
4. **Feed Back & Back-Link Existing Notes (Compile, Don't Just Append)**:
   - Review the existing `[[概念]]` and predecessor `[[论文]]` notes referenced in this session: did this paper reveal a **new scope boundary, failure mode, counterexample, or contradiction** to any of them?
   - If yes (only when genuinely warranted—never pad), incrementally update that existing note's `机制与推导` / `顿悟与误区`, add `[[新论文]]` to its `sources` / `related` and `## 自测与关联`, and bump `updated:`. Even when no boundary changed, add `[[新论文]]` to a direct predecessor paper's `related` / `## 自测与关联` so lineage links stay bidirectional.
5. **Update `index.md` & Run Vault Lint**:
   - Append or update the paper entry under `## 论文与文献 (Papers)` with `[deep]` (switching `[skim]` to `[deep]` if upgraded, using `### <领域名称>` subheadings when `Papers` spans multiple disciplines).
   - Execute `python3 scripts/lint-vault.py` after writing/updating notes, updating `index.md`, and archiving the PDF from `inbox/` to `.raw/`. Resolve any reported errors before closing.
