#!/usr/bin/env python3
"""Generate Unraid <Changes> BBCode blocks from each app's CHANGELOG.md.

This repo holds multiple Unraid templates, one per top-level app folder. Each
app folder contains a CHANGELOG.md and a <app>.xml template with a <Changes>
block. This script regenerates those blocks from the changelogs.

For every configured app it reads each release >= the app's start_version,
flattens all entries (Features, Bug Fixes, Performance, ...) into a single
bullet list per version, renders BBCode, and writes it into the template's
<Changes> block at the NEW_CHANGES_HERE marker (everything below the marker is
regenerated; the header above it is preserved).

Usage:
  python3 scripts/generate-changes.py                 # all configured apps
  python3 scripts/generate-changes.py video-ware      # just these app(s)
  python3 scripts/generate-changes.py --dry-run       # print, don't write

Add a new app by dropping a folder with a CHANGELOG.md and <app>.xml, then
registering it in APPS below. No third-party dependencies.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# --- App registry -----------------------------------------------------------
# Key = top-level folder name. Each app's changelog is <folder>/CHANGELOG.md and
# its template is <folder>/<xml> (defaults to <folder>.xml).
#
#   "start_version"  required  oldest release to include, inclusive
#   "xml"            optional  template filename (default "<folder>.xml")
#   "title"         optional  header title for brand-new templates lacking a
#                              header (existing headers are always preserved)
#   "changelog_url" optional  "Full changelog" link for brand-new templates
APPS: dict[str, dict] = {
    "video-ware": {
        "start_version": "0.8.0",
        "title": "VideoWare Release Notes",
        "changelog_url": "https://github.com/make-ware/video-ware/blob/main/CHANGELOG.md",
    },
}

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKER = "<!-- NEW_CHANGES_HERE -->"  # anchor; content after it is regenerated
SEP = "&#xD;"                         # Unraid renders this as a blank line

# --- Parsing -----------------------------------------------------------------

# Matches:  ## [0.8.2](https://.../compare/...) (2026-06-22)
VERSION_RE = re.compile(r"^##\s+\[(\d+\.\d+\.\d+)\]\([^)]*\)\s+\((.*?)\)\s*$")
# A list item:  * subject ([abc1234](https://...))
ITEM_RE = re.compile(r"^\s*[*-]\s+(.*\S)\s*$")
# Trailing commit reference(s):  ([abc1234](https://...))
TRAILING_REF_RE = re.compile(r"\s*\(\[[0-9a-f]{6,}\]\([^)]*\)\)\s*$")
# Conventional-commit scope at the start:  **webapp:**
SCOPE_RE = re.compile(r"^\*\*[^*]+:\*\*\s*")


def version_tuple(v: str) -> tuple[int, ...]:
    return tuple(int(p) for p in v.split("."))


def clean_subject(text: str) -> str:
    """Strip commit links / scope prefixes and tidy a changelog line."""
    text = TRAILING_REF_RE.sub("", text)
    text = SCOPE_RE.sub("", text)
    text = text.replace("\\n", " ").strip()
    text = re.sub(r"\s{2,}", " ", text)  # collapse whitespace runs
    if text:
        text = text[0].upper() + text[1:]
    return text


def parse_changelog(path: Path, start: str) -> list[dict]:
    """Return [{version, date, items[]}, ...] for releases >= start, newest first."""
    floor = version_tuple(start)
    releases: list[dict] = []
    current: dict | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        vm = VERSION_RE.match(raw)
        if vm:
            version, date = vm.group(1), vm.group(2)
            if version_tuple(version) >= floor:
                current = {"version": version, "date": date, "items": []}
                releases.append(current)
            else:
                current = None  # below the floor — skip its items
            continue

        if current is None:
            continue
        if raw.startswith("###"):  # category header — flatten, so ignore
            continue

        im = ITEM_RE.match(raw)
        if im:
            subject = clean_subject(im.group(1))
            if subject and subject not in current["items"]:  # dedupe within release
                current["items"].append(subject)

    releases.sort(key=lambda r: version_tuple(r["version"]), reverse=True)
    return [r for r in releases if r["items"]]


# --- Rendering ---------------------------------------------------------------

def render_release(rel: dict) -> str:
    lines = [f"[b]v{rel['version']}[/b] ({rel['date']})", "[list]"]
    lines += [f"[*]{item}" for item in rel["items"]]
    lines.append("[/list]")
    return "\n".join(lines)


def render_blocks(releases: list[dict]) -> str:
    return f"\n{SEP}\n".join(render_release(r) for r in releases)


def default_header(cfg: dict, name: str) -> str:
    title = cfg.get("title", f"{name} Release Notes")
    lines = [f"[center][b]{title}[/b][/center]", SEP]
    if cfg.get("changelog_url"):
        lines += [f"[i]Full changelog: {cfg['changelog_url']}[/i]", SEP]
    lines.append(MARKER)
    return "\n".join(lines)


# --- XML injection -----------------------------------------------------------

CHANGES_RE = re.compile(r"(<Changes>\n)(.*?)(\n</Changes>)", re.DOTALL)


def inject(xml_text: str, generated: str, cfg: dict, name: str) -> str:
    m = CHANGES_RE.search(xml_text)
    if not m:
        raise ValueError("no <Changes>...</Changes> block found")

    body = m.group(2)
    if MARKER in body:
        # Keep everything up to and including the marker; regenerate the rest.
        header = body[: body.index(MARKER) + len(MARKER)]
    else:
        header = default_header(cfg, name)

    new_body = f"{header}\n{SEP}\n{generated}"
    return xml_text[: m.start()] + m.group(1) + new_body + m.group(3) + xml_text[m.end():]


# --- Per-app driver ----------------------------------------------------------

def resolve_xml(app_dir: Path, name: str, cfg: dict) -> Path:
    if cfg.get("xml"):
        return app_dir / cfg["xml"]
    preferred = app_dir / f"{name}.xml"
    if preferred.exists():
        return preferred
    xmls = sorted(app_dir.glob("*.xml"))
    if len(xmls) == 1:
        return xmls[0]
    raise FileNotFoundError(
        f"could not pick a template in {app_dir} (set 'xml' in APPS['{name}'])"
    )


def process_app(name: str, cfg: dict, dry_run: bool) -> bool:
    app_dir = REPO_ROOT / name
    changelog = app_dir / "CHANGELOG.md"
    if not changelog.exists():
        print(f"[{name}] error: changelog not found: {changelog}", file=sys.stderr)
        return False

    releases = parse_changelog(changelog, cfg["start_version"])
    if not releases:
        print(
            f"[{name}] error: no releases >= {cfg['start_version']} in {changelog.name}",
            file=sys.stderr,
        )
        return False

    generated = render_blocks(releases)
    versions = ", ".join(r["version"] for r in releases)
    print(f"[{name}] releases >= {cfg['start_version']}: {versions}", file=sys.stderr)

    if dry_run:
        print(f"\n----- {name} -----\n{generated}\n")
        return True

    try:
        xml_path = resolve_xml(app_dir, name, cfg)
    except FileNotFoundError as e:
        print(f"[{name}] error: {e}", file=sys.stderr)
        return False
    if not xml_path.exists():
        print(f"[{name}] error: template not found: {xml_path}", file=sys.stderr)
        return False

    try:
        updated = inject(xml_path.read_text(encoding="utf-8"), generated, cfg, name)
    except ValueError as e:
        print(f"[{name}] error: {e} in {xml_path.name}", file=sys.stderr)
        return False
    xml_path.write_text(updated, encoding="utf-8")
    print(f"[{name}] wrote <Changes> block to {xml_path.name}", file=sys.stderr)
    return True


# --- Main --------------------------------------------------------------------

def main(argv: list[str]) -> int:
    dry_run = False
    requested: list[str] = []
    for arg in argv:
        if arg in ("--dry-run", "-n"):
            dry_run = True
        elif arg in ("--help", "-h"):
            print(__doc__)
            return 0
        elif arg.startswith("-"):
            print(f"error: unknown option {arg}", file=sys.stderr)
            return 2
        else:
            requested.append(arg)

    # Warn about app folders with a changelog that aren't registered.
    for d in sorted(REPO_ROOT.iterdir()):
        if d.is_dir() and (d / "CHANGELOG.md").exists() and d.name not in APPS:
            print(f"note: '{d.name}' has a CHANGELOG.md but is not in APPS", file=sys.stderr)

    names = requested or list(APPS)
    unknown = [n for n in names if n not in APPS]
    if unknown:
        print(f"error: unknown app(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"known apps: {', '.join(APPS) or '(none)'}", file=sys.stderr)
        return 2

    ok = all(process_app(n, APPS[n], dry_run) for n in names)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
