"""
Post-processes DefaultDocumentation output in docs/api/:
  - Removes the assembly breadcrumb line (#### [Brine2D]...)
  - Adds proper front matter with title extracted from the ## heading
  - Adds hide: toc since the ToC only ever mirrors the single heading
"""

import os
import re

API_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "docs", "api"))


def process_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Skip files that already have front matter (e.g. our hand-written index.md)
    if content.startswith("---"):
        return

    lines = content.splitlines()

    # Strip leading breadcrumb lines (#### [...] lines at the top)
    while lines and lines[0].startswith("####"):
        lines.pop(0)
    while lines and lines[0].strip() == "":
        lines.pop(0)

    # Extract title from the first ## heading
    title = None
    for line in lines:
        m = re.match(r"^## (.+)$", line)
        if m:
            # Clean up escaped dots and trailing anchors like \. and ' ¶'
            title = re.sub(r"\\(.)", r"\1", m.group(1))
            title = re.sub(r"\s*[¶§].*$", "", title).strip()
            break

    if not title:
        return  # nothing useful to do

    front_matter = f"---\ntitle: \"{title}\"\nhide:\n  - toc\n---\n\n"
    new_content = front_matter + "\n".join(lines) + "\n"

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
