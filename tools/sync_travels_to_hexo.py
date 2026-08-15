#!/usr/bin/env python3
"""Auto-discover travel README files under DEST_ROOT and sync them into Hexo pages.

Every directory under DEST_ROOT that contains a README.md and a tips.md or
photos/ folder is treated as a travel destination.  The script walks the
hierarchy, derives front-matter (continent, country, tags, slug) from the
directory path, reads the actual title from the first `# ` heading, and
writes/overwrites the corresponding Hexo page under SOURCE_TRAVELS.

Hand-written Hexo pages outside the travel set are never touched.
"""

from __future__ import annotations
import re
from datetime import date as Date

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST_ROOT = ROOT / "destinations"
SOURCE_TRAVELS = ROOT / "source" / "travels"

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

COORDS = {
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


def is_leaf_destination(leaf: Path) -> bool:
    has_content = (leaf / "tips.md").exists() or ((leaf / "photos").exists() and any((leaf / "photos").iterdir()))
    if not has_content:
        return False
    for child in leaf.iterdir():
        if child.is_dir() and (child / "README.md").exists() and ((child / "tips.md").exists() or ((child / "photos").exists() and any((child / "photos").iterdir()))):
            return False
    return True


def discover_travels() -> list[Travel]:
    travels: list[Travel] = []
    for readme in DEST_ROOT.rglob("README.md"):
        leaf = readme.parent
        if not is_leaf_destination(leaf):
            continue
        rel = leaf.relative_to(DEST_ROOT)
        parts = rel.parts
        if len(parts) < 2:
            continue

        title = NAME_MAP.get(parts[-1], read_title(readme) or display_name(parts[-1]))
        country_chinese = chinese_name(parts[1])
        hierarchy = [chinese_name(p) for p in parts]
        coords = COORDS.get(parts[-1], (None, None))

        hier_tuple = tuple(hierarchy)
        travels.append((Travel(
            title=title,
            slug=slugify(parts[-1]),
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
    tags = "\n".join(f"  - {tag}" for tag in travel.tags)
    hier = "\n".join(f"  - {h}" for h in hierarchy)
    lat_line = f"lat: {travel.lat}\n" if travel.lat is not None else ""
    lng_line = f"lng: {travel.lng}\n" if travel.lng is not None else ""
    desc_line = ""
    if travel.desc:
        safe = travel.desc.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
        desc_line = f'desc: "{safe}"\n'
    date_line = existing_date or Date.today().isoformat()
    return f"""---
title: {travel.title}
date: {date_line}
layout: post
continent: {travel.continent}
country: {travel.country}
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


def sync_travel(travel: Travel, hierarchy: tuple[str, ...] = ()) -> None:
    if not travel.source.exists():
        raise FileNotFoundError(travel.source)

    target_dir = SOURCE_TRAVELS / travel.slug
    target_dir.mkdir(parents=True, exist_ok=True)
    body = strip_first_heading(travel.source.read_text(encoding="utf-8"))
    body = clean_body(body)
    body = body.replace("./tips.md", "./tips")
    existing_date = read_existing_date(target_dir)
    (target_dir / "index.md").write_text(front_matter(travel, hierarchy, existing_date) + body, encoding="utf-8")

    tips_src = travel.source.parent / "tips.md"
    if tips_src.exists():
        tips_fm = f"""---
title: {travel.title} · 攻略
layout: page
---

"""
        (target_dir / "tips.md").write_text(tips_fm + tips_src.read_text(encoding="utf-8"), encoding="utf-8")


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

    for travel, hierarchy in travels:
        sync_travel(travel, hierarchy)


if __name__ == "__main__":
    main()
