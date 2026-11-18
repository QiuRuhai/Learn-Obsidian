---
name: paper
description: >-
  Use this skill when the user wants to read, skim, deeply understand, or
  upgrade an already-skimmed `[skim]` paper note to `status: deep` (via `inbox/`
  or `.raw/`). Supports inbox/ lineage triage, fast Skim & Ingest (`Mode A`),
  and Deep Co-Reading (`Mode B` with LearnHarness probes, adaptive solver/theory
  walkthroughs, and nested `learn`). Do NOT use for standalone concepts without a
  paper source (`learn`), pure memory quizzes (`review`), or multi-note
  comparisons (`synthesize`).
---

# Paper Co-Reading Skill (Dual-Mode LearnHarness × Obsidian Wiki)

Reading a paper is not summarizing from Abstract to Conclusion. Route cleanly between **fast ingestion (`Mode A`)**, **`[skim]` → `[deep]` upgrade**, and **motivated deep co-reading (`Mode B`)**, invoking `learn` only when a ≥3-step blocking prerequisite stalls derivation. Conduct all dialogue and note writing in **Simplified Chinese**, keeping standard **English technical terms**.

## Phase 1: Triage, Lineage Radar & Mode Routing

1. **Read Context (Progressive & Grounded)**:
   - Read `index.md` first (including `## 待沉淀支线 (Backlog)`). Read 1–2 directly intersecting prerequisites or related papers—covering **both** predecessors (`[[前作论文]]`), already-digested descendant papers (`[[后续论文]]`, e.g., reading Bouaziz 2014 after DiffPD), and any `[skim]` prerequisite **or** candidate-paper-grounded `[skim]` concept notes (reading their `> [!question] 待深挖断点` so you never assume unencoded algebra as `[✓]`, and surfacing upgrade synergy during triage).
   - **`[skim]` Direct Re-Entry**: **IF** the requested paper already exists in `index.md` as `[skim]`, read `notes/<Paper>.md`, link both it and `.raw/<filename>` via clickable `[basename](file:///...)` anchors in chat, and access the PDF directly via its YAML `source: ".raw/<filename>"`. **Skip the Mode A / Mode B menu**, jump straight into **Mode B**, and (unless already warmed up via `review`) anchor your 1–2 turn free-text probe directly on its `> [!question] 待深挖疑问` and hardest prerequisite.
   - **Adaptive `inbox/` Lineage Triage (`阅读雷达`) + Hard Prerequisite Gate**: When tackling `inbox/` or a paper with unread ancestors/descendants in `inbox/`, group `inbox/` filenames/titles dynamically by the **vault's actual research domains** (never force physics-only buckets onto finance/CS/systems papers). **Hard Prerequisite Gate**: recommend reading a predecessor first *only* when its internal derivation is a black-box prerequisite of the target paper's main equations; baselines cited only in experiments/evaluation (e.g., IPC in a contact-gradient diagnostic paper) need only a 1–2 line summary, not a prerequisite detour.
   - **Strict Grounding**: Inspect target PDF pages directly before teaching; never reconstruct equations, subscripts, indices, or algorithm numbers from memory.
2. **Surface the Spine (4–6 Lines)**:
   - State: (a) prior bottleneck attacked, (b) 1-line end-to-end operational flow + single load-bearing insight (or **Ancestor Delta** if a descendant paper is already in `notes/`), and (c) 2–4 prerequisites (pairing held `index.md` notes with clickable `file://` links in chat while keeping `notes/` pure `[[wikilinks]]`).
3. **Route Cleanly (Wait Unless Specified or Upgrading `[skim]`)**:
   - Present lineage recommendation + Mode summary in chat and use `ask_question` when choosing an `inbox/` PDF and/or routing between **`(Recommended) Mode B｜精读啃透`**, **`Mode A｜速览入库 ([skim])`**, and **`前置盲测热身 (review → Mode B)`**—skip `ask_question` if Turn 1 already specified `Mode B` or on `[skim]` Direct Re-Entry.
   - Once **Mode B** starts (unless warmed up via `review`), run a **1–2 turn free-text calibrated probe** (never `ask_question`) isolated inside `---` + `> **Probe｜<纯文字短标题>**` ending with certainty cue (*“用 1–2 句话写判断和理由，拿不准可注明‘猜的/模糊’，不会直接说‘不会’”*), **STOP** immediately, apply Conservative Anti-Charity, and exit Turn 1 on clean `[Q1]` (`[Q1]` Solid Floor, `[Q2]` Pseudo-Fluency, `[Q3]` Near-Edge, `[Q4]` Floor Boundary)—carrying any `[Q2]`/`[Q3]`/`[Q4]` prerequisite gap directly into Phase 2 so unfamiliar basics are explained inside the global pipeline overview.

