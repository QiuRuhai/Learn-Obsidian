#!/usr/bin/env python3
"""Zero-dependency Obsidian vault linter for MyVault.

Checks:
1. Index <-> Notes Sync (index.md <-> notes/*.md), Backlog exemption & paper status sync
2. Dead / Dangling [[wikilinks]] and #Heading targets in index.md and notes/*.md
3. YAML Frontmatter Hygiene (required fields, enums, dates, tags, disjoint edge sets, quoted [[...]], no $ in title/aliases)
4. Obsidian MathJax x [[wikilink]] Iron Rules & Placeholder / Leaked Pedagogy Tag checks
5. Scoped Structural Link Symmetry & .raw/ Archive Integrity for paper notes
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
import re
import sys

REQUIRED_FRONTMATTER_FIELDS = ("title", "type", "created", "updated", "status")
EDGE_FIELDS = ("prerequisites", "concepts", "sources", "related")
VALID_TYPES = ("concept", "paper", "synthesis")
VALID_STATUS_BY_TYPE: dict[str, tuple[str, ...]] = {
    "concept": ("skim", "evergreen", "superseded"),
    "paper": ("skim", "deep", "superseded"),
    "synthesis": ("evergreen", "superseded"),
}

WIKILINK_RE = re.compile(r"\[\[([^\[\]\n]+?)\]\]")
MATH_DOLLAR_RE = re.compile(r"(?<!\\)\$")
IMPLIES_RE = re.compile(r"\\implies(?![A-Za-z])")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KEBAB_TAG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TEMPLATE_PLACEHOLDER_RE = re.compile(r"\{\{(?:title|date|status|inbox_file|[A-Za-z_][A-Za-z0-9_]*)\}\}")
PEDAGOGY_TAG_RE = re.compile(r"\[(必然推导|经验权衡|计算数据流|反例与定理边界|前置补洞)\]")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)(?:\s+#+)?\s*$")
TOP_H2_RE = re.compile(r"^\s{0,3}##(?!#)\s+(.+?)(?:\s+#+)?\s*$")
CATALOG_ENTRY_RE = re.compile(r"^\s*[-*+]\s+(?:\[[^\]]+\]\s*)?\[\[([^\[\]\n]+?)\]\]")
BLOCKQUOTE_PREFIX_RE = re.compile(r"^(?:\s*>\s?)+")
SKIM_CALLOUT_RE = re.compile(r"^\s*\[!(tip|question)\b", re.IGNORECASE)
CHAT_SCAFFOLD_PROSE_RE = re.compile(
    r"(?:<agent-embed\b|file:///|\[✓\]|\[→(?:\s*暂停)?\]|\[(?:重点深挖|正在深挖重点|重点\s*\d+\s*已推通|重点待拆黑盒|正在拆解黑盒|黑盒\s*\d+\s*已拆通)[^\]]*\]|(?:流程定位|符号防撞)\s*[：:])",
    re.IGNORECASE,
)
CHAT_PROMPT_BQ_RE = re.compile(r"^\s*(?:Probe|Predict|Check|Review|支线暂记)\s*[｜:|：]")
CHAT_PROGRESS_LINE_RE = re.compile(
    r"^\s*`?\[[✓→ ]\]\s*\d+(?:\.[ab]/\d+|\.)?\s+.*(?:→|->)"
)
HR_DIVIDER_RE = re.compile(r"^\s*---\s*$")
CURRENCY_AT_RE = re.compile(
    r"^\$(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[kKmMbBtT](?![A-Za-z0-9_]))?"
)


@dataclass(frozen=True)
class LintIssue:
    """Single lint diagnostic produced by lint_vault or lint_markdown_content."""

    level: str  # "ERROR" | "WARN"
    path: str
    line: int
    rule: str
    message: str

    def format(self) -> str:
        return f"{self.level} {self.path}:{self.line} [{self.rule}] {self.message}"


@dataclass
class _FrontmatterResult:
    has_frontmatter: bool
    closed: bool
    body_start_line: int  # 1-based line number where body begins
    fields: dict[str, str]
    field_lines: dict[str, int]
    aliases_values: list[tuple[int, str]]
    wikilinks: list[tuple[int, str]]
    field_values: dict[str, list[tuple[int, str]]] = field(default_factory=dict)
    field_wikilinks: dict[str, list[tuple[int, str]]] = field(default_factory=dict)
    heading_links: list[tuple[int, str | None, str]] = field(default_factory=list)
    placeholder_lines: list[tuple[int, str]] = field(default_factory=list)


def _extract_wikilink_parts(raw_inner: str) -> tuple[str | None, str | None]:
    """Extract (note_stem_or_None, heading_or_None) from [[Target#Heading|Alias]]."""
    parts = re.split(r"(?<!\\)\|", raw_inner, maxsplit=1)
    target_part = parts[0].replace("\\|", "|").strip()
    if target_part.startswith("#"):
        heading = target_part[1:].strip() or None
        return None, heading
    if "#" in target_part:
        target, _, heading_raw = target_part.partition("#")
        target = target.strip()
        if target.endswith(".md"):
            target = target[:-3].strip()
        heading = heading_raw.strip() or None
        return target or None, heading
    target = target_part
    if target.endswith(".md"):
        target = target[:-3].strip()
    return target, None


def _extract_wikilink_target(raw_inner: str) -> str | None:
    """Extract note stem from [[Target#Heading|Alias]], or None for same-note #Heading."""
    target, _ = _extract_wikilink_parts(raw_inner)
    return target


def _split_yaml_list_items(raw_val: str) -> list[str]:
    """Split a YAML inline list `[a, b]` or non-empty scalar into unquoted string items."""
    val = raw_val.strip()
    if not val:
        return []
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        items: list[str] = []
        buf: list[str] = []
        quote_char: str | None = None
        i = 0
        n = len(inner)
        while i < n:
            ch = inner[i]
            if quote_char is None:
                if ch in ('"', "'"):
                    quote_char = ch
                    buf.append(ch)
                elif ch == ",":
                    part = _unquote_yaml_scalar("".join(buf))
                    if part:
                        items.append(part)
                    buf = []
                else:
                    buf.append(ch)
                i += 1
            elif quote_char == '"':
                if ch == "\\" and i + 1 < n:
                    buf.extend((ch, inner[i + 1]))
                    i += 2
                    continue
                buf.append(ch)
                if ch == '"':
                    quote_char = None
                i += 1
            else:
                if ch == "'" and i + 1 < n and inner[i + 1] == "'":
                    buf.extend(("'", "'"))
                    i += 2
                    continue
                buf.append(ch)
                if ch == "'":
                    quote_char = None
                i += 1
        tail = _unquote_yaml_scalar("".join(buf))
        if tail:
            items.append(tail)
        return items
    scalar = _unquote_yaml_scalar(val)
    return [scalar] if scalar else []


def _strip_yaml_comment_with_quote_map(line: str) -> tuple[str, list[bool]]:
    """Return (non_comment_prefix, is_quoted_per_char) for a single YAML line."""
    quote_char: str | None = None
    chars: list[str] = []
    quoted: list[bool] = []
    i = 0
    n = len(line)

    while i < n:
        ch = line[i]
        if quote_char is None:
            if ch == "#" and (i == 0 or line[i - 1].isspace()):
                break
            if ch in ('"', "'"):
                quote_char = ch
                chars.append(ch)
                quoted.append(True)
                i += 1
                continue
            chars.append(ch)
            quoted.append(False)
            i += 1
        elif quote_char == '"':
            if ch == "\\" and i + 1 < n:
                chars.extend((ch, line[i + 1]))
                quoted.extend((True, True))
                i += 2
                continue
            chars.append(ch)
            quoted.append(True)
            if ch == '"':
                quote_char = None
            i += 1
        else:  # single quote
            if ch == "'" and i + 1 < n and line[i + 1] == "'":
                chars.extend(("'", "'"))
                quoted.extend((True, True))
                i += 2
                continue
            chars.append(ch)
            quoted.append(True)
            if ch == "'":
                quote_char = None
            i += 1

    return "".join(chars), quoted


def _unquote_yaml_scalar(raw_val: str) -> str:
    val = raw_val.strip()
    if len(val) >= 2 and (
        (val[0] == '"' and val[-1] == '"') or (val[0] == "'" and val[-1] == "'")
    ):
        return val[1:-1].strip()
    return val


def _parse_frontmatter(
    lines: list[str],
    *,
    path: str,
    require_frontmatter: bool,
    issues: list[LintIssue],
) -> _FrontmatterResult:
    empty_res = _FrontmatterResult(
        has_frontmatter=False,
        closed=True,
        body_start_line=1,
        fields={},
        field_lines={},
        aliases_values=[],
        wikilinks=[],
    )
    if not lines or lines[0].strip() != "---":
        if require_frontmatter:
            issues.append(
                LintIssue("ERROR", path, 1, "yaml-missing", "missing YAML frontmatter block")
            )
        return empty_res

    close_idx: int | None = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() in ("---", "..."):
            close_idx = idx
            break

    if close_idx is None:
        issues.append(
            LintIssue("ERROR", path, 1, "yaml-unclosed", "unclosed YAML frontmatter block")
        )
        return _FrontmatterResult(
            has_frontmatter=True,
            closed=False,
            body_start_line=len(lines) + 1,
            fields={},
            field_lines={},
            aliases_values=[],
            wikilinks=[],
        )

    fields: dict[str, str] = {}
    field_lines: dict[str, int] = {}
    aliases_values: list[tuple[int, str]] = []
    wikilinks: list[tuple[int, str]] = []
    field_values: dict[str, list[tuple[int, str]]] = {}
    field_wikilinks: dict[str, list[tuple[int, str]]] = {}
    heading_links: list[tuple[int, str | None, str]] = []
    placeholder_lines: list[tuple[int, str]] = []
    current_key: str | None = None

    for idx in range(1, close_idx):
        lineno = idx + 1
        raw_line = lines[idx]
        code_part, quoted_map = _strip_yaml_comment_with_quote_map(raw_line)
        stripped = code_part.strip()
        if not stripped:
            continue

        if TEMPLATE_PLACEHOLDER_RE.search(code_part):
            placeholder_lines.append((lineno, code_part))

        # Parse top-level key: value and indented/list continuations first so current_key is accurate.
        if not raw_line[0].isspace() and not stripped.startswith("-") and ":" in code_part:
            key, _, rest = code_part.partition(":")
            key = key.strip()
            if key in field_lines:
                issues.append(
                    LintIssue(
                        "ERROR",
                        path,
                        lineno,
                        "yaml-duplicate-key",
                        f"duplicate top-level YAML key '{key}' (first defined on line {field_lines[key]})",
                    )
                )
            current_key = key
            field_lines[key] = lineno
            val = rest.strip()
            fields[key] = _unquote_yaml_scalar(val)
            field_values.setdefault(key, [])
            field_wikilinks.setdefault(key, [])
            for item in _split_yaml_list_items(val):
                field_values[key].append((lineno, item))
            if key == "aliases" and val:
                aliases_values.append((lineno, val))
        elif current_key is not None:
            if current_key == "aliases" and stripped:
                aliases_values.append((lineno, stripped))
            if stripped.startswith("-"):
                item_raw = stripped[1:].strip()
                for item in _split_yaml_list_items(item_raw):
                    field_values.setdefault(current_key, []).append((lineno, item))
                if current_key in fields and not fields[current_key] and item_raw:
                    fields[current_key] = _unquote_yaml_scalar(item_raw)
            elif current_key in fields and not fields[current_key] and stripped:
                fields[current_key] = _unquote_yaml_scalar(stripped)
                for item in _split_yaml_list_items(stripped):
                    field_values.setdefault(current_key, []).append((lineno, item))

        # Check every [[...]] in YAML non-comment text is enclosed in quotes.
        for m in WIKILINK_RE.finditer(code_part):
            start, end = m.span()
            if not all(quoted_map[pos] for pos in range(start, end)):
                issues.append(
                    LintIssue(
                        "ERROR",
                        path,
                        lineno,
                        "yaml-unquoted-wikilink",
                        f"YAML wikilink [[{m.group(1)}]] must be enclosed in quotes",
                    )
                )
            if MATH_DOLLAR_RE.search(m.group(1)):
                issues.append(
                    LintIssue(
                        "ERROR",
                        path,
                        lineno,
                        "math-in-wikilink",
                        f"math delimiter $ must not appear inside [[{m.group(1)}]]",
                    )
                )
            target, heading = _extract_wikilink_parts(m.group(1))
            if heading is not None:
                heading_links.append((lineno, target, heading))
            if target is not None:
                wikilinks.append((lineno, target))
                if current_key is not None:
                    field_wikilinks.setdefault(current_key, []).append((lineno, target))

    # Disjoint YAML edge sets check across structural link fields.
    seen_edge_targets: dict[str, tuple[str, int]] = {}
    for edge_field in EDGE_FIELDS:
        for lineno, target in field_wikilinks.get(edge_field, []):
            if target in seen_edge_targets:
                prev_field, _ = seen_edge_targets[target]
                if prev_field != edge_field:
                    issues.append(
                        LintIssue(
                            "ERROR",
                            path,
                            lineno,
                            "yaml-overlapping-links",
                            (
                                f"wikilink [[{target}]] appears in both '{prev_field}' "
                                f"and '{edge_field}'; YAML edge sets must be disjoint"
                            ),
                        )
                    )
            else:
                seen_edge_targets[target] = (edge_field, lineno)

    # Required fields hygiene
    for req in REQUIRED_FRONTMATTER_FIELDS:
        if req not in fields:
            issues.append(
                LintIssue(
                    "ERROR",
                    path,
                    1,
                    "yaml-missing-field",
                    f"missing required YAML field '{req}'",
                )
            )
        elif not fields[req]:
            issues.append(
                LintIssue(
                    "ERROR",
                    path,
                    field_lines.get(req, 1),
                    "yaml-empty-field",
                    f"required YAML field '{req}' must not be empty",
                )
            )

    # Disallow $ in title and aliases
    if "title" in fields and MATH_DOLLAR_RE.search(fields["title"]):
        issues.append(
            LintIssue(
                "ERROR",
                path,
                field_lines.get("title", 1),
                "math-in-title",
                "YAML title must not contain math delimiter '$'",
            )
        )
    for lineno, alias_val in aliases_values:
        if MATH_DOLLAR_RE.search(alias_val):
            issues.append(
                LintIssue(
                    "ERROR",
                    path,
                    lineno,
                    "math-in-alias",
                    "YAML aliases must not contain math delimiter '$'",
                )
            )

    return _FrontmatterResult(
        has_frontmatter=True,
        closed=True,
        body_start_line=close_idx + 2,
        fields=fields,
        field_lines=field_lines,
        aliases_values=aliases_values,
        wikilinks=wikilinks,
        field_values=field_values,
        field_wikilinks=field_wikilinks,
        heading_links=heading_links,
        placeholder_lines=placeholder_lines,
    )


def _strip_blockquote_prefix(line: str) -> tuple[bool, str]:
    """Return (is_blockquote_line, line_without_leading_blockquote_markers)."""
    m = BLOCKQUOTE_PREFIX_RE.match(line)
    if not m:
        return False, line
    return True, line[m.end() :]


def _is_currency_dollar(line: str, open_idx: int) -> bool:
    """Return True if '$' at open_idx begins a standalone currency amount (e.g. $10, $10.50)."""
    m = CURRENCY_AT_RE.match(line[open_idx:])
    if not m:
        return False
    after = open_idx + len(m.group(0))
    if after == len(line):
        return True
    nxt = line[after]
    if nxt == "$":
        return False
    if nxt == "-" and re.match(r"-\s*\$?\d", line[after:]):
        return True
    if nxt in ",.;:!?)]—–，。；：、）%元块刀美":
        return True
    if nxt.isspace():
        rest = line[after:].lstrip()
        if not rest:
            return True
        if rest[0] in "+-*/=<>^_\\":
            # Looks like arithmetic starting with a number (e.g. "$10 + 2$") only if closed cleanly.
            return _find_closing_inline_dollar(line, open_idx) is None
        return True
    if nxt == "/":
        # Currency rate like "$10/mo" vs math fraction "$10/2$"
        tail = line[after + 1 :]
        if tail and tail[0].isalpha() and "$" not in tail:
            return True
        return _find_closing_inline_dollar(line, open_idx) is None
    return False


def _find_closing_inline_dollar(line: str, open_idx: int) -> int | None:
    """Find matching unescaped single '$' on the same line, skipping currency like '$10 to $20'."""
    n = len(line)
    j = open_idx + 1
    while j < n:
        if line[j] == "\\":
            j += 2
            continue
        if line[j : j + 2] == "$$":
            # Display math opener inside an unclosed inline $: abort inline pairing.
            return None
        if line[j] == "$":
            if _is_currency_dollar(line, j):
                j += 1
                continue
            prev_ch = line[j - 1]
            next_ch = line[j + 1] if j + 1 < n else ""
            # Currency heuristic: in '$10 to $20', second '$' follows space and precedes a digit.
            if prev_ch.isspace() and next_ch.isdigit():
                j += 1
                continue
            return j
        j += 1
    return None


def _find_closing_double_dollar(line: str, start_idx: int) -> int | None:
    """Find next unescaped '$$' on the same line starting from start_idx."""
    n = len(line)
    j = start_idx
    while j < n:
        if line[j] == "\\":
            j += 2
            continue
        if line[j : j + 2] == "$$":
            return j
        j += 1
    return None


def _check_math_segment(
    segment: str,
    *,
    is_display: bool,
    path: str,
    lineno: int,
    issues: list[LintIssue],
) -> None:
    if not is_display and segment and (segment[0].isspace() or segment[-1].isspace()):
        issues.append(
            LintIssue(
                "ERROR",
                path,
                lineno,
                "math-inline-space",
                "inline $...$ must not have leading or trailing spaces",
            )
        )
    for m in WIKILINK_RE.finditer(segment):
        issues.append(
            LintIssue(
                "ERROR",
                path,
                lineno,
                "wikilink-in-math",
                f"wikilink [[{m.group(1)}]] must not appear inside math delimiters",
            )
        )
    if not is_display and IMPLIES_RE.search(segment):
        issues.append(
            LintIssue(
                "ERROR",
                path,
                lineno,
                "prose-implies",
                "\\implies must not appear in inline $...$; use ⟹ in prose or move to $$...$$",
            )
        )


def _normalize_heading_variants(raw_heading: str) -> set[str]:
    """Return normalized Obsidian heading candidates for raw ATX heading text."""
    cleaned = re.sub(r"<!--.*?-->", "", raw_heading).strip()
    v1 = re.sub(r"\s+", " ", cleaned)
    stripped = re.sub(r"\[\[[^\[\]|\n]+\|([^\[\]\n]+)\]\]", r"\1", cleaned)
    stripped = re.sub(r"\[\[([^\[\]\n]+)\]\]", r"\1", stripped)
    stripped = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)
    stripped = stripped.replace("`", "").replace("**", "").replace("__", "")
    v2 = re.sub(r"\s+", " ", stripped.strip())
    return {v for v in (v1, v2) if v}


def _scan_body(
    lines: list[str],
    *,
    start_line: int,
    path: str,
    issues: list[LintIssue],
    headings_out: set[str] | None = None,
    heading_links_out: list[tuple[int, str | None, str]] | None = None,
    prose_lines_out: list[tuple[int, str]] | None = None,
    callouts_out: list[tuple[int, str]] | None = None,
    check_body_hr: bool = False,
) -> list[tuple[int, str]]:
    """Scan Markdown body for MathJax/wikilink violations and extract body wikilinks."""
    body_wikilinks: list[tuple[int, str]] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    fence_in_blockquote = False
    fence_start_line = 0
    in_html_comment = False
    in_display_math = False
    display_math_start_line = 0
    display_math_in_blockquote = False

    for idx in range(start_line - 1, len(lines)):
        lineno = idx + 1
        raw_line = lines[idx]
        is_bq, line = _strip_blockquote_prefix(raw_line)

        # Leaving a blockquote closes/flags open blockquote-scoped fences or display math.
        if not is_bq and in_fence and fence_in_blockquote:
            issues.append(
                LintIssue(
                    "ERROR",
                    path,
                    fence_start_line,
                    "fence-unclosed",
                    "unclosed fenced code block inside blockquote",
                )
            )
            in_fence = False
            fence_in_blockquote = False
        if not is_bq and in_display_math and display_math_in_blockquote:
            issues.append(
                LintIssue(
                    "ERROR",
                    path,
                    display_math_start_line,
                    "math-unclosed",
                    "unclosed $$ display math block inside blockquote",
                )
            )
            in_display_math = False
            display_math_in_blockquote = False

        # 1. Fenced code blocks (handles both top-level and blockquote/callout prefixes)
        if in_fence:
            close_pat = re.compile(rf"^\s*{re.escape(fence_char)}{{{fence_len},}}\s*$")
            if close_pat.match(line):
                in_fence = False
                fence_in_blockquote = False
            continue

        progress_bar_hit = False
        if not in_display_math and not in_html_comment:
            m_fence = FENCE_RE.match(line)
            if m_fence:
                fence_str = m_fence.group(1)
                f_char = fence_str[0]
                info_after = line[m_fence.end() :]
                # CommonMark: backtick fence info strings cannot contain '`'; treat ```inline``` as inline code.
                if not (f_char == "`" and "`" in info_after):
                    fence_char = f_char
                    fence_len = len(fence_str)
                    in_fence = True
                    fence_in_blockquote = is_bq
                    fence_start_line = lineno
                    continue
            if not line.lstrip().startswith("<!--"):
                if headings_out is not None:
                    m_head = HEADING_RE.match(line)
                    if m_head:
                        headings_out.update(_normalize_heading_variants(m_head.group(1)))
                if is_bq and callouts_out is not None:
                    m_callout = SKIM_CALLOUT_RE.match(line)
                    if m_callout:
                        callouts_out.append((lineno, m_callout.group(1).lower()))
                progress_bar_hit = bool(CHAT_PROGRESS_LINE_RE.match(line))
                if check_body_hr and not is_bq and HR_DIVIDER_RE.match(line):
                    issues.append(
                        LintIssue(
                            "WARN",
                            path,
                            lineno,
                            "body-hr-divider",
                            "horizontal rule '---' should not appear in note body; keep continuous narrative prose without chat dividers",
                        )
                    )

        # Tokenize line into ("BOLD",) or ("MATH",) for bold-wrapping check.
        tokens: list[str] = []
        prose_chars: list[str] = []
        i = 0
        n = len(line)

        while i < n:
            if in_html_comment:
                end_comment = line.find("-->", i)
                if end_comment == -1:
                    i = n
                else:
                    in_html_comment = False
                    i = end_comment + 3
                continue

            if in_display_math:
                end_dd = _find_closing_double_dollar(line, i)
                if end_dd is None:
                    _check_math_segment(
                        line[i:], is_display=True, path=path, lineno=lineno, issues=issues
                    )
                    i = n
                else:
                    _check_math_segment(
                        line[i:end_dd], is_display=True, path=path, lineno=lineno, issues=issues
                    )
                    in_display_math = False
                    tokens.append("MATH")
                    i = end_dd + 2
                continue

            # Outside comments and display math
            if line.startswith("<!--", i):
                in_html_comment = True
                i += 4
                continue

            # Backslash escape outside math/code: check prose \implies before skipping
            if line[i] == "\\":
                if IMPLIES_RE.match(line, i):
                    issues.append(
                        LintIssue(
                            "ERROR",
                            path,
                            lineno,
                            "prose-implies",
                            "\\implies must not be used in prose outside $$...$$; use Unicode ⟹",
                        )
                    )
                    i += len("\\implies")
                    continue
                i += 2 if i + 1 < n else 1
                continue

            # Inline code span
            if line[i] == "`":
                k = 0
                while i + k < n and line[i + k] == "`":
                    k += 1
                # Find matching closing backtick run of exact length k
                search_pos = i + k
                matched_close = -1
                while search_pos < n:
                    if line[search_pos] == "`":
                        run = 0
                        while search_pos + run < n and line[search_pos + run] == "`":
                            run += 1
                        if run == k:
                            matched_close = search_pos
                            break
                        search_pos += run
                    else:
                        search_pos += 1
                if matched_close != -1:
                    i = matched_close + k
                else:
                    i += k
                continue

            # Display math $$...$$
            if line[i : i + 2] == "$$":
                end_dd = _find_closing_double_dollar(line, i + 2)
                if end_dd is None:
                    _check_math_segment(
                        line[i + 2 :], is_display=True, path=path, lineno=lineno, issues=issues
                    )
                    in_display_math = True
                    display_math_start_line = lineno
                    display_math_in_blockquote = is_bq
                    tokens.append("MATH")
                    i = n
                else:
                    _check_math_segment(
                        line[i + 2 : end_dd],
                        is_display=True,
                        path=path,
                        lineno=lineno,
                        issues=issues,
                    )
                    tokens.append("MATH")
                    i = end_dd + 2
                continue

            # Inline math $...$ (skipping standalone currency tokens such as $10)
            if line[i] == "$":
                if _is_currency_dollar(line, i):
                    m_curr = CURRENCY_AT_RE.match(line[i:])
                    end_curr = i + (len(m_curr.group(0)) if m_curr else 1)
                    prose_chars.append(line[i:end_curr])
                    i = end_curr
                    continue
                close_d = _find_closing_inline_dollar(line, i)
                if close_d is not None:
                    segment = line[i + 1 : close_d]
                    _check_math_segment(
                        segment, is_display=False, path=path, lineno=lineno, issues=issues
                    )
                    tokens.append("MATH")
                    i = close_d + 1
                    continue
                issues.append(
                    LintIssue(
                        "ERROR",
                        path,
                        lineno,
                        "math-unclosed",
                        "unclosed inline '$' math delimiter",
                    )
                )
                prose_chars.append(line[i])
                i += 1
                continue

            # Bold marker **
            if line[i : i + 2] == "**":
                tokens.append("BOLD")
                i += 2
                continue

            # Wikilink [[...]]
            if line[i : i + 2] == "[[":
                m_wl = WIKILINK_RE.match(line, i)
                if m_wl:
                    raw_inner = m_wl.group(1)
                    if MATH_DOLLAR_RE.search(raw_inner):
                        issues.append(
                            LintIssue(
                                "ERROR",
                                path,
                                lineno,
                                "math-in-wikilink",
                                f"math delimiter $ must not appear inside [[{raw_inner}]]",
                            )
                        )
                    target, heading = _extract_wikilink_parts(raw_inner)
                    if target is not None:
                        body_wikilinks.append((lineno, target))
                    if heading is not None and heading_links_out is not None:
                        heading_links_out.append((lineno, target, heading))
                    i = m_wl.end()
                    continue

            prose_chars.append(line[i])
            i += 1

        plain_prose = "".join(prose_chars)
        if prose_lines_out is not None and prose_chars:
            prose_lines_out.append((lineno, plain_prose))
        if (
            progress_bar_hit
            or CHAT_SCAFFOLD_PROSE_RE.search(plain_prose)
            or (is_bq and CHAT_PROMPT_BQ_RE.match(plain_prose))
        ):
            issues.append(
                LintIssue(
                    "ERROR",
                    path,
                    lineno,
                    "leaked-chat-scaffold",
                    "chat-only teaching scaffold (progress pill, prompt box, file:// link, or <agent-embed>) must not appear in vault files",
                )
            )

        # Check bold markers wrapping math on this line by pairing BOLD tokens left-to-right.
        bold_indices = [pos for pos, tok in enumerate(tokens) if tok == "BOLD"]
        for pair_idx in range(0, len(bold_indices) - 1, 2):
            b_start = bold_indices[pair_idx]
            b_end = bold_indices[pair_idx + 1]
            if any(tok == "MATH" for tok in tokens[b_start + 1 : b_end]):
                issues.append(
                    LintIssue(
                        "ERROR",
                        path,
                        lineno,
                        "math-in-bold",
                        "do not wrap $...$ math inside **...** bold markers",
                    )
                )

    if in_display_math:
        issues.append(
            LintIssue(
                "ERROR",
                path,
                display_math_start_line,
                "math-unclosed",
                "unclosed $$ display math block",
            )
        )
    if in_fence:
        issues.append(
            LintIssue("ERROR", path, fence_start_line or len(lines), "fence-unclosed", "unclosed fenced code block")
        )

    return body_wikilinks


def lint_markdown_content(
    content: str,
    *,
    path: str = "<memory>",
    known_notes: set[str] | None = None,
    require_frontmatter: bool = False,
) -> list[LintIssue]:
    """Lint a single Markdown string for YAML, wikilink, and MathJax x [[wikilink]] rules.

    If `known_notes` is provided, verifies all extracted wikilinks resolve to a note stem
    in `known_notes`.
    """
    issues: list[LintIssue] = []
    lines = content.splitlines()

    fm = _parse_frontmatter(
        lines,
        path=path,
        require_frontmatter=require_frontmatter,
        issues=issues,
    )
    body_wikilinks = _scan_body(
        lines,
        start_line=fm.body_start_line,
        path=path,
        issues=issues,
        check_body_hr=require_frontmatter,
    )

    if known_notes is not None:
        all_links = fm.wikilinks + body_wikilinks
        for lineno, target in all_links:
            if target not in known_notes:
                issues.append(
                    LintIssue(
                        "ERROR",
                        path,
                        lineno,
                        "dead-wikilink",
                        f"dangling wikilink [[{target}]] has no matching file notes/{target}.md",
                    )
                )

    return issues


def _collect_wikilinks_from_note(content: str) -> tuple[_FrontmatterResult, list[tuple[int, str]]]:
    """Parse frontmatter and body wikilinks without emitting duplicate issues."""
    dummy: list[LintIssue] = []
    lines = content.splitlines()
    fm = _parse_frontmatter(lines, path="<scan>", require_frontmatter=False, issues=dummy)
    body_links = _scan_body(lines, start_line=fm.body_start_line, path="<scan>", issues=dummy)
    return fm, fm.wikilinks + body_links


def _collect_note_details(
    content: str,
    *,
    callouts_out: list[tuple[int, str]] | None = None,
) -> tuple[
    _FrontmatterResult,
    list[tuple[int, str]],
    set[str],
    list[tuple[int, str | None, str]],
    list[tuple[int, str]],
]:
    """Extract frontmatter, wikilinks, headings, #heading links, and non-code prose lines."""
    dummy: list[LintIssue] = []
    lines = content.splitlines()
    fm = _parse_frontmatter(lines, path="<scan>", require_frontmatter=False, issues=dummy)
    headings: set[str] = set()
    body_heading_links: list[tuple[int, str | None, str]] = []
    prose_lines: list[tuple[int, str]] = []
    body_links = _scan_body(
        lines,
        start_line=fm.body_start_line,
        path="<scan>",
        issues=dummy,
        headings_out=headings,
        heading_links_out=body_heading_links,
        prose_lines_out=prose_lines,
        callouts_out=callouts_out,
    )
    return fm, fm.wikilinks + body_links, headings, fm.heading_links + body_heading_links, prose_lines


def _strip_inline_code_and_comments(line: str, in_comment: bool) -> tuple[str, bool]:
    """Return (non-comment, non-inline-code text, next_in_comment) for index.md parsing."""
    out: list[str] = []
    i = 0
    n = len(line)
    while i < n:
        if in_comment:
            end_c = line.find("-->", i)
            if end_c == -1:
                return "".join(out), True
            in_comment = False
            i = end_c + 3
            continue
        if line.startswith("<!--", i):
            in_comment = True
            i += 4
            continue
        if line[i] == "`":
            k = 0
            while i + k < n and line[i + k] == "`":
                k += 1
            search_pos = i + k
            matched_close = -1
            while search_pos < n:
                if line[search_pos] == "`":
                    run = 0
                    while search_pos + run < n and line[search_pos + run] == "`":
                        run += 1
                    if run == k:
                        matched_close = search_pos
                        break
                    search_pos += run
                else:
                    search_pos += 1
            if matched_close != -1:
                i = matched_close + k
            else:
                i += k
            continue
        out.append(line[i])
        i += 1
    return "".join(out), False


def _classify_index_h2_section(h2_title: str) -> str | None:
    """Classify top-level index.md H2 heading into concept|paper|synthesis|backlog or None."""
    low = h2_title.lower()
    if "待沉淀支线" in h2_title or "backlog" in low:
        return "backlog"
    if "概念" in h2_title or "concepts" in low:
        return "concept"
    if "论文" in h2_title or "papers" in low:
        return "paper"
    if "专题" in h2_title or "synthes" in low:
        return "synthesis"
    return None


def _scan_index_catalog(
    index_text: str,
    start_line: int,
) -> tuple[
    set[str],
    dict[str, list[tuple[int, str]]],
    dict[str, list[tuple[int, str]]],
    dict[str, list[tuple[int, str | None]]],
]:
    """Scan index.md outside Backlog for catalog targets, entry bullets, target lines, and entry sections."""
    lines = index_text.splitlines()
    catalog_targets: set[str] = set()
    catalog_entry_lines: dict[str, list[tuple[int, str]]] = {}
    catalog_target_lines: dict[str, list[tuple[int, str]]] = {}
    catalog_entry_sections: dict[str, list[tuple[int, str | None]]] = {}

    in_fence = False
    fence_char = ""
    fence_len = 0
    in_comment = False
    current_section: str | None = None

    for idx in range(start_line - 1, len(lines)):
        lineno = idx + 1
        raw_line = lines[idx]

        if in_fence:
            close_pat = re.compile(rf"^\s*{re.escape(fence_char)}{{{fence_len},}}\s*$")
            if close_pat.match(raw_line):
                in_fence = False
            continue

        if not in_comment:
            m_fence = FENCE_RE.match(raw_line)
            if m_fence:
                fence_str = m_fence.group(1)
                if not (fence_str[0] == "`" and "`" in raw_line[m_fence.end() :]):
                    fence_char = fence_str[0]
                    fence_len = len(fence_str)
                    in_fence = True
                    continue

        clean_line, in_comment = _strip_inline_code_and_comments(raw_line, in_comment)
        if not clean_line.strip():
            continue

        m_h2 = TOP_H2_RE.match(clean_line)
        if m_h2:
            current_section = _classify_index_h2_section(m_h2.group(1))
            continue

        if current_section == "backlog":
            continue

        m_entry = CATALOG_ENTRY_RE.match(clean_line)
        if m_entry:
            entry_target = _extract_wikilink_target(m_entry.group(1))
            if entry_target is not None:
                catalog_entry_lines.setdefault(entry_target, []).append((lineno, clean_line))
                catalog_entry_sections.setdefault(entry_target, []).append((lineno, current_section))

        for m in WIKILINK_RE.finditer(clean_line):
            target = _extract_wikilink_target(m.group(1))
            if target is not None:
                catalog_targets.add(target)
                catalog_target_lines.setdefault(target, []).append((lineno, clean_line))

    return catalog_targets, catalog_entry_lines, catalog_target_lines, catalog_entry_sections


def lint_vault(root: Path | str) -> list[LintIssue]:
    """Run all vault integrity, sync, archive, and formatting checks on `root`."""
    vault_root = Path(root).resolve()
    issues: list[LintIssue] = []

    index_path = vault_root / "index.md"
    notes_dir = vault_root / "notes"

    if not notes_dir.is_dir():
        issues.append(
            LintIssue("ERROR", "notes", 1, "vault-structure", "notes/ directory does not exist")
        )
        return issues

    note_files = sorted(notes_dir.glob("*.md"), key=lambda p: p.name)
    known_notes = {p.stem for p in note_files}

    # Check note filenames themselves don't contain '$'
    for note_path in note_files:
        if "$" in note_path.stem:
            issues.append(
                LintIssue(
                    "ERROR",
                    f"notes/{note_path.name}",
                    1,
                    "math-in-filename",
                    "note filename must not contain '$'",
                )
            )

    # 1. Lint index.md and scan catalog (exempting Backlog from coverage & duplicate checks)
    has_index = index_path.is_file()
    index_headings: set[str] = set()
    index_heading_links: list[tuple[int, str | None, str]] = []
    catalog_targets: set[str] = set()
    catalog_entry_lines: dict[str, list[tuple[int, str]]] = {}
    catalog_target_lines: dict[str, list[tuple[int, str]]] = {}
    catalog_entry_sections: dict[str, list[tuple[int, str | None]]] = {}

    if not has_index:
        issues.append(
            LintIssue("ERROR", "index.md", 1, "vault-structure", "index.md does not exist")
        )
    else:
        index_text = index_path.read_text(encoding="utf-8")
        issues.extend(
            lint_markdown_content(
                index_text,
                path="index.md",
                known_notes=known_notes,
                require_frontmatter=False,
            )
        )
        idx_fm, _, index_headings, index_heading_links, _ = _collect_note_details(index_text)
        (
            catalog_targets,
            catalog_entry_lines,
            catalog_target_lines,
            catalog_entry_sections,
        ) = _scan_index_catalog(index_text, idx_fm.body_start_line)

        for stem in sorted(known_notes):
            if stem not in catalog_entry_lines:
                issues.append(
                    LintIssue(
                        "ERROR",
                        "index.md",
                        1,
                        "index-missing-note",
                        f"notes/{stem}.md must have its own bullet catalog entry in index.md",
                    )
                )

        for target, entries in sorted(catalog_entry_lines.items()):
            if target in known_notes and len(entries) > 1:
                for dup_line, _ in entries[1:]:
                    issues.append(
                        LintIssue(
                            "WARN",
                            "index.md",
                            dup_line,
                            "index-duplicate-entry",
                            f"[[{target}]] appears multiple times as a catalog entry in index.md",
                        )
                    )

    # 2. Lint every note in notes/*.md and validate concrete note hygiene + archives
    notes_fm: dict[str, _FrontmatterResult] = {}
    notes_headings: dict[str, set[str]] = {}
    all_heading_checks: list[tuple[str, str | None, list[tuple[int, str | None, str]]]] = []
    if has_index:
        all_heading_checks.append(("index.md", None, index_heading_links))

    referenced_raw: set[Path] = set()

    for note_path in note_files:
        stem = note_path.stem
        rel_path = f"notes/{note_path.name}"
        text = note_path.read_text(encoding="utf-8")
        issues.extend(
            lint_markdown_content(
                text,
                path=rel_path,
                known_notes=known_notes,
                require_frontmatter=True,
            )
        )
        callouts: list[tuple[int, str]] = []
        fm, links, headings, heading_links, prose_lines = _collect_note_details(
            text, callouts_out=callouts
        )
        notes_fm[stem] = fm
        notes_headings[stem] = headings
        all_heading_checks.append((rel_path, stem, heading_links))

        # Concrete-note YAML enum, date, and tag checks
        if fm.has_frontmatter and fm.closed:
            note_type = fm.fields.get("type", "").strip()
            note_status = fm.fields.get("status", "").strip()
            if note_type:
                if note_type not in VALID_TYPES:
                    issues.append(
                        LintIssue(
                            "ERROR",
                            rel_path,
                            fm.field_lines.get("type", 1),
                            "yaml-invalid-enum",
                            f"invalid YAML type '{note_type}'; expected one of {', '.join(VALID_TYPES)}",
                        )
                    )
                elif note_status and note_status not in VALID_STATUS_BY_TYPE[note_type]:
                    allowed = ", ".join(VALID_STATUS_BY_TYPE[note_type])
                    issues.append(
                        LintIssue(
                            "ERROR",
                            rel_path,
                            fm.field_lines.get("status", 1),
                            "yaml-invalid-enum",
                            f"invalid status '{note_status}' for type '{note_type}'; expected one of {allowed}",
                        )
                    )

            for date_key in ("created", "updated"):
                date_val = fm.fields.get(date_key, "").strip()
                if date_val:
                    is_valid_date = False
                    if DATE_RE.match(date_val):
                        try:
                            date.fromisoformat(date_val)
                            is_valid_date = True
                        except ValueError:
                            is_valid_date = False
                    if not is_valid_date:
                        issues.append(
                            LintIssue(
                                "ERROR",
                                rel_path,
                                fm.field_lines.get(date_key, 1),
                                "yaml-invalid-date",
                                f"YAML field '{date_key}' value '{date_val}' is not a valid YYYY-MM-DD date",
                            )
                        )

            tag_items = fm.field_values.get("tags", [])
            tag_line = fm.field_lines.get("tags", 1)
            if not tag_items:
                issues.append(
                    LintIssue(
                        "ERROR",
                        rel_path,
                        tag_line,
                        "yaml-empty-tags",
                        "YAML 'tags' must not be empty",
                    )
                )
            else:
                if len(tag_items) > 3:
                    issues.append(
                        LintIssue(
                            "WARN",
                            rel_path,
                            tag_line,
                            "yaml-tag-hygiene",
                            f"YAML 'tags' should contain at most 3 tags (found {len(tag_items)})",
                        )
                    )
                for t_line, tag_val in tag_items:
                    if not KEBAB_TAG_RE.match(tag_val):
                        issues.append(
                            LintIssue(
                                "WARN",
                                rel_path,
                                t_line,
                                "yaml-tag-hygiene",
                                f"tag '{tag_val}' should use lowercase kebab-case",
                            )
                        )

            if note_type in ("paper", "synthesis"):
                edge_count = sum(len(fm.field_wikilinks.get(f, [])) for f in EDGE_FIELDS)
                if edge_count == 0:
                    issues.append(
                        LintIssue(
                            "WARN",
                            rel_path,
                            fm.field_lines.get("type", 1),
                            "empty-links",
                            f"{note_type} note has no YAML links in prerequisites, concepts, sources, or related",
                        )
                    )

            if note_status == "skim":
                has_question_callout = False
                for callout_line, callout_kind in callouts:
                    if callout_kind == "tip":
                        issues.append(
                            LintIssue(
                                "WARN",
                                rel_path,
                                callout_line,
                                "skim-callout-mismatch",
                                "status: skim note must not use > [!tip]; replace with > [!question]",
                            )
                        )
                    elif callout_kind == "question":
                        has_question_callout = True
                if not has_question_callout:
                    issues.append(
                        LintIssue(
                            "WARN",
                            rel_path,
                            fm.field_lines.get("status", 1),
                            "skim-callout-mismatch",
                            "status: skim note must include a > [!question] callout",
                        )
                    )

        # Unfilled template placeholders & leaked pedagogy tags
        for lineno, _ in fm.placeholder_lines:
            issues.append(
                LintIssue(
                    "ERROR",
                    rel_path,
                    lineno,
                    "unfilled-placeholder",
                    "unfilled template placeholder {{...}} in YAML frontmatter",
                )
            )
        for lineno, plain_line in prose_lines:
            if TEMPLATE_PLACEHOLDER_RE.search(plain_line) or "……" in plain_line:
                issues.append(
                    LintIssue(
                        "ERROR",
                        rel_path,
                        lineno,
                        "unfilled-placeholder",
                        "unfilled template placeholder ({{...}} or ……) left in note body",
                    )
                )
            m_ped = PEDAGOGY_TAG_RE.search(plain_line)
            if m_ped:
                issues.append(
                    LintIssue(
                        "ERROR",
                        rel_path,
                        lineno,
                        "leaked-pedagogy-tag",
                        f"pedagogy tag [{m_ped.group(1)}] must not appear in compiled notes",
                    )
                )

        # Self-wikilink check (ignore [[Stem#Heading]] section links; warn on bare [[Stem]])
        heading_target_lines = {(ln, tgt) for ln, tgt, _ in heading_links if tgt is not None}
        for lineno, target in links:
            if target == stem and (lineno, target) not in heading_target_lines:
                issues.append(
                    LintIssue(
                        "WARN",
                        rel_path,
                        lineno,
                        "self-wikilink",
                        f"note contains self-referential wikilink [[{stem}]]",
                    )
                )

        # Index section & status badge sync for concrete notes
        if has_index and fm.has_frontmatter and fm.closed:
            note_type_idx = fm.fields.get("type", "").strip()
            note_status_idx = fm.fields.get("status", "").strip()
            if note_type_idx in VALID_TYPES:
                for sec_line, sec_kind in catalog_entry_sections.get(stem, []):
                    if sec_kind is not None and sec_kind != note_type_idx:
                        issues.append(
                            LintIssue(
                                "ERROR",
                                "index.md",
                                sec_line,
                                "index-section-mismatch",
                                f"[[{stem}]] has type '{note_type_idx}' but is cataloged under '{sec_kind}' section in index.md",
                            )
                        )
            if note_type_idx in ("concept", "synthesis") and note_status_idx in VALID_STATUS_BY_TYPE.get(
                note_type_idx, ()
            ):
                entry_lines_cs = catalog_entry_lines.get(stem, [])
                if entry_lines_cs:
                    required_badge = (
                        "[skim]"
                        if note_status_idx == "skim"
                        else "[superseded]"
                        if note_status_idx == "superseded"
                        else None
                    )
                    for badge in ("[skim]", "[superseded]"):
                        has_badge = any(badge in txt for _, txt in entry_lines_cs)
                        if badge == required_badge and not has_badge:
                            issues.append(
                                LintIssue(
                                    "ERROR",
                                    "index.md",
                                    entry_lines_cs[0][0],
                                    "index-status-mismatch",
                                    f"index.md entry for {note_status_idx} note [[{stem}]] must include {badge}",
                                )
                            )
                        elif badge != required_badge and has_badge:
                            issues.append(
                                LintIssue(
                                    "ERROR",
                                    "index.md",
                                    entry_lines_cs[0][0],
                                    "index-status-mismatch",
                                    f"index.md entry for {note_status_idx} note [[{stem}]] must not carry {badge}",
                                )
                            )

        # Archive check + index status sync for type: paper notes
        if fm.fields.get("type") == "paper":
            if "source" not in fm.fields:
                issues.append(
                    LintIssue(
                        "ERROR",
                        rel_path,
                        fm.field_lines.get("type", 1),
                        "yaml-missing-field",
                        "paper note missing required YAML field 'source'",
                    )
                )
            else:
                source_val = fm.fields.get("source", "").strip()
                src_line = fm.field_lines.get("source", 1)
                if not source_val:
                    issues.append(
                        LintIssue(
                            "ERROR",
                            rel_path,
                            src_line,
                            "yaml-empty-field",
                            "paper YAML field 'source' must not be empty",
                        )
                    )
                elif source_val.startswith(".raw/"):
                    raw_file = vault_root / source_val
                    referenced_raw.add(raw_file.resolve())
                    if not raw_file.is_file():
                        issues.append(
                            LintIssue(
                                "ERROR",
                                rel_path,
                                src_line,
                                "archive-missing",
                                f"paper source '{source_val}' does not exist",
                            )
                        )
                    inbox_dup = vault_root / "inbox" / Path(source_val).name
                    if inbox_dup.exists():
                        issues.append(
                            LintIssue(
                                "ERROR",
                                rel_path,
                                src_line,
                                "archive-duplicate-in-inbox",
                                f"archived paper '{Path(source_val).name}' still exists in inbox/",
                            )
                        )
                elif source_val.startswith("inbox/"):
                    issues.append(
                        LintIssue(
                            "WARN",
                            rel_path,
                            src_line,
                            "archive-pending",
                            f"paper source '{source_val}' is still in inbox/; move to .raw/ when done",
                        )
                    )
                elif not source_val.startswith(("http://", "https://")):
                    issues.append(
                        LintIssue(
                            "ERROR",
                            rel_path,
                            src_line,
                            "paper-invalid-source",
                            f"paper source '{source_val}' must point to '.raw/...', 'inbox/...', or a URL",
                        )
                    )

            paper_status = fm.fields.get("status", "").strip()
            if has_index and paper_status in VALID_STATUS_BY_TYPE["paper"]:
                entry_lines = catalog_entry_lines.get(stem) or catalog_target_lines.get(stem, [])
                if entry_lines and not any(f"[{paper_status}]" in txt for _, txt in entry_lines):
                    issues.append(
                        LintIssue(
                            "ERROR",
                            "index.md",
                            entry_lines[0][0],
                            "index-paper-status-mismatch",
                            f"index.md entry for paper [[{stem}]] must match YAML status [{paper_status}]",
                        )
                    )

    # 3. Validate #Heading fragments in [[Target#Heading]] and [[#Heading]]
    for rel_path, owner_stem, heading_links in all_heading_checks:
        for lineno, target, heading in heading_links:
            if heading.startswith("^"):
                continue
            resolved_stem = target if target is not None else owner_stem
            if resolved_stem is None:
                target_headings = index_headings
                target_file = "index.md"
            elif resolved_stem in notes_headings:
                target_headings = notes_headings[resolved_stem]
                target_file = f"notes/{resolved_stem}.md"
            else:
                continue
            norm_h = re.sub(r"\s+", " ", heading.strip())
            sub_h = (
                re.sub(r"\s+", " ", heading.rsplit("#", 1)[-1].strip())
                if "#" in heading
                else norm_h
            )
            if norm_h not in target_headings and sub_h not in target_headings:
                issues.append(
                    LintIssue(
                        "ERROR",
                        rel_path,
                        lineno,
                        "dead-heading-link",
                        f"heading '#{heading}' does not exist in {target_file}",
                    )
                )

    # 4. Scoped structural link symmetry (WARN):
    #    - related <-> related
    #    - paper.concepts <-> concept.sources/related
    #    - synthesis.sources <-> target.related
    #    (prerequisites, concept.sources -> paper, and prose links are exempt)
    for src in sorted(notes_fm):
        src_fm = notes_fm[src]
        src_type = src_fm.fields.get("type", "").strip()
        src_rel_path = f"notes/{src}.md"

        seen_rel: set[str] = set()
        for lineno, dst in src_fm.field_wikilinks.get("related", []):
            if dst == src or dst not in notes_fm or dst in seen_rel:
                continue
            seen_rel.add(dst)
            dst_fm = notes_fm[dst]
            # Accept any YAML structural back-edge (prerequisites/concepts/sources/related)
            # so disjoint-edge rules never conflict with reciprocity checks.
            dst_back = {t for f in EDGE_FIELDS for _, t in dst_fm.field_wikilinks.get(f, [])}
            if src not in dst_back:
                issues.append(
                    LintIssue(
                        "WARN",
                        src_rel_path,
                        lineno,
                        "asymmetric-link",
                        f"[[{src}]] lists [[{dst}]] in YAML 'related', but [[{dst}]] does not link back symmetrically",
                    )
                )

        if src_type == "paper":
            seen_concepts: set[str] = set()
            for lineno, dst in src_fm.field_wikilinks.get("concepts", []):
                if dst == src or dst not in notes_fm or dst in seen_concepts:
                    continue
                seen_concepts.add(dst)
                dst_fm = notes_fm[dst]
                dst_back = {
                    t for f in ("sources", "related") for _, t in dst_fm.field_wikilinks.get(f, [])
                }
                if src not in dst_back:
                    issues.append(
                        LintIssue(
                            "WARN",
                            src_rel_path,
                            lineno,
                            "asymmetric-link",
                            f"paper [[{src}]] lists [[{dst}]] in 'concepts', but [[{dst}]] does not list [[{src}]] in 'sources' or 'related'",
                        )
                    )

        if src_type == "synthesis":
            seen_sources: set[str] = set()
            for lineno, dst in src_fm.field_wikilinks.get("sources", []):
                if dst == src or dst not in notes_fm or dst in seen_sources:
                    continue
                seen_sources.add(dst)
                dst_related = {t for _, t in notes_fm[dst].field_wikilinks.get("related", [])}
                if src not in dst_related:
                    issues.append(
                        LintIssue(
                            "WARN",
                            src_rel_path,
                            lineno,
                            "asymmetric-link",
                            f"synthesis [[{src}]] cites [[{dst}]] in 'sources', but [[{dst}]] does not list [[{src}]] in 'related'",
                        )
                    )

    # 5. Orphan .raw/ file check (WARN)
    raw_dir = vault_root / ".raw"
    if raw_dir.is_dir():
        for raw_path in sorted(raw_dir.rglob("*"), key=lambda p: p.as_posix()):
            if not raw_path.is_file():
                continue
            if raw_path.name in {".gitkeep", ".DS_Store"} or raw_path.name.startswith("._"):
                continue
            if raw_path.resolve() not in referenced_raw:
                rel_raw = raw_path.relative_to(vault_root).as_posix()
                issues.append(
                    LintIssue(
                        "WARN",
                        rel_raw,
                        1,
                        "orphan-raw-file",
                        f"archived file '{rel_raw}' is not referenced by any type: paper note",
                    )
                )

    return issues


def format_report(issues: list[LintIssue], *, checked_notes: int, has_index: bool) -> str:
    errors = [iss for iss in issues if iss.level == "ERROR"]
    warnings = [iss for iss in issues if iss.level == "WARN"]
    total_files = checked_notes + (1 if has_index else 0)

    lines = [iss.format() for iss in issues]
    status = "PASS" if not errors else "FAIL"
    summary = (
        f"{status}: {total_files} files checked ({checked_notes} notes"
        f"{', index.md' if has_index else ''}) — "
        f"{len(errors)} errors, {len(warnings)} warnings"
    )
    lines.append(summary)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint an Obsidian Learning Harness vault.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Path to vault root (defaults to repository root).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures (exit 1 on WARN as well as ERROR).",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    issues = lint_vault(root)
    notes_dir = root / "notes"
    checked_notes = len(list(notes_dir.glob("*.md"))) if notes_dir.is_dir() else 0
    has_index = (root / "index.md").is_file()

    print(format_report(issues, checked_notes=checked_notes, has_index=has_index))

    has_error = any(iss.level == "ERROR" for iss in issues)
    has_warn = any(iss.level == "WARN" for iss in issues)
    if has_error or (args.strict and has_warn):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
