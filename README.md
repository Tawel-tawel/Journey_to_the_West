# Journey to the West

> 用脚步丈量世界，用 Git 管理记忆。  
> 按 **大洲 → 国家 → 省/州 → 城市 → 地点** 的层级整理游记、攻略、影像和旅行清单。

## 导航

- [足迹地图](./docs/world_map.md)
- [亚洲](./Asia/)
- [地点 README 模板](./templates/place_readme_template.md)
- [Hexo 博客内容](./source/)
- [脚本工具](./tools/)

## Hexo 博客

这个仓库现在同时是一个 Hexo 博客项目：

- `Asia/`：原始旅行资料库，按大洲、国家、省市、地点保存 `README.md`、`tips.md` 和照片。
- `source/`：Hexo 站点内容，用于生成网页。
- `themes/journey/`：仓库自带的轻量主题，先保证能本地预览和部署，后续可以再换更漂亮的主题。
- `scaffolds/`：Hexo 新建文章和页面时使用的模板。

### 本地预览

```bash
npm install
npm run server
```

然后访问 `http://localhost:4000/Journey_to_the_West/`。

### 生成静态网页

```bash
npm run build
```

生成结果会放在 `public/`，该目录不会提交到源码分支。

### 部署到 GitHub Pages

当前 `_config.yml` 的部署目标是：

```yaml
deploy:
  type: git
  repo: https://github.com/Tawel-tawel/Journey_to_the_West.git
  branch: gh-pages
```

执行：

```bash
npm run deploy
```

这会生成静态页面并推送到 `gh-pages` 分支。GitHub 仓库的 Pages 设置里需要选择 `gh-pages` 分支作为发布来源。

## 当前存档

这个仓库记录了本人去过的地方及配套攻略。之所以写在 GitHub 上，是因为某些平台（如小红书）会删评论…… 以下是目录结构：

<!-- TOC:START -->
- [Asia](./Asia/)
  - [China](./Asia/China/)
    - [Beijing](./Asia/China/Beijing/)
    - [Guangxi](./Asia/China/Guangxi/)
      - [Guilin](./Asia/China/Guangxi/Guilin/)
      - [Liuzhou](./Asia/China/Guangxi/Liuzhou/)
    - [Hainan](./Asia/China/Hainan/)
      - [Haikou](./Asia/China/Hainan/Haikou/)
    - [Jilin](./Asia/China/Jilin/)
      - [Changchun](./Asia/China/Jilin/Changchun/)
      - [Jilin City](./Asia/China/Jilin/Jilin_City/)
      - [Songyuan](./Asia/China/Jilin/Songyuan/)
    - [Sichuan](./Asia/China/Sichuan/)
      - [Aba](./Asia/China/Sichuan/Aba/)
        - [Jiuzhaigou](./Asia/China/Sichuan/Aba/Jiuzhaigou/)
      - [Chengdu](./Asia/China/Sichuan/Chengdu/)
        - [Jinli](./Asia/China/Sichuan/Chengdu/Jinli/)
        - [Kuanzhai Alley](./Asia/China/Sichuan/Chengdu/Kuanzhai_Alley/)
<!-- TOC:END -->

## 计划补充

以下地点已经去过，但尚未整理成完整游记（sad）。后续补充时，将从 [地点 README 模板](./templates/place_readme_template.md) 复制结构，再添加照片和攻略。

| 地区 | 地点 | 当前状态 |
| --- | --- | --- |
| 广西 | 桂林 | 已建档，待补游记和攻略 |
| 广西 | 柳州 | 已建档，待补游记和攻略 |
| 海南 | 海口 | 已建档，待补游记和攻略 |
| 四川 | 成都 | 已建档，待补更多地点和细节 |
| 四川 | 阿坝州 / 九寨沟 | 已建档，待补游记和攻略 |
| 北京 | 北京 | 已建档，待补游记和攻略 |
| 吉林 | 长春 | 已建档，待补游记和攻略 |
| 吉林 | 松原 | 已建档，待补游记和攻略 |
| 吉林 | 吉林市 | 已建档，待补游记和攻略 |

## 编写规范

- 文件夹路径使用英文或拼音，避免中文字符在部分工具中产生乱码。
- 内部的 README 和攻略正文可以使用中文。
- 目录层级建议遵循：`大洲/国家/省或州/城市或地区/具体地点/`。
- 每个地点建议包含以下内容：
  - `README.md`：像美篇一样展示地点介绍、行程流程、照片、时间线、路线、预算和旅途故事。
  - `tips.md`：单独整理攻略信息，包括交通、住宿、美食、避坑建议、开放时间、预约方式等。
  - `photos/`：存放原始照片或压缩后的展示照片。
- 新建地点时，可以先复制 [templates/place_readme_template.md](./templates/place_readme_template.md)，然后根据实际旅行经历替换内容。

## 本地使用

```bash
git clone https://github.com/Tawel-tawel/Journey_to_the_West.git
cd Journey_to_the_West
python3 tools/generate_toc.py
npm install
npm run server
```

建议使用 VS Code + Markdown Preview Enhanced 进行阅读和整理。

## 照片许可协议

照片默认为本人原创内容。如需公开发布，建议采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 协议：署名、非商业使用。

代码与脚本遵循仓库根目录的 [LICENSE](./LICENSE) 文件。
