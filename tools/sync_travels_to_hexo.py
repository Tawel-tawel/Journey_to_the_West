#!/usr/bin/env python3
"""Auto-discover travel README files under DEST_ROOT and sync them into Hexo pages.

Every directory under DEST_ROOT that contains a README.md and a tips.md or
photos/ folder is treated as a travel destination.  The script walks the
hierarchy, derives front-matter (continent, country, tags, slug) from the
directory path, reads the actual title from the first `# ` heading, and
writes/overwrites the corresponding Hexo page under SOURCE_TRAVELS.

Hand-written Hexo pages outside the travel set are never touched.

Behaviour notes:
- Any destination directory that has its own content (tips.md or a non-empty
  photos/ folder) is synced, even when it also has sub-destinations.
- Files are only rewritten when their content actually changes, so that
  `updated_option: mtime` in _config.yml keeps reflecting real edits.
- photos/ folders are copied next to the generated page, so image links like
  `./photos/01.jpg` work both on the site and on GitHub.
- Stale page directories (e.g. after a destination was renamed or removed)
  and stale tips.md / photos/ copies are cleaned up automatically.
- Leaf slugs are the directory name; if two destinations share the same leaf
  name, the colliding ones fall back to a full-path slug to stay unique.
- COORDS accepts both full relative paths ("Asia/China/Guangxi/Guilin") and
  bare leaf names ("Guilin"); the full path wins on conflict.
"""

from __future__ import annotations
import re
import shutil
from collections import Counter
from datetime import date as Date

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST_ROOT = ROOT / "destinations"
SOURCE_TRAVELS = ROOT / "source" / "travels"

# Files that do not count as real content inside photos/ folders.
JUNK_FILES = {".gitkeep", ".DS_Store"}

CONTINENT_MAP = {
    "Asia": "亚洲",
    "Europe": "欧洲",
    "North_America": "北美洲",
    "South_America": "南美洲",
    "Africa": "非洲",
    "Oceania": "大洋洲",
    "Antarctica": "南极洲",
}


NAME_MAP = {
    "Asia": "亚洲",
    "China": "中国",
    "Beijing": "北京",
    "Guangxi": "广西",
    "Guilin": "桂林",
    "Liuzhou": "柳州",
    "Hainan": "海南",
    "Haikou": "海口",
    "Jilin": "吉林",
    "Changchun": "长春",
    "Jilin_City": "吉林市",
    "Songyuan": "松原",
    "Sichuan": "四川",
    "Aba": "阿坝州",
    "Chengdu": "成都",
    "Jinli": "锦里",
    "Kuanzhai_Alley": "宽窄巷子",
    "Jiuzhaigou": "九寨沟",
}

# Keyed by full relative path (preferred) or bare leaf name (fallback).
COORDS = {
    "Asia/China/Guangxi/Guilin":   (25.2736, 110.2900),
    "Asia/China/Guangxi/Liuzhou":  (24.3263, 109.4280),
    "Asia/China/Hainan/Haikou":    (20.0440, 110.3580),
    "Asia/China/Sichuan/Chengdu/Jinli": (30.6476, 104.0478),
    "Asia/China/Sichuan/Chengdu/Kuanzhai_Alley": (30.6716, 104.0580),
    "Asia/China/Sichuan/Aba/Jiuzhaigou": (33.2611, 104.2386),
    "Asia/China/Beijing":          (39.9042, 116.4074),
    "Asia/China/Jilin/Changchun":  (43.8966, 125.3262),
    "Asia/China/Jilin/Songyuan":   (45.1298, 124.8260),
    "Asia/China/Jilin/Jilin_City": (43.8378, 126.5486),
    # Legacy leaf-name keys, kept as fallback:
    "Guilin":       (25.2736, 110.2900),
    "Liuzhou":      (24.3263, 109.4280),
    "Haikou":       (20.0440, 110.3580),
    "Jinli":        (30.6476, 104.0478),
    "Kuanzhai_Alley": (30.6716, 104.0580),
    "Jiuzhaigou":   (33.2611, 104.2386),
    "Beijing":      (39.9042, 116.4074),
    "Changchun":    (43.8966, 125.3262),
    "Songyuan":     (45.1298, 124.8260),
    "Jilin_City":   (43.8378, 126.5486),
}


def chinese_name(name: str) -> str:
    return NAME_MAP.get(name, display_name(name))