---

## Mode A: Skim & Ingest (Fast Path, Zero-Turn Interactive)

1. **Tight Source-Grounded Digest**:
   - Summarize `瓶颈 → 核心洞察 → 方法/诊断骨架 → 代价与失效边界 → 潜在前置概念` (linking existing `index.md` notes; strictly non-exam, no closing quiz).
2. **Compile Paper Note, Wire Lineage, Archive & Lint**:
   - Write `notes/<论文简称或标题>.md` via `_templates/paper-note.md` (`status: skim`, `authors`, `year`, `aliases`, 2–3 `kebab-case` `tags`, content-driven `##` headings, page/equation provenance anchors). Replace `[!tip]` with `> [!question] 待深挖疑问` recording one **Trigger Condition + Most Suspect Unverified Assumption** pair, and write 1–2 blind zero-spoiler `自测线索` (never leaking `title`/`aliases`, grounded in body prose).
   - Wire symmetric `related` links across already-digested predecessor/descendant papers (even in Mode A) while keeping `prerequisites` / `concepts` / `related` strictly disjoint.
   - Move `inbox/` source file to `.raw/` (`source: ".raw/<filename>"`), update `index.md` (`[skim]`), and run `python3 -B scripts/lint-vault.py`.

---

## Mode B: Deep Co-Reading (LearnHarness + Nested `learn`)

### Phase 2: Panorama Pipeline Walkthrough, Prerequisite Patching & Roadmap (Working Hypothesis & STOP)

1. **Prerequisite-Aware Pipeline Integration (Driven by Phase 1 `Probe`)**:
   - Prune held `evergreen`/`[Q1]` anchors, digested `[skim]` paper spine, and known baseline/descendant techniques from active Phase 3 derivation while keeping `[✓]` anchors *in-place* inside the macro pipeline (skip full pipeline staging only on `1–2` step `[skim]` tail upgrades). For any prerequisite marked `[skim]` in `index.md`, **half-prune**: prune its `已验直觉` (`[✓]`) and keep its `卡壳断点` equations on the active roadmap.
   - **IF Phase 1 `Probe` surfaced unfamiliar or shaky prerequisites (`[Q2]`/`[Q3]`/`[Q4]`)**: **weave a clear, intuitive mini-explanation of those prerequisites and their role directly into Phase 2's global pipeline walkthrough** so missing basics never leave holes in the big picture, and retain `[前置补洞]` on the roadmap whenever `≥3`-step derivation is also needed. Strip internal rubric tags (`[必然推导]`/`[经验权衡]`/`[计算数据流]`/`[反例与定理边界]`) from landmark titles.
2. **Present Thorough End-to-End Pipeline + Key Impressions & Signposts + Landmarks & STOP**:
   - **Stage 1 — Full End-to-End Pipeline Walkthrough (`全景流程讲透，直接挑明顶层思路，不卡死行数`)**: Never compress into cryptic 3–5 line slogans or withhold high-level spoilers. Use **2–4 natural, causally connected paragraphs + a clear stage breakdown** (and/or chat-only `Mermaid` diagram with readable labels) to walk through the complete pipeline from input to output (`Precompute → Forward → Backward` or `Problem Setup → Lemma Chain → Main Bound/Theorem`), **openly explaining the paper's core breakthrough idea**, how data/claims pass across stages, and any prerequisite background surfaced by `Probe`. Include **1 conditional `符号防撞：` line** if core symbols flip roles against held `notes/`, and **at most 1 top-level governing `$$...$$` equation** (with plain-Chinese role labels) if anchoring the master equation clarifies the whole system—deferring only **multi-step local algebraic derivations** to Phase 3.
   - **Stage 2 — Key/Hard Part Impressions & Derivation Previews (`重难点先给直观印象 + 重点预告`)**: Highlight **2–3** **`[重点深挖 k：<难点/核心模块>]`** inside the pipeline: **first explain in plain Chinese why this part is hard/vital and what intuitive trick/mechanism makes it work** (spoilers encouraged so the learner builds a clear mental impression upfront), then explicitly signpost *"等下在第 X 步我们会重点把这里的具体推导一步步讲透"*.
   - List 3–6 ordered landmarks (`[✓]` pruned anchors inline / `[→]` / `[ ]`) + 1-sentence completion criterion, then **STOP** and wait for confirmation.

### Phase 3: Stepwise Deep Derivation & Genre-Adaptive Walkthrough (`Teach Clearly → Check Rigorously`)

