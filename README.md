# China Thematic Map Skill / 中国专题地图制图 Skill

[English](#english) | [中文](#中文)

Generate publication-quality thematic maps of China using Python, local shapefiles, and raster basemaps.

使用 Python、本地行政区划 Shapefile 和栅格底图，生成出版级中国专题地图。

![Example output / 示例输出](china_cities_polygons_map_with_inset.png)

---

## English

### What It Produces

A complete map includes:
- Natural Earth basemap (cropped & reprojected to target CRS)
- Province boundaries, land borders with dual-band purple styling
- Highlighted city polygons with color-coded labels
- Graticule with degree annotations on all four edges
- North arrow, scale bar, and legend
- South China Sea inset with nine-dash line (single-sided buffer styling)

### How It Works

All map layers — vector boundaries, city polygons, nine-dash line — are rendered in a unified pixel space after projection, so basemap and overlays always align perfectly.

```
Shapefiles (WGS84)
     │                        Basemap TIFF + World File (WGS84)
     ▼                        ▼
  Project to target CRS     Crop to extent → Reproject to target CRS
     │                        │
     ▼                        ▼
  Convert to pixel coords    Ready as NumPy array
     │                        │
     └────────┬───────────────┘
              ▼
     Draw layers in order on shared pixel canvas
              │
              ▼
         Output PNG
```

**Why pixel space instead of GIS coordinates?** By reprojecting everything into a single pixel grid, every layer shares the exact same coordinate system — no offsets, no resampling gaps.

### Data Checklist

| # | Requirement | Get it |
|---|-------------|--------|
| 1 | Raster basemap (TIFF + TFW) | Run `scripts/download_basemap.py` |
| 2 | Land border shapefile | Run `scripts/download_land_border.py` |
| 3 | China admin shapefiles (province, city, nine-dash) | [DataV.GeoAtlas](http://datav.aliyun.com/portal/school/atlas/area_selector) or [WebMap](https://www.webmap.cn/) |
| 4 | Python environment with GDAL/geopandas | `pip install geopandas matplotlib numpy Pillow pyproj shapely requests` |

### Quick Start

```bash
# 1. Install dependencies
pip install geopandas matplotlib numpy Pillow pyproj shapely requests

# 2. Download basemap and land boundary (outputs to project root)
python scripts/download_basemap.py
python scripts/download_land_border.py

# 3. Edit scripts/map_cities_with_inset.py — set your shapefile paths
#    PROVINCE_PATH, CITY_PATH, COUNTRY_BORDER_PATH, NINE_DASH_PATH

# 4. Generate the map
python scripts/map_cities_with_inset.py
```

### Configuration Reference

All tunable parameters live at the top of `scripts/map_cities_with_inset.py`.

| Section | Parameter | What it controls |
|---------|-----------|------------------|
| **Paths** | `WORKDIR` | Project root (auto-detected) |
| | `BASEMAP_TIF / TFW` | Local basemap files |
| | `PROVINCE_PATH` etc. | Shapefile locations |
| **Extents** | `MAIN_EXTENT_GEO` | Main map bounds `(min_lon, min_lat, max_lon, max_lat)` |
| | `INSET_EXTENT_GEO` | South China Sea inset bounds |
| **CRS** | `SOURCE_CRS` | Input data CRS (default: WGS84) |
| | `TARGET_CRS` | Output projection (default: UTM 49N) |
| **Padding** | `MAIN_BASEMAP_PAD_*` | Extra basemap extent beyond vector bounds (degrees) |
| | `INSET_BASEMAP_PAD_DEG` | Same, for the inset |
| **Cities** | `CITY_CODE_TO_LABEL` | City admin codes and display names |
| | `CITY_COLORS` | Fill color per city |
| **Borders** | `BORDER_OUTER_COLOR / INNER_COLOR` | Purple band colors |
| | `BORDER_OUTER_ALPHA / INNER_ALPHA` | Band transparency (0.3–0.8) |
| | `MAIN_BORDER_INNER_BUFFER / OUTER_BUFFER` | Band widths in pixels |
| **Nine-dash** | `NINE_DASH_INNER_BUFFER / OUTER_BUFFER` | Single-sided buffer widths |
| | `NINE_DASH_SIDE_SIGN` | Which side to buffer (1 or -1) |
| | `NINE_DASH_END_EXTEND` | How much to extend line ends |
| **Layout** | `INSET_AXES_RECT` | Inset position `[left, bottom, width, height]` |
| | `SCALE_BAR_LENGTH_KM` | Scale bar total length |
| | `LON_TICKS / LAT_TICKS` | Graticule intervals |

### Layer Rendering Order

```
Basemap → Graticule → Province boundaries → Border bands → Border core line
→ Nine-dash bands → Nine-dash line → City polygons → City labels
→ Legend → North arrow → Scale bar → South China Sea inset
```

### Basemap Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Entire map white | TIFF path wrong or file missing | Verify `BASEMAP_TIF` exists |
| Map is solid white | Data read as empty array | Check TIFF is valid, not corrupt |
| Basemap offset from vectors | CRS mismatch | Ensure basemap is reprojected, not just cropped |
| Basemap shows wrong area | Crop bounds incorrect | Check `MAIN_EXTENT_GEO` and padding values |
| Some regions pixelated | Resolution too low | Reduce padding to use more of the source TIFF |

### Architecture Decisions

- **No GIS rendering libraries.** Pure matplotlib + numpy. Vector geometries are projected with pyproj/shapely, converted to pixel coordinates, and drawn as matplotlib patches.
- **No online dependencies at runtime.** Once downloaded, everything runs offline.
- **Single script, no framework.** Config at the top, functions below, `main()` at the bottom.

### Anti-Patterns

- Don't style borders before verifying CRS alignment
- Don't use double-sided buffers for nine-dash line
- Don't hardcode layout numbers deep inside functions
- Don't delete the South China Sea inset to "save space"
- Don't regenerate the whole script when only one parameter changed

### Technology Stack

| Component | Library |
|-----------|---------|
| Vector I/O | `geopandas`, `fiona` |
| Coordinate transforms | `pyproj` |
| Geometry operations | `shapely` |
| Raster handling | `PIL` (Pillow), `numpy` |
| Rendering | `matplotlib` |
| Data download | `requests` |
| Target CRS | EPSG:32649 (UTM Zone 49N) |

---

## 中文

### 输出效果

完整地图包含：
- Natural Earth 底图（裁切并重投影至目标坐标系）
- 省界、国界（双色带紫色风格）
- 高亮城市面 + 彩色标签
- 经纬网 + 四边度标注
- 指北针、比例尺、图例
- 南海插图 + 九段线（单侧缓冲紫色色带）

### 运行原理

所有图层（矢量边界、城市面、九段线）在投影后统一转换到像素空间，在同一个像素画布上叠加绘制，确保底图与矢量层完美对齐。

```
Shapefile（WGS84）
     │                        底图 TIFF + 世界文件（WGS84）
     ▼                        ▼
  投影至目标坐标系          按范围裁切 → 重投影至目标坐标系
     │                        │
     ▼                        ▼
  转换为像素坐标             就绪为 NumPy 数组
     │                        │
     └────────┬───────────────┘
              ▼
     按图层顺序在像素画布上绘制
              │
              ▼
          输出 PNG
```

**为什么用像素空间而非 GIS 坐标？** 将一切重投影到统一像素网格后，每一层共用完全相同的坐标系统——无偏移、无重采样间隙。

### 数据准备清单

| # | 所需数据 | 获取方式 |
|---|---------|---------|
| 1 | 栅格底图（TIFF + TFW） | 运行 `scripts/download_basemap.py` |
| 2 | 陆上国界线 Shapefile | 运行 `scripts/download_land_border.py` |
| 3 | 中国行政区划数据（省/市/九段线） | [DataV.GeoAtlas](http://datav.aliyun.com/portal/school/atlas/area_selector) 或 [天地图](https://www.webmap.cn/) |
| 4 | Python 环境（GDAL/geopandas） | `pip install geopandas matplotlib numpy Pillow pyproj shapely requests` |

### 快速开始

```bash
# 1. 安装依赖
pip install geopandas matplotlib numpy Pillow pyproj shapely requests

# 2. 下载底图和国界线数据（输出到项目根目录）
python scripts/download_basemap.py
python scripts/download_land_border.py

# 3. 编辑 scripts/map_cities_with_inset.py，配置你的 Shapefile 路径
#    PROVINCE_PATH、CITY_PATH、COUNTRY_BORDER_PATH、NINE_DASH_PATH

# 4. 生成地图
python scripts/map_cities_with_inset.py
```

### 配置参数参考

所有可调参数集中在 `scripts/map_cities_with_inset.py` 顶部。

| 分类 | 参数 | 控制内容 |
|------|------|---------|
| **路径** | `WORKDIR` | 项目根目录（自动检测） |
| | `BASEMAP_TIF / TFW` | 本地底图文件 |
| | `PROVINCE_PATH` 等 | Shapefile 所在位置 |
| **范围** | `MAIN_EXTENT_GEO` | 主图经纬度范围 `(最小经度, 最小纬度, 最大经度, 最大纬度)` |
| | `INSET_EXTENT_GEO` | 南海插图范围 |
| **坐标系** | `SOURCE_CRS` | 源数据坐标系（默认 WGS84） |
| | `TARGET_CRS` | 目标投影（默认 UTM 49N） |
| **扩边** | `MAIN_BASEMAP_PAD_*` | 底图超出矢量范围的额外边距（度） |
| | `INSET_BASEMAP_PAD_DEG` | 插图的对应参数 |
| **城市** | `CITY_CODE_TO_LABEL` | 城市行政区划代码与显示名称 |
| | `CITY_COLORS` | 每个城市的填充色 |
| **国界** | `BORDER_OUTER_COLOR / INNER_COLOR` | 紫色色带颜色 |
| | `BORDER_OUTER_ALPHA / INNER_ALPHA` | 色带透明度（0.3–0.8） |
| | `MAIN_BORDER_INNER_BUFFER / OUTER_BUFFER` | 色带像素宽度 |
| **九段线** | `NINE_DASH_INNER_BUFFER / OUTER_BUFFER` | 单侧缓冲宽度 |
| | `NINE_DASH_SIDE_SIGN` | 缓冲方向（1 或 -1） |
| | `NINE_DASH_END_EXTEND` | 端点延长像素数 |
| **布局** | `INSET_AXES_RECT` | 插图位置 `[左, 下, 宽, 高]` |
| | `SCALE_BAR_LENGTH_KM` | 比例尺总长度 |
| | `LON_TICKS / LAT_TICKS` | 经纬网间隔 |

### 图层绘制顺序

```
底图 → 经纬网 → 省界 → 国界色带 → 国界核心线
→ 九段线色带 → 九段线 → 城市面 → 城市标注
→ 图例 → 指北针 → 比例尺 → 南海插图
```

### 底图故障排查

| 症状 | 可能原因 | 修复方法 |
|------|---------|---------|
| 整张图白色 | TIFF 路径错误或文件不存在 | 检查 `BASEMAP_TIF` 是否存在 |
| 地图纯白色 | 数据读入为空数组 | 检查 TIFF 是否有效、未损坏 |
| 底图与矢量偏移 | 坐标系不一致 | 确保底图做了重投影，而非仅仅裁切 |
| 底图显示区域不对 | 裁切范围错误 | 检查 `MAIN_EXTENT_GEO` 和扩边值 |
| 部分区域像素化 | 分辨率过低 | 减小扩边值以利用更多原始 TIFF 像素 |

### 架构决策

- **不使用 GIS 渲染库。** 纯 matplotlib + numpy 实现。矢量几何通过 pyproj/shapely 投影，转为像素坐标后用 matplotlib patches 绘制。
- **运行时无在线依赖。** 底图和 Shapefile 下载完成后，脚本完全离线运行。
- **单文件，无框架。** 顶部配置、中间函数、底部 `main()`，无类继承、无插件体系。

### 应避免的操作

- 不要在确认坐标系对齐前调整边界样式
- 不要对九段线使用双侧缓冲
- 不要把布局数字硬编码在函数内部
- 不要为了"省空间"删掉南海插图
- 不要因为只改了一个参数就重写整张图

### 技术栈

| 组件 | 库 |
|------|----|
| 矢量读写 | `geopandas`, `fiona` |
| 坐标转换 | `pyproj` |
| 几何运算 | `shapely` |
| 栅格处理 | `PIL` (Pillow), `numpy` |
| 渲染 | `matplotlib` |
| 数据下载 | `requests` |
| 目标投影 | EPSG:32649（UTM 第 49 带，适合中国范围） |
