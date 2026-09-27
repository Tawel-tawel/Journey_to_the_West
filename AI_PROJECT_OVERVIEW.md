# Journey to the West — 项目结构概览

> 给 AI 辅助工具看的项目介绍。阅读此文件后可快速理解项目全貌。

## 一句话

一个 Hexo 旅行博客，原始游记按 `大洲/国家/省份/城市/地点` 目录结构保存在 `destinations/` 中，通过脚本自动同步为 Hexo 页面并部署到 GitHub Pages。

## 目录结构

```
/
├── destinations/               # 原始旅行资料库（核心数据文件夹）
│   └── Asia/
│       └── China/
│           ├── Beijing/
│           │   ├── README.md   # 游记正文
│           │   ├── tips.md     # 攻略信息
│           │   └── photos/     # 照片（可选）
│           ├── Guangxi/Guilin/
│           └── ...（同层级结构）
├── source/
│   ├── _posts/                 # Hexo 博客文章（非游记内容）
│   ├── travels/                # 自动生成的游记页面（由 sync_travels_to_hexo.py 写入）
│   ├── about/                  # 关于页面
│   ├── planned/                # 待补清单页面
│   └── map/index.md            # 地图页面（layout: map）
├── themes/journey/             # 自定义 Hexo 主题
│   ├── layout/
│   │   ├── layout.ejs          # 页面骨架（导航 + 页脚）
│   │   ├── index.ejs           # 首页（B站嵌入视频 + 最近文章 + 最近更新）
│   │   ├── map.ejs             # 足迹地图（Leaflet + OSM 瓦片）
│   │   ├── page.ejs            # 普通页面 / 攻略页（tips）
│   │   ├── travels-index.ejs   # 足迹总览页（多级目录树 + 层级 icon）
│   │   ├── post.ejs            # 游记详情页（带"返回足迹列表"链接）
│   │   ├── archive.ejs         # 归档（合并 posts + 游记 pages）
│   │   ├── tag.ejs             # 单个标签页（合并 posts + pages）
│   │   ├── tag-index.ejs       # 标签云
│   │   └── ...
│   └── source/css/style.css    # 主题样式
├── tools/
│   ├── sync_travels_to_hexo.py # 自动发现 destinations/ 下所有游记并同步到 source/travels/
│   ├── generate_toc.py         # 生成 README.md 目录树
│   └── README.md               # 工具说明
├── templates/
│   └── place_readme_template.md# 新建地点时参考的 README 模板
├── _config.yml                 # Hexo 站点配置（部署目标 gh-pages）
├── package.json
├── AI_PROJECT_OVERVIEW.md      # 本文档
└── AI_UPDATE_GUIDE.md          # AI 更新指南
```

## 关键文件说明

### `tools/sync_travels_to_hexo.py`

自动扫描 `destinations/` 目录，将每篇 README.md 同步为 `source/travels/{slug}/index.md`（添加 Hexo front-matter）。不再需要手动维护地点列表。

附加行为：

- 任何有自身内容（`tips.md` 或非空 `photos/`）的目录都会生成页面，即使下面还有子地点（如阿坝州）；仅 README 的目录只作层级节点。
- `tips.md` 同步为子页面，正文 `./tips.md` 链接自动替换为 `./tips.html`（GitHub Pages 不解析无扩展名 URL）。
- `photos/` 自动拷贝到 `source/travels/{slug}/photos/`（忽略 `.gitkeep`、`.DS_Store`），源目录删除照片后同步会清理博客侧旧照片。
- 内容未变化时跳过写入，避免文件 mtime 变动导致 `updated_option: mtime` 下的"最近更新"失真。
- 同步结束后自动清理 `source/travels/` 下已无对应地点的残留目录。
- slug 默认取叶子目录名；出现同名地点时，冲突的地点自动改用全路径 slug。
- `COORDS` 支持两种 key：完整相对路径（优先）和叶子目录名（兜底）。

### `tools/generate_toc.py`

生成 README.md 中的目录树（`<!-- TOC:START -->` 到 `<!-- TOC:END -->` 之间）。GitHub Actions 在推送到 `JourneyForTawel` 时自动运行。

### `themes/journey/layout/map.ejs`

全屏足迹地图，使用 Leaflet + OpenStreetMap 瓦片。侧边栏目录树支持展开/折叠，叶子节点点击飞到地图对应位置。

`map.ejs` 是页面片段，由 `layout.ejs` 包裹（对 `layout: map` 页面跳过站点 header/footer，Leaflet CSS 在 layout head 中按需加载）。动态从 `site.pages` 读取 `lat`/`lng` front-matter 生成标记点。新地点需在 `tools/sync_travels_to_hexo.py` 的 `COORDS` 字典中添加坐标（完整相对路径 key 优先，叶子目录名兜底）。

### `themes/journey/layout/travels-index.ejs`

足迹列表页，解析 `page.hierarchy` 生成多级目录树（大洲 → 国家 → 省/州 → 城市 → 地点），带展开/折叠和叶子计数。

## 数据流

```
destinations/Asia/China/Guangxi/Guilin/README.md
  │
  ▼  python3 tools/sync_travels_to_hexo.py
  │
source/travels/guilin/index.md   （添加 front-matter, 替换 ./tips.md → ./tips.html）
source/travels/guilin/tips.md    （同步 tips.md）
source/travels/guilin/photos/    （拷贝照片目录）
  │
  ▼  npx hexo generate
  │
public/travels/guilin/index.html
  │
  ▼  npx hexo deploy
  │
gh-pages branch → GitHub Pages
```

## 配置摘要

| 项目 | 值 |
|------|-----|
| 站点 URL | `https://tawel-tawel.github.io/Journey_to_the_West/` |
| 根路径 | `/Journey_to_the_West/` |
| 主题 | `journey`（自定义 EJS 主题） |
| 部署分支 | `gh-pages` |
| 开发分支 | `JourneyForTawel` |

## 技术栈

- **Hexo 7.3** — 静态站点生成器
- **Leaflet + OpenStreetMap** — 地图
- **EJS** — 模板引擎
- **Python 3** — 同步脚本
