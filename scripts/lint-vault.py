#!/usr/bin/env python3
"""Zero-dependency Obsidian vault linter for MyVault.

Checks:
1. Index <-> Notes Sync (index.md <-> notes/*.md)
2. Dead / Dangling [[wikilinks]] in index.md and notes/*.md
3. YAML Frontmatter Hygiene (required fields, quoted [[...]], no $ in title/aliases)
4. Obsidian MathJax x [[wikilink]] Iron Rules:
   - No [[...]] inside $...$ or $$...$$
   - No $...$ inside [[...]]
   - No $...$ or $$...$$ wrapped inside **...**
   - No prose \\implies outside $$...$$ display math blocks
   - No leading/trailing spaces inside inline $...$
5. Bidirectional Link Warning & .raw/ Archive Integrity for paper notes
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REQUIRED_FRONTMATTER_FIELDS = ("title", "type", "created", "updated", "status")

WIKILINK_RE = re.compile(r"\[\[([^\[\]\n]+?)\]\]")
MATH_DOLLAR_RE = re.compile(r"(?<!\\)\$")
IMPLIES_RE = re.compile(r"\\implies(?![A-Za-z])")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


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


def _extract_wikilink_target(raw_inner: str) -> str | None:
    """Extract note stem from [[Target#Heading|Alias]], or None for same-note #Heading."""
    parts = re.split(r"(?<!\\)\|", raw_inner, maxsplit=1)
    target_part = parts[0].replace("\\|", "|").strip()
    if target_part.startswith("#"):
        return None
    target = target_part.split("#", 1)[0].strip()
    if target.endswith(".md"):
        target = target[:-3].strip()
    return target


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
    current_key: str | None = None

    for idx in range(1, close_idx):
        lineno = idx + 1
        raw_line = lines[idx]
        code_part, quoted_map = _strip_yaml_comment_with_quote_map(raw_line)
        stripped = code_part.strip()
        if not stripped:
            continue

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
            target = _extract_wikilink_target(m.group(1))
            if target is not None:
                wikilinks.append((lineno, target))

        # Parse top-level key: value and indented/list continuations.
        if not raw_line[0].isspace() and not stripped.startswith("-") and ":" in code_part:
            key, _, rest = code_part.partition(":")
            key = key.strip()
            current_key = key
            field_lines[key] = lineno
            val = rest.strip()
            fields[key] = _unquote_yaml_scalar(val)
            if key == "aliases" and val:
                aliases_values.append((lineno, val))
        elif current_key == "aliases" and stripped:
            aliases_values.append((lineno, stripped))
        elif current_key and current_key in fields and not fields[current_key] and stripped:
            fields[current_key] = _unquote_yaml_scalar(stripped)

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
    )


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


def _scan_body(
    lines: list[str],
    *,
    start_line: int,
    path: str,
    issues: list[LintIssue],
) -> list[tuple[int, str]]:
    """Scan Markdown body for MathJax/wikilink violations and extract body wikilinks."""
    body_wikilinks: list[tuple[int, str]] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    in_html_comment = False
    in_display_math = False
    display_math_start_line = 0

    for idx in range(start_line - 1, len(lines)):
        lineno = idx + 1
        line = lines[idx]

        # 1. Fenced code blocks
        if in_fence:
            close_pat = re.compile(rf"^\s*{re.escape(fence_char)}{{{fence_len},}}\s*$")
            if close_pat.match(line):
                in_fence = False
            continue

        if not in_display_math and not in_html_comment:
            m_fence = FENCE_RE.match(line)
            if m_fence:
                fence_str = m_fence.group(1)
                fence_char = fence_str[0]
                fence_len = len(fence_str)
                in_fence = True
                continue

        # Tokenize line into ("BOLD",) or ("MATH",) for bold-wrapping check.
        tokens: list[str] = []
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

            # Inline math $...$
            if line[i] == "$":
                close_d = _find_closing_inline_dollar(line, i)
                if close_d is not None:
                    segment = line[i + 1 : close_d]
                    _check_math_segment(
                        segment, is_display=False, path=path, lineno=lineno, issues=issues
                    )
                    tokens.append("MATH")
                    i = close_d + 1
                    continue
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
                    target = _extract_wikilink_target(raw_inner)
                    if target is not None:
                        body_wikilinks.append((lineno, target))
                    i = m_wl.end()
                    continue

            i += 1

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
            LintIssue("ERROR", path, len(lines), "fence-unclosed", "unclosed fenced code block")
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

    # 1. Lint index.md and verify Index <-> Notes sync
    indexed_targets: set[str] = set()
    if not index_path.is_file():
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
        _, index_links = _collect_wikilinks_from_note(index_text)
        indexed_targets = {target for _, target in index_links}

        for stem in sorted(known_notes):
            if stem not in indexed_targets:
                issues.append(
                    LintIssue(
                        "ERROR",
                        "index.md",
                        1,
                        "index-missing-note",
                        f"notes/{stem}.md is not linked in index.md",
                    )
                )

    # 2. Lint every note in notes/*.md and collect outgoing graph + paper archives
    outgoing: dict[str, dict[str, int]] = {}
    for note_path in note_files:
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
        fm, links = _collect_wikilinks_from_note(text)

        # Outgoing link map (preserve earliest line number for clean reporting)
        note_targets: dict[str, int] = {}
        for lineno, target in links:
            if target in known_notes and target != note_path.stem:
                note_targets.setdefault(target, lineno)
        outgoing[note_path.stem] = note_targets

        # Archive check for type: paper notes
        if fm.fields.get("type") == "paper":
            source_val = fm.fields.get("source", "").strip()
            src_line = fm.field_lines.get("source", 1)
            if source_val.startswith(".raw/"):
                raw_file = vault_root / source_val
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

    # 3. Bidirectional link check (WARN only, does not fail exit code 0)
    for src in sorted(outgoing):
        for dst, lineno in sorted(outgoing[src].items()):
            if src not in outgoing.get(dst, {}):
                issues.append(
                    LintIssue(
                        "WARN",
                        f"notes/{src}.md",
                        lineno,
                        "asymmetric-link",
                        f"[[{src}]] links to [[{dst}]], but [[{dst}]] does not link back",
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