def yaml_str(value: str) -> str:
    """Quote a string for safe use as a YAML scalar."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


@dataclass(frozen=True)
class Travel:
    title: str
    slug: str
    source: Path
    tags: tuple[str, ...]
    continent: str
    country: str
    lat: float | None = None
    lng: float | None = None
    desc: str = ""


def display_name(name: str) -> str:
    return name.replace("_", " ")


def slugify(name: str) -> str:
    return name.lower().replace("_", "-")


def read_title(readme: Path) -> str:
    lines = readme.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def read_desc(readme: Path) -> str:
    """Return the first substantive paragraph from a README.

    Skips the title, blockquote status lines, list items, and template
    boilerplate like "正式内容可参考仓库中的 [地点 README 模板](...)".
    """
    lines = readme.read_text(encoding="utf-8").splitlines()

    def clean(line: str) -> str:
        line = re.sub(r"\[[^\]]+\]\([^)]*\)", "", line)
        line = re.sub(r"\[/\]\([^)]*\)", "", line)
        return line.strip()

    for line in lines:
        s = line.strip()
        if not s or s.startswith("#") or s.startswith(">") or s.startswith(("-", "*", "1.")):
            continue
        for marker in ("正式内容请参阅", "正式内容可参考仓库", "页面将随", "旅行记录索引"):
            idx = s.find(marker)
            if idx > 0:
                s = s[:idx].strip(" ，。；：,")
                break
        s = clean(s)
        if not s:
            continue
        return s
    return ""


def has_real_content(directory: Path) -> bool:
    """True if the directory exists and holds at least one non-junk entry."""
    if not directory.exists():
        return False
    return any(entry.name not in JUNK_FILES for entry in directory.iterdir())


def is_leaf_destination(leaf: Path) -> bool:
    """A directory is synced when it has its own content (tips.md or photos).

    Since v2, directories that ALSO have sub-destinations are synced too
    (e.g. 阿坝州 with its own tips.md plus a 九寨沟 child) — they become a
    page of their own and appear in the tree as a clickable branch.
    """
    return (leaf / "tips.md").exists() or has_real_content(leaf / "photos")


def discover_travels() -> list[tuple[Travel, tuple[str, ...]]]:
    candidates: list[tuple[tuple[str, ...], Path]] = []
    for readme in DEST_ROOT.rglob("README.md"):
        leaf = readme.parent
        if not is_leaf_destination(leaf):
            continue
        rel = leaf.relative_to(DEST_ROOT)
        parts = rel.parts
        if len(parts) < 2:
            continue
        candidates.append((parts, readme))

    # Leaf-name slugs first; disambiguate duplicates with a full-path slug.
    leaf_counts = Counter(slugify(parts[-1]) for parts, _ in candidates)

    travels: list[tuple[Travel, tuple[str, ...]]] = []
    for parts, readme in candidates:
        leaf_slug = slugify(parts[-1])
        if leaf_counts[leaf_slug] > 1:
            slug = slugify("-".join(parts))
        else:
            slug = leaf_slug

        title = NAME_MAP.get(parts[-1], read_title(readme) or display_name(parts[-1]))
        country_chinese = chinese_name(parts[1])
        hierarchy = [chinese_name(p) for p in parts]
        coords = COORDS.get("/".join(parts), COORDS.get(parts[-1], (None, None)))

        hier_tuple = tuple(hierarchy)
        travels.append((Travel(
            title=title,
            slug=slug,
            source=readme,
            tags=(country_chinese,),
            continent=CONTINENT_MAP.get(parts[0], parts[0]),
            country=country_chinese,
            lat=coords[0],
            lng=coords[1],
            desc=read_desc(readme),
        ), hier_tuple))
    return travels


def front_matter(travel: Travel, hierarchy: tuple[str, ...] = (), existing_date: str = "") -> str:
    tags = "\n".join(f"  - {yaml_str(tag)}" for tag in travel.tags)
    hier = "\n".join(f"  - {yaml_str(h)}" for h in hierarchy)
    lat_line = f"lat: {travel.lat}\n" if travel.lat is not None else ""
    lng_line = f"lng: {travel.lng}\n" if travel.lng is not None else ""
    desc_line = ""
    if travel.desc:
        desc_line = f"desc: {yaml_str(travel.desc)}\n"
    date_line = existing_date or Date.today().isoformat()
    return f"""---
title: {yaml_str(travel.title)}
date: {date_line}
layout: post
continent: {yaml_str(travel.continent)}
country: {yaml_str(travel.country)}
categories:
  - travel