Walk **1 load-bearing step per turn** using a clean **3-Zone Chat Layout**:
- **Zone 1 (Progress, Pipeline Locator & Lock)**: `` `[✓] 1. ...` → **`[→] 2. ...`** → `[ ] 3. ...` `` (or `2.a/2`), followed by a **1-clause Pipeline Locator** (`流程定位：<所属全局环节>｜[正在深挖重点 k]` or `[重点 k 已推通 ⟹ 交接至…]`) anchoring where the current equation plugs into Stage 1's global flow + 1 factual line locking what the prior reply established (never empty praise or yes/no hints).
- **Zone 2 (Causal Bridge & Readable Math)**: Bridge causally from the prior step (`上一步… ⟹ 这一步…`) with **5 In-Chat Equation Rules**: (1) 1-line plain-Chinese intent sentence (`≤1` symbol) before every `$$...$$`; (2) **at most 1 primary `$$...$$` block per turn** with `\underbrace{...}_{\text{角色}}` or 2–3 role bullets right below; (3) cap inline math at `≤2` atomic `$...$` spans per clause (no inline `\frac`, norms, transposes, or `\sum`); (4) write out non-trivial chain-rule, transpose, or projection steps explicitly; (5) de-alias colliding chat indices with a ≤5-word bridge to PDF notation. Track genuine learner errors silently for Phase 4 `易错陷阱：...`.
- **Zone 3 (Isolated Prompt & Hard Stop)**: Put the single free-text question (never `ask_question`) inside `---` + `> **Check｜<纯文字短标题>**` (or rare `Predict`; no `$...$` in bold) and **STOP**.

1. **Genre-Adaptive `Teach → Check → Repair` Strategy**:
   - **Teach Clearly First, Check Concrete Understanding After**: Do **not** withhold core mechanisms as a guessing game. On each step, **explain and derive the concrete content clearly first** (`Intuition-First`: ground multi-index/tensor calculus in a 1D/scalar/2-DOF miniature *first*, then lift to full equations and lock object signatures—dimensions, units, or state sets; fade worked scaffolds across steps toward diagnostic boundary checks). Reserve `Predict` strictly for rare counterintuitive numerical paradoxes *after* equations are on the table (`Predict Fast-Forward` if used).
   - **Branch by Paper Genre** (do not force solver templates onto theory papers):
     - **`[必然推导]` vs. `[经验权衡]`**: Contrast only at genuine compromises where exact fidelity/generality is traded for tractability;
     - **Solver / Algorithm steps (`[计算数据流]`)**: After 1D intuition holds, trace a **2-Frame Rollout & Resource Lifetime** (`Precompute once → Forward t→t+1 cache (minimal save_for_backward state tuple vs. discarded inner iterates) → Backward t+1→t reuse`) + 1-line **solver-primitive invariant** (e.g., never materialize $A^{-1}$), allowing boundary `Check`s to probe where analytic adjoints diverge from finite-difference checks (or why relaxed solver `tol` preserves descent);
     - **Theory / Diagnostic steps (`[反例与定理边界]`)**: Anchor on a minimal 1D/scalar counterexample (e.g., step discontinuity, scalar chaotic map) before extracting the governing variance/Lipschitz/stiffness bound.
   - **Unified Warrant-Coupled `Check`, `k.a → k.b` Micro-Stepping & 2-Turn `Repair`**:
     - End Zone 3 with **1 unified free-text `Check`** (verifying the concrete derivation step, governing condition/signature, or failure boundary in one cohesive question) and **STOP**. Apply Conservative Anti-Charity: parroting Phase 2's high-level summary without the concrete mathematical warrant never unlocks `[✓]`.
     - Auto-downshift into **`[→] k.a/2` (1D 直觉) → `[→] k.b/2` (全文公式升维与签名)** whenever hitting `≥3`-layer equations, `[skim]` `卡壳断点` from `L48`, or `"慢一点 / 没看懂 / 帮我拆一下"` (non-punitive: 0 `Repair` strikes; macro `[✓] k` unlocks only on `k.b`, then auto-upshifts). Repair with max 1 Level-1 hint before explaining cleanly at Level 2.
