#!/usr/bin/env python3
"""Sync selected travel README files into Hexo travel pages.

The script only overwrites pages listed in TRAVELS. Other hand-written
Hexo pages stay untouched.
"""

from __future__ import annotations
from datetime import date as Date

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_TRAVELS = ROOT / "source" / "travels"


@dataclass(frozen=True)
class Travel:
    title: str
    slug: str
    source: Path
    tags: tuple[str, ...]
    continent: str = "亚洲"
    country: str = "中国"


TRAVELS = (
    Travel("桂林", "guilin", ROOT / "Asia/China/Guangxi/Guilin/README.md", ("广西", "桂林")),
    Travel("柳州", "liuzhou", ROOT / "Asia/China/Guangxi/Liuzhou/README.md", ("广西", "柳州")),
    Travel("海口", "haikou", ROOT / "Asia/China/Hainan/Haikou/README.md", ("海南", "海口")),
    Travel("宽窄巷子", "kuanzhai-alley", ROOT / "Asia/China/Sichuan/Chengdu/Kuanzhai_Alley/README.md", ("四川", "成都")),
    Travel("锦里", "jinli", ROOT / "Asia/China/Sichuan/Chengdu/Jinli/README.md", ("四川", "成都")),
    Travel("九寨沟", "jiuzhaigou", ROOT / "Asia/China/Sichuan/Aba/Jiuzhaigou/README.md", ("四川", "阿坝州", "九寨沟")),
    Travel("北京", "beijing", ROOT / "Asia/China/Beijing/README.md", ("北京",)),
    Travel("长春", "changchun", ROOT / "Asia/China/Jilin/Changchun/README.md", ("吉林", "长春")),
    Travel("松原", "songyuan", ROOT / "Asia/China/Jilin/Songyuan/README.md", ("吉林", "松原")),
    Travel("吉林市", "jilin-city", ROOT / "Asia/China/Jilin/Jilin_City/README.md", ("吉林", "吉林市")),
)


def front_matter(travel: Travel) -> str:
    tags = "\n".join(f"  - {tag}" for tag in travel.tags)
    return f"""---
title: {travel.title}
date: {Date.today().isoformat()}
continent: {travel.continent}
country: {travel.country}
categories:
  - travel
tags:
{tags}
"""


def strip_first_heading(markdown: str) -> str:
    lines = markdown.splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).lstrip() + "\n"
    return markdown


def sync_travel(travel: Travel) -> None:
    if not travel.source.exists():
        raise FileNotFoundError(travel.source)

    target_dir = SOURCE_TRAVELS / travel.slug
    target_dir.mkdir(parents=True, exist_ok=True)
    body = strip_first_heading(travel.source.read_text(encoding="utf-8"))
    body = body.replace("./tips.md", "./tips")
    (target_dir / "index.md").write_text(front_matter(travel) + body, encoding="utf-8")

    tips_src = travel.source.parent / "tips.md"
    if tips_src.exists():
        tips_fm = f"""---
title: {travel.title} · 攻略
layout: page
---

"""
        (target_dir / "tips.md").write_text(tips_fm + tips_src.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> None:
    for travel in TRAVELS:
        sync_travel(travel)


if __name__ == "__main__":
    main()