tags:
{tags}
hierarchy:
{hier}
{desc_line}{lat_line}{lng_line}---
"""


def strip_first_heading(markdown: str) -> str:
    lines = markdown.splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).lstrip() + "\n"
    return markdown


def clean_body(markdown: str) -> str:
    """Strip repository-internal boilerplate before publishing.

    Removes the "[地点 README 模板](...)" pointer sentence (broken once the
    page is nested under source/travels/<slug>/), leaving site content intact.
    """
    markdown = re.sub(r"正式内容(?:请参阅|可参考仓库中的)\s*[^。\n]*\[[^\]]*模板\][^\n]*。?", "", markdown)
    return markdown.strip() + "\n"


def read_existing_date(target_dir: Path) -> str:
    if not (target_dir / "index.md").exists():
        return ""
    text = (target_dir / "index.md").read_text(encoding="utf-8")
    m = re.search(r"^date:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def write_if_changed(path: Path, content: str) -> bool:
    """Write only when content differs, keeping mtime (and thus `updated`) stable."""
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def sync_photos(leaf: Path, target_dir: Path) -> str:
    """Mirror the destination's photos/ folder into the generated page dir.

    Returns "copied", "removed", or "" when nothing had to happen.
    """
    photos_src = leaf / "photos"
    photos_dst = target_dir / "photos"
    src_has_photos = has_real_content(photos_src)

    if src_has_photos:
        if photos_dst.exists():
            shutil.rmtree(photos_dst)
        shutil.copytree(photos_src, photos_dst, ignore=shutil.ignore_patterns(*JUNK_FILES))
        return "copied"
    if photos_dst.exists():
        shutil.rmtree(photos_dst)
        return "removed"
    return ""


def sync_travel(travel: Travel, hierarchy: tuple[str, ...] = ()) -> str:
    """Sync one destination. Returns "written", "unchanged", or "removed-photos"."""
    if not travel.source.exists():
        raise FileNotFoundError(travel.source)

    target_dir = SOURCE_TRAVELS / travel.slug
    target_dir.mkdir(parents=True, exist_ok=True)
    body = strip_first_heading(travel.source.read_text(encoding="utf-8"))
    body = clean_body(body)
    body = body.replace("./tips.md", "./tips.html")
    existing_date = read_existing_date(target_dir)
    index_written = write_if_changed(
        target_dir / "index.md", front_matter(travel, hierarchy, existing_date) + body
    )

    tips_src = travel.source.parent / "tips.md"
    tips_dst = target_dir / "tips.md"
    tips_written = False
    if tips_src.exists():
        tips_fm = f"""---
title: {yaml_str(f"{travel.title} · 攻略")}
layout: page
---

"""
        tips_written = write_if_changed(tips_dst, tips_fm + tips_src.read_text(encoding="utf-8"))
    elif tips_dst.exists():
        tips_dst.unlink()

    photos_status = sync_photos(travel.source.parent, target_dir)

    if index_written or tips_written or photos_status == "copied":
        return "written"
    if photos_status == "removed":
        return "removed-photos"
    return "unchanged"


def cleanup_stale_dirs(valid_slugs: set[str]) -> list[str]:
    """Remove page directories that no longer map to any destination."""
    removed: list[str] = []
    if not SOURCE_TRAVELS.exists():
        return removed
    for child in SOURCE_TRAVELS.iterdir():
        if child.is_dir() and child.name not in valid_slugs:
            shutil.rmtree(child)
            removed.append(child.name)
    return removed


def main() -> None:
    travels = discover_travels()
    if not travels:
        print(f"Warning: no travel destinations found under {DEST_ROOT}")
        return

    uncoordinated = [t.slug for t, _ in travels if t.lat is None or t.lng is None]
    if uncoordinated:
        names = ", ".join(uncoordinated)
        print(f"WARNING: {len(uncoordinated)} destination(s) lack coordinates in COORDS and will NOT appear on the map: {names}")
        print(f"          Add entries to COORDS in {__file__} to place them on the map.")
    else:
        print(f"OK: all {len(travels)} destinations have coordinates.")

    counts = Counter(sync_travel(travel, hierarchy) for travel, hierarchy in travels)

    removed = cleanup_stale_dirs({t.slug for t, _ in travels})
    for name in removed:
        print(f"CLEANUP: removed stale page directory source/travels/{name}/")

    print(
        f"Synced {len(travels)} destinations: "
        f"{counts.get('written', 0)} written, "
        f"{counts.get('unchanged', 0)} unchanged, "
        f"{counts.get('removed-photos', 0)} photo-only cleanup."
    )


if __name__ == "__main__":
    main()
