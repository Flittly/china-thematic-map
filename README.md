# China Thematic Map Skill / 中国专题地图制图 Skill

[English](#english) | [中文](#中文)

---

## English

### Overview

This is an **AI Skill** (compatible with Claude Code, Cursor, Codex, and other AI coding assistants) that provides a complete workflow for creating publication-quality thematic maps of China using Python. It includes:

- A ready-to-run example script generating a city-highlighted China map with South China Sea inset and nine-dash line
- Download scripts for Natural Earth basemap and land boundary data
- Comprehensive instructions for the AI assistant on how to handle China map creation, debugging, and refinement

### Project Structure

```
china-thematic-map/
├── SKILL.md              # Skill instructions read by AI assistants
├── README.md             # This file
├── .gitignore            # Ignores data dirs, output images, archives
├── scripts/
│   ├── download_basemap.py          # Download Natural Earth 50m basemap
│   ├── download_land_border.py      # Download 10m land boundary shapefile
│   └── map_cities_with_inset.py     # Main mapping script (example)
├── HYP_50M_SR_W/                    # (downloaded) Basemap raster files
├── ne_10m_admin_0_boundary_lines_land/  # (downloaded) Boundary data
└── china_cities_polygons_map_with_inset.png  # Example output map
```

### Prerequisites

- Python 3.9+
- Required packages:
  - `geopandas`
  - `matplotlib`
  - `numpy`
  - `Pillow`
  - `pyproj`
  - `shapely`
  - `requests`

Install with:

```bash
pip install geopandas matplotlib numpy Pillow pyproj shapely requests
```

### Quick Start

1. **Download basemap and boundary data:**

   ```bash
   python scripts/download_basemap.py
   python scripts/download_land_border.py
   ```

2. **Prepare China administrative shapefiles:**

   You need to obtain the following shapefiles (not included):
   - Province-level boundaries (省级矢量)
   - City-level boundaries (地级市矢量)
   - Land border lines (陆上边界线)
   - Nine-dash line (九段线)

   Popular source: [DataV.GeoAtlas](http://datav.aliyun.com/portal/school/atlas/area_selector) or [National Geomatics Center of China](https://www.webmap.cn/)

3. **Configure data paths:**

   Edit `scripts/map_cities_with_inset.py` and update the path configuration at the top of the file:
   - `PROVINCE_PATH` — path to province shapefile
   - `CITY_PATH` — path to city shapefile
   - `COUNTRY_BORDER_PATH` — path to land border shapefile
   - `NINE_DASH_PATH` — path to nine-dash line shapefile

4. **Generate the map:**

   ```bash
   python scripts/map_cities_with_inset.py
   ```

   The output PNG will be saved as `china_cities_polygons_map_with_inset.png` in the project root.

### Example Output

![Example China Thematic Map](china_cities_polygons_map_with_inset.png)

### How AI Uses This Skill

When installed as a skill, AI assistants will automatically use `SKILL.md` to:

- Understand the proper workflow for China map creation
- Follow best practices for basemap handling, CRS alignment, and layer ordering
- Debug common issues (misaligned layers, missing basemap, white map)
- Modify existing scripts with minimal changes instead of rewriting
- Add South China Sea insets and nine-dash lines correctly

### License

MIT

---

## 中文

### 概述

这是一个 **AI Skill**（兼容 Claude Code、Cursor、Codex 等 AI 编程助手），提供了一套用 Python 绘制出版级中国专题地图的完整工作流。包含：

- 可直接运行的示例脚本：高亮城市 + 南海插图 + 九段线
- Natural Earth 底图和陆上国界线的下载脚本
- 面向 AI 助手的完整制图指导（数据准备、投影处理、样式调整、故障排查）

### 项目结构

```
china-thematic-map/
├── SKILL.md              # AI 助手读取的 Skill 指令
├── README.md             # 本文件
├── .gitignore            # 忽略数据目录、输出图、压缩包
├── scripts/
│   ├── download_basemap.py          # 下载 Natural Earth 50m 全球底图
│   ├── download_land_border.py      # 下载 10m 陆上国界线数据
│   └── map_cities_with_inset.py     # 主绘图脚本（示例）
├── HYP_50M_SR_W/                    # （需下载）底图栅格文件
├── ne_10m_admin_0_boundary_lines_land/  # （需下载）国界线数据
└── china_cities_polygons_map_with_inset.png  # 输出示例地图
```

### 环境要求

- Python 3.9+
- 依赖包：
  - `geopandas`
  - `matplotlib`
  - `numpy`
  - `Pillow`
  - `pyproj`
  - `shapely`
  - `requests`

安装命令：

```bash
pip install geopandas matplotlib numpy Pillow pyproj shapely requests
```

### 快速开始

1. **下载底图和国界线数据：**

   ```bash
   python scripts/download_basemap.py
   python scripts/download_land_border.py
   ```

2. **准备中国行政区划 shapefile：**

   你需要自行获取以下数据（本项目不包含）：
   - 省级行政区矢量
   - 地级市矢量
   - 陆上边界线
   - 九段线

   常用来源：[DataV.GeoAtlas](http://datav.aliyun.com/portal/school/atlas/area_selector) 或 [全国地理信息资源目录服务系统](https://www.webmap.cn/)

3. **配置数据路径：**

   编辑 `scripts/map_cities_with_inset.py`，修改顶部的路径配置：
   - `PROVINCE_PATH` — 省级矢量 shp 路径
   - `CITY_PATH` — 地级市矢量 shp 路径
   - `COUNTRY_BORDER_PATH` — 陆上边界线 shp 路径
   - `NINE_DASH_PATH` — 九段线 shp 路径

4. **生成地图：**

   ```bash
   python scripts/map_cities_with_inset.py
   ```

   输出 PNG 将保存为项目根目录下的 `china_cities_polygons_map_with_inset.png`。

### 示例输出

![示例中国专题地图](china_cities_polygons_map_with_inset.png)

### AI 如何使用此 Skill

作为 Skill 安装后，AI 助手会自动读取 `SKILL.md` 来：

- 理解中国地图制图的正确工作流
- 遵循底图处理、坐标系对齐、图层顺序的最佳实践
- 排查常见问题（图层错位、底图缺失、地图空白）
- 在已有脚本上做最小修改，避免不必要的重写
- 正确处理南海插图和九段线

### 自定义地图

`map_cities_with_inset.py` 顶部的配置区集中了所有可调参数：

- **路径参数**：底图路径、矢量数据路径、输出路径
- **范围参数**：主图经纬度范围、南海插图范围
- **投影参数**：源坐标系、目标坐标系
- **底图扩边参数**：主图和插图的额外裁切边距
- **城市专题参数**：需高亮的城市代码、标签、配色
- **国界线色带参数**：内外层缓冲宽度、颜色、透明度
- **九段线参数**：单侧缓冲宽度、端点延长、方向
- **比例尺和插图参数**：比例尺长度、位置；插图锚点、大小

### 许可

MIT
