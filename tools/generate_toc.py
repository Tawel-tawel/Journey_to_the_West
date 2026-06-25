#!/usr/bin/env python3
"""Generate the travel directory table of contents in README.md."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST_ROOT = ROOT / "destinations"
README = ROOT / "README.md"
START = "<!-- TOC:START -->"
END = "<!-- TOC:END -->"

IGNORE_DIRS = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    "__pycache__",
    "photos",
}

ORDER = [
    "Asia",
    "Europe",
    "North_America",
    "South_America",
    "Africa",
    "Oceania",
    "Antarctica",
]


def display_name(path: Path) -> str:
    return path.name.replace("_", " ")


def sort_key(path: Path) -> tuple[int, str]:
    if path.parent == ROOT and path.name in ORDER:
        return (ORDER.index(path.name), path.name.lower())
    return (len(ORDER), path.name.lower())


def iter_visible_dirs(path: Path) -> list[Path]:
    return sorted(
        [
            child
            for child in path.iterdir()
            if child.is_dir() and child.name not in IGNORE_DIRS and not child.name.startswith(".")
        ],
        key=sort_key,
    )


def build_toc(path: Path = ROOT, depth: int = 0) -> list[str]:
    lines: list[str] = []
    for child in iter_visible_dirs(path):
        rel = child.relative_to(ROOT).as_posix()
        indent = "  " * depth
        lines.append(f"{indent}- [{display_name(child)}](./{rel}/)")
        lines.extend(build_toc(child, depth + 1))
    return lines


def replace_toc(readme_text: str, toc: str) -> str:
    if START not in readme_text or END not in readme_text:
        raise SystemExit(f"README.md must contain {START} and {END} markers.")

    before, rest = readme_text.split(START, 1)
    _, after = rest.split(END, 1)
    return f"{before}{START}\n{toc}\n{END}{after}"


def main() -> None:
    if not DEST_ROOT.exists():
        print(f"Warning: {DEST_ROOT} not found. Skipping TOC update.")
        return
    toc = "\n".join(build_toc(DEST_ROOT))
    README.write_text(replace_toc(README.read_text(encoding="utf-8"), toc), encoding="utf-8")


if __name__ == "__main__":
    main()
