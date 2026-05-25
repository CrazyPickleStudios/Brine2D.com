"""
Post-processes DefaultDocumentation output in docs/api/:
  - Removes assembly breadcrumb lines (any #+ heading that is only a link at the top)
  - Strips pilcrow/section sign anchors from all heading lines
  - Adds proper front matter with title extracted from the ## heading
  - Injects a ## Definition block with Namespace: link beneath the title
  - Adds hide: toc since the ToC only ever mirrors the single heading
"""

import os
import re

API_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "docs", "api"))

# Matches a heading line that is purely a breadcrumb link, e.g. "#### [Brine2D](../index.md)"
_BREADCRUMB_RE = re.compile(r"^#{1,6}\s+\[.+\]\(.+\)\s*$")


def _strip_heading_anchor(line):
    """Remove trailing pilcrow/section-sign permalink from a heading line."""
    return re.sub(r"\s*[¶§]\s*$", "", line)


def _namespace_info(filepath):
    """
    Derives namespace name and a relative link to the namespace index page
    from the file path within docs/api/.

    Path patterns:
      docs/api/Brine2D/Input/IInputContext/GetGamepadLeftStick(int)/index.md  -> method page
      docs/api/Brine2D/Input/IInputContext/index.md                           -> type page
      docs/api/Brine2D/Input/index.md                                         -> namespace page (skip)
    """
    rel = os.path.relpath(filepath, API_DIR)
    parts = rel.replace("\\", "/").split("/")[:-1]  # drop "index.md"

    if len(parts) < 3:
        return None, None

    # Member pages have a signature with '(' in the last segment
    if "(" in parts[-1]:
        ns_parts = parts[:-2]  # namespace path segments (drop type + member)
    else:
        ns_parts = parts[:-1]  # namespace path segments (drop type)

    if not ns_parts:
        return None, None

    namespace = ".".join(ns_parts)
    # Relative link: go up (len(parts) - len(ns_parts)) directories
    up = len(parts) - len(ns_parts)
    ns_link = "/".join([".."] * up) + "/"
    return namespace, ns_link


def process_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Skip files that already have front matter (e.g. our hand-written index.md)
    if content.startswith("---"):
        return

    lines = content.splitlines()

    # Strip leading breadcrumb-only heading lines (any depth)
    while lines and _BREADCRUMB_RE.match(lines[0]):
        lines.pop(0)
    while lines and lines[0].strip() == "":
        lines.pop(0)

    # Remove pilcrow anchors from all heading lines throughout the page
    lines = [
        _strip_heading_anchor(line) if line.startswith("#") else line
        for line in lines
    ]

    # Extract title from the first ## heading, then remove that line from the body
    # (MkDocs Material renders the front matter title as h1; keeping ## creates a duplicate)
    title = None
    title_index = None
    for i, line in enumerate(lines):
        m = re.match(r"^## (.+)$", line)
        if m:
            title = re.sub(r"\\(.)", r"\1", m.group(1)).strip()
            title_index = i
            break

    if not title:
        return  # nothing useful to do

    lines.pop(title_index)
    while title_index < len(lines) and lines[title_index].strip() == "":
        lines.pop(title_index)

    # Build the Definition block with namespace
    namespace, ns_link = _namespace_info(filepath)
    if namespace and ns_link:
        definition_block = f"## Definition\n\n**Namespace:** [{namespace}]({ns_link})\n\n"
    else:
        definition_block = ""

    front_matter = f"---\ntitle: \"{title}\"\nhide:\n  - toc\n---\n\n"
    new_content = front_matter + definition_block + "\n".join(lines) + "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)


def main():
    root_index = os.path.join(API_DIR, "index.md")
    count = 0
    for dirpath, _, filenames in os.walk(API_DIR):
        for filename in filenames:
            if not filename.endswith(".md"):
                continue
            filepath = os.path.join(dirpath, filename)
            if os.path.abspath(filepath) == os.path.abspath(root_index):
                continue  # never touch docs/api/index.md — it's hand-written
            process_file(filepath)
            count += 1
    print(f"Post-processed {count} API files.")


if __name__ == "__main__":
    main()
