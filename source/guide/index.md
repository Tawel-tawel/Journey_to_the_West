---
title: 写作指南
date: 2026-06-03
---

## 内容分工

- `README.md`：写成游记展示页，负责地点介绍、旅行流程、照片、时间线、路线、预算和故事，风格可以接近美篇。
- `tips.md`：写成攻略页，负责交通、住宿、美食、避坑、开放时间、预约方式和注意事项。
- `photos/`：放图片，正文里使用 Markdown 图片语法引用。

## 游记结构

```markdown
# 地点名称

> 一句话简介。

## Overview

| 项目 | 内容 |
| --- | --- |
| 时间 | 2026-06 |
| 天数 | 2 天 1 晚 |

## Travel Story

正文。

![照片](./photos/01.jpg)
```

完整模板见仓库中的 `templates/place_readme_template.md`。
