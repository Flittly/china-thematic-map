<div align="center">

# China Thematic Map · 中国专题地图制图.skill

<p align="center">
  <img src="china_cities_polygons_map_with_inset.png" alt="China Thematic Map Example" width="720" />
</p>

> *「让 AI 帮你画出每一张中国地图」*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Standard-green)](https://agentskills.io)
[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://python.org)

<br>

**输入一句话，AI 自动生成带南海插图、九段线、城市高亮的中国专题地图。**

<sub>基于开放的 [Agent Skills 协议](https://agentskills.io)，可在 Claude Code、Codex、Cursor、Gemini CLI、OpenCode 等兼容 runtime 中运行。</sub>

<br>

[效果预览](#效果预览) · [安装](#安装) · [使用](#使用) · [工作原理](#工作原理) · [English](#english)

</div>

---

## 效果预览

```
用户      ❯ 帮我画一张中国地图，高亮北京、上海、广州、深圳、成都、武汉，
            加上南海插图和九段线，国界线用紫色渐变。

AI Agent ❯ （自动读取 SKILL.md，检查数据路径，调用 scripts/map_cities_with_inset.py 出图）
          地图已生成 → china_cities_polygons_map_with_inset.png
```

```
用户      ❯ 把九段线的紫色带改细一点，颜色调淡一些。

AI Agent ❯ （定位到 NINE_DASH_INNER_BUFFER 和 BORDER_OUTER_ALPHA 参数，
            只改这两行，不重写整张图）
          已调整九段线样式，重新生成地图。
```

```
用户      ❯ 地图是白的，底图没显示出来。

AI Agent ❯ （按 SKILL.md 中的故障排查清单，依次检查：
            TIFF 路径 → 文件有效性 → 裁切范围 → 重投影链路）
          定位到问题：底图未做重投影。已修复，地图正常显示。
```

这不是简单的脚本执行。AI 在调参、改线宽、换颜色之前，**会先确认坐标系对齐、底图正确加载**——然后才做样式调整。

---

## 安装

### 方式一：告诉 AI Agent 安装（推荐）

打开你正在用的 AI Agent（Claude Code、Codex、Cursor、Gemini CLI、OpenCode 等），告诉它：

```
帮我安装这个 skill：https://github.com/<your-repo>/china-thematic-map
```

### 方式二：手动安装

<details>
<summary>展开查看各 runtime 的 skills 目录</summary>

| Runtime | 安装路径 |
|---|---|
| Claude Code | `~/.claude/skills/china-thematic-map/` |
| Codex CLI | `~/.codex/skills/china-thematic-map/` |
| Cursor | `~/.cursor/skills/china-thematic-map/` |
| Gemini CLI | `~/.gemini/skills/china-thematic-map/` |
| OpenCode | `~/.config/opencode/skills/china-thematic-map/` |
| 其他 runtime | clone 到对应 runtime 的 `skills/` 目录 |

```bash
git clone <repo-url> <上面对应的路径>
```

</details>

### 前置依赖

安装后，需要确保 Python 环境有这些包（AI Agent 出图时会用到）：

```bash
pip install geopandas matplotlib numpy Pillow pyproj shapely requests
```

以及底图和矢量数据（AI Agent 会在需要时引导你下载和配置）。

---

## 使用

装好后，直接用自然语言告诉 AI Agent 你要什么：

```
> 生成一张中国城市分布图，高亮省会城市
> 帮我画一张带南海插图的中国地形图
> 把上次那张图的省界加粗，九段线用红色
> 底图没显示，帮我排查一下
> 把颜色配置改成适合论文投稿的黑白风格
```

AI Agent 会自动读取本 Skill 的 SKILL.md，按照其中的工作流处理你的请求。

**维护已有地图：**

```
> 在 map_cities.py 的基础上，只改比例尺长度
> 把输出改成 600 DPI，文件名不变
> 帮我把主图范围缩小到华北地区
```

## 这个 Skill 能做什么

| 能力 | 说明 |
|---|---|
| **底图处理** | 自动裁切、重投影栅格底图，与矢量层对齐 |
| **行政区边界** | 省界、国界线，支持双色带外侧渐变 |
| **城市高亮** | 按行政区划代码选中城市，自定义填充色 |
| **南海插图** | 独立插图视窗，与主图风格统一 |
| **九段线** | 单侧缓冲色带，端点自动延长 |
| **地图元素** | 经纬网、度标注、指北针、比例尺、图例 |
| **投影变换** | 支持任意 pyproj 坐标系，默认 UTM 49N |
| **增量修改** | 已出图的脚本只改参数区，不重写整张图 |

## 工作原理

AI Agent 读取 SKILL.md 后，按五步工作流执行：

```
1. 输入检查
   ├── 数据路径存在吗？
   ├── 底图可用吗？
   ├── 投影坐标系明确吗？
   └── 缺失信息 → 先问用户再继续

2. 底图准备
   ├── 从 Natural Earth 裁切对应范围
   └── 重投影至目标坐标系（与矢量一致）

3. 矢量投影
   ├── Shapefile → 目标 CRS → 像素坐标
   ├── 国界线外侧色带生成（缓冲 + 差集裁切）
   └── 九段线单侧色带生成（端点延长 + 单侧缓冲）

4. 分层绘制（严格顺序）
   底图 → 经纬网 → 省界 → 国界色带 → 国界核心线
   → 九段线色带 → 九段线 → 城市面 → 城市标注
   → 图例 → 指北针 → 比例尺 → 南海插图

5. 输出
   └── PNG（默认 300 DPI）
```

**关键设计：像素空间统一。** 所有图层在投影后转换到同一个像素网格上叠加——没有 GIS 引擎的渲染差异，底图和矢量永远对齐。

**故障排查优先级：** 路径错误 → 坐标系对齐 → 底图显示 → 插图/九段线 → 样式细节。AI Agent 不会在底图错了的时候去调颜色。

## 仓库结构

```
china-thematic-map/
├── SKILL.md                          # AI Agent 读取的核心指令
├── README.md                         # 本文件
├── china_cities_polygons_map_with_inset.png  # 示例输出图
├── scripts/                              # AI Agent 调用的脚本
│   ├── download_basemap.py               #   下载 Natural Earth 底图
│   ├── download_land_border.py           #   下载陆上国界线数据
│   └── map_cities_with_inset.py          #   完整示例：城市高亮 + 南海插图
├── HYP_50M_SR_W/                         # （需下载）底图缓存
└── ne_10m_admin_0_boundary_lines_land/   # （需下载）国界线缓存
```

`scripts/` 里的 Python 文件由 AI Agent 调用——你不需要手动运行它们。你只需要告诉 AI 你要什么地图，AI 会自行定位到对应脚本和参数。

---

## English

> *"Tell AI what map you want, and it draws it."*

**China Thematic Map** is an [Agent Skill](https://agentskills.io) that enables AI coding assistants to generate publication-quality thematic maps of China. It bundles a complete workflow: basemap downloading, CRS alignment, vector projection, pixel-space rendering, and style configuration — all in a single-script architecture.

### What It Does

- Downloads and caches Natural Earth basemaps and land boundary data
- Projects all layers into a unified pixel space for perfect alignment
- Renders province boundaries, land borders with dual-band purple styling, city polygons, nine-dash line
- Adds graticule, north arrow, scale bar, legend, and South China Sea inset
- Supports incremental edits — tweak parameters, don't rewrite the whole map

### Install

Tell your AI agent: `Install this skill: https://github.com/<repo>/china-thematic-map`

Or manually clone into your runtime's `skills/` directory.

Required Python packages: `geopandas matplotlib numpy Pillow pyproj shapely requests`

### Usage

Talk to your AI agent in natural language:

```
> Draw a China map highlighting Beijing, Shanghai, Guangzhou
> Add a South China Sea inset with nine-dash line
> The basemap is not showing — debug it
> Change the border style to red, keep everything else the same
```

### How It Works

```
Input Check → Basemap Prep → Vector Projection → Layered Rendering → PNG Output
```

All layers share a single pixel coordinate system after projection — no GIS engine rendering gaps. The AI agent follows a strict troubleshooting priority: path errors → CRS alignment → basemap display → inset styling.

### Tech Stack

`geopandas` · `pyproj` · `shapely` · `matplotlib` · `numpy` · `Pillow` · `requests` · EPSG:32649

### License

MIT

---

<div align="center">

**China Thematic Map.skill** — 让每张中国地图都有一致的南海插图、九段线和出版级品质。

<sub>MIT License</sub>

</div>
