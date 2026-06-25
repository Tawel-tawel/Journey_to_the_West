# AI 更新指南 — 如何维护旅行记录

> 给 AI 辅助工具的指令：按此流程添加、更新旅行记录。

## 一、添加新地点

### 目录结构

在 `destinations/` 下按层级创建目录：

```
destinations/
└── {大洲}/
    └── {国家}/
        └── {省份或州}/
            └── {城市或具体地点}/
                ├── README.md       # 游记正文
                ├── tips.md         # 攻略信息
                └── photos/         # 照片（可选）
```

**命名规则**：
- 目录名用英文或拼音，`_` 代替空格（例如 `Kuanzhai_Alley`、`Jilin_City`）
- `photos/` 目录如果为空，可以不创建或保留 `.gitkeep`

**示例**：添加日本东京的游记

```
destinations/Asia/Japan/Tokyo/Tokyo/README.md
destinations/Asia/Japan/Tokyo/Tokyo/tips.md
```

### 目录层级要求

| 层级 | 说明 | 示例 |
|------|------|------|
| 大洲 | 必须，顶级目录 | `Asia`, `Europe` |
| 国家 | 必须 | `China`, `Japan` |
| 省份/州 | 可选（如国家没有省份则跳过） | `Guangxi`, `California` |
| 城市/地区 | 如果具体地点在城市内则必填 | `Chengdu`, `Tokyo` |
| 具体地点 | 最终目的地目录，含 README.md | `Jinli`, `Disneyland` |

如果省份名和地点名相同（如北京既是直辖市又是目的地），目录结构为：

```
destinations/Asia/China/Beijing/Beijing/README.md
```

如果地点直接在城市下（如成都的锦里）：

```
destinations/Asia/China/Sichuan/Chengdu/Jinli/README.md
```

### 坐标（用于地图）

在 `tools/sync_travels_to_hexo.py` 的 `COORDS` 字典中添加坐标，格式为 `"目录名": (纬度, 经度)`。

### 游记内容（README.md）

第一行用 `# 标题` 作为一级标题（脚本会自动去掉这行，用 front-matter 的 title 替代）。

可以在正文中使用 `./tips.md` 链接到攻略页（脚本会自动替换为 `./tips`）。

### 攻略内容（tips.md）

可选。如果存在，会被同步到博客的 `tips` 子页面。

## 二、更新已有地点

直接修改 `destinations/` 下对应目录的 `README.md` 或 `tips.md`。

## 三、更新后必须执行的步骤

### 1. 同步到 Hexo

```bash
python3 tools/sync_travels_to_hexo.py
```

### 2. 更新 README 目录树

```bash
python3 tools/generate_toc.py
```

### 3. 验证 Hexo 生成

```bash
npx hexo clean && npx hexo generate
```

确认输出没有错误（`ERROR` 级别日志），文件数量合理。

### 4. 更新 docs/world_map.md

如果添加了新的目的地，在 `docs/world_map.md` 的「当前足迹」列表中添加链接。

格式：
```markdown
- [亚洲 / 中国 / 广西 / 桂林](../destinations/Asia/China/Guangxi/Guilin/)
```

### 5. 检查事项清单

- [ ] `sync_travels_to_hexo.py` 无报错
- [ ] `hexo generate` 无报错
- [ ] 新页面在 `source/travels/{slug}/index.md` 中生成
- [ ] tips.md 已同步（如果存在）
- [ ] README.md 的 TOC 已更新
- [ ] `docs/world_map.md` 已添加新链接
- [ ] 游记内容中有 `./tips.md` 链接的都被替换为 `./tips`
- [ ] `tools/sync_travels_to_hexo.py` 的 `COORDS` 字典已添加新地点的坐标**

> ** 地图坐标存在 `tools/sync_travels_to_hexo.py` 的 `COORDS` 字典中，添加新地点后记得在这里添加坐标 `"Slug": (lat, lng)`。

## 四、部署上线

```bash
# 推送到开发分支
git add -A
git commit -m "feat: 添加 {地点名称} 游记"
git push origin JourneyForTawel

# 构建并部署到 gh-pages
npx hexo clean && npx hexo deploy
```

## 五、注意事项

1. **不要手动编辑 `source/travels/`** 下的文件——它们由 `sync_travels_to_hexo.py` 自动生成，会被覆盖。
2. 不要修改 `_config.yml` 中的 `root: /Journey_to_the_West/`。
3. 不要修改 `.github/workflows/` 中的 GitHub Actions。
4. 照片放在 `photos/` 目录中，正文用 Markdown 图片语法引用（`![描述](./photos/01.jpg)`）。
5. 所有 Python 脚本在 `tools/` 目录下运行（以根目录为 `..`）。