2. **Side-Note & Reusable Primitive Routing + Multi-Session Pause**:
   - *1–2 turn patch*: inline;
   - *Blocking ≥3-step prerequisite (`Nested learn`)*: pause `[→ 暂停]`, run `learn` (skipping `learn` Phase 1 probe; saving `sources: []` temporarily if `ParentPaper.md` doesn't exist yet), lint, and return (optionally hint `/compact` before synthesizing back into `ParentPaper` in long sessions);
   - *Non-blocking tangent or native cross-paper primitive (`📌 待沉淀支线`)*: silently track both off-axis side concepts **and** 1–2 native reusable primitives introduced by this paper that transfer across `≥1` other `notes/`/`inbox/` route (`> 支线暂记：<概念名>` in chat only on `"记一下"`, max 3/paper total) so Phase 4's batch triage prevents `concepts: []` / `Backlog` leakage;
   - *Pause*: output a 4-line in-chat **Resume Anchor** without writing partial files to `notes/`.

### Phase 4: Gate, Compile / Upgrade, Archive, Backlog & Lint

1. **Active Pipeline Reconstruction Gate (`回扣总体流程闭环`) & Fatigue Bailout**:
   - Re-display **only** Stage 1's bare stage skeleton + `[重点 k]` slot names (without Phase 2's explanatory prose) and ask in **1 single turn** for the learner to stitch the derived mechanisms back across the overall workflow in 2–4 plain sentences (`前作瓶颈 ⟹ 各重点环节如何靠具体机制串起全局数据流/定理链 ⟹ 主失效边界`), then **STOP**; apply Conservative Anti-Charity and fold any stitching gap into `> [!warning] 易错陷阱：`. **Bypass** on `"存笔记 / save note"`. (If the learner bails out mid-Phase 3 with `"看不进去/推不动/先出笔记"` while unverified steps remain, skip this quiz and compile honestly as `status: skim` with `> [!question] 待深挖疑问`.)
2. **Write or Upgrade `notes/<论文简称或标题>.md` (`claude-obsidian` Narrative Style)**:
   - Follow `_templates/paper-note.md` (`status: deep`), adapting headings cleanly to solver vs. theory papers (`## <直白标题 2：核心机制与推导主线>`). When upgrading `[skim]` → `[deep]`, edit the existing file in place: preserve `created:` and `source: ".raw/..."`, set `status: "deep"`, bump `updated:`, replace `[!question]` with verified `[!tip]`, populate `concepts:`, and verify every page/equation/algorithm citation directly against the PDF.
   - **Two-Tier Symbol Binding & Signal-Bearing Warnings**: Define 3–5 core symbols upfront and local symbols right before their equation. Embed `> [!tip]` near the key click; under `## 适用边界与局限`, use **`> [!warning] 易错陷阱：<盲点短标题>`** if Phase 1–4 exposed a real blind spot/repair (objective technical tone; ≥1 `自测线索` targets it), else **`> [!warning] 常见误区：<边界短标题>`**.
   - **Disjoint YAML Edges & Zero-Spoiler Cues**: Keep `prerequisites`, `concepts`, and `related` strictly disjoint (never copy YAML links to the bottom). Write 2 blind `自测线索` grounded in body derivations and **NEVER** containing `title` or `aliases`.
3. **Archive, Backfill Nested `learn` & Batch-Triage Backlog**:
   - Move `inbox/` PDF to `.raw/` (`source: ".raw/<filename>"`) unless already there (`[skim]` upgrade).
   - **Backfill `sources` & Upgrade Covered `[skim]` Concepts**: for any prerequisite compiled mid-paper with `sources: []` **or** any pre-existing concept (including `[skim]` concepts resolved during this paper) grounded in this paper, append `"[[<论文简称或标题>]]"` into its `sources` and wire it cleanly into the paper's `prerequisites` or `concepts`. If a `[skim]` concept's `卡壳断点` was verified during co-reading, upgrade it in place (`status: skim → evergreen`, `[!question] → [!tip]`, update `自测线索`, bump `updated:`, and remove `[skim]` in `index.md`).
   - Batch-triage `📌 待沉淀支线` (`暂存 Backlog / 抽成独立笔记 / 忽略`); when `≥2` side-notes exist post-compile in a non-bailout session, use 1 batched `ask_question`. Log deferred items in `index.md` under `## 待沉淀支线 (Backlog)` (soft cap 8) with plain bold `**<概念名>**`.
4. **Feed Back Lineage & Contradictions (Avoiding Catch-22 Cycles)**:
   - Wire symmetric `related` links onto **direct predecessor/descendant papers** (whether skimmed or deep); if the newly wired competing/lineage cluster reaches `≥3` notes without an existing `type: synthesis` note, include a 1-line optional `synthesize` pointer in your final report.
   - **NEVER** push `"[[新论文]]"` into an upstream `[[概念]].related` when `[[新论文]].prerequisites` already lists `[[概念]]`—instead, if the paper refines a foundational concept's boundary or exposes a contradiction, add a prose cross-reference / `> [!warning] 跨文献冲突：...` inside the concept's body and bump its `updated:` without duplicating the YAML edge.
5. **Update `index.md` & Run Lint**:
   - Add/flip the paper entry in `## 论文与文献 (Papers)` → `### <领域名称>` (`[deep]`, ~15–25 char summary). Run `python3 -B scripts/lint-vault.py` and resolve all errors and warnings before finishing, then report compiled `notes/<论文简称或标题>.md` & `index.md` in chat via clickable `[basename](file:///...)` anchors.
