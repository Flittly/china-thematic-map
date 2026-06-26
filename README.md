# China Thematic Map Skill

Generate publication-quality thematic maps of China using Python, local shapefiles, and raster basemaps.

All map layers — vector boundaries, city polygons, nine-dash line — are rendered in a unified pixel space after projection, so basemap and overlays always align perfectly.

## What It Produces

![Example output](china_cities_polygons_map_with_inset.png)

A complete map includes:
- Natural Earth basemap (cropped & reprojected to target CRS)
- Province boundaries, land borders with dual-band purple styling
- Highlighted city polygons with color-coded labels
- Graticule with degree annotations on all four edges
- North arrow, scale bar, and legend
- South China Sea inset with nine-dash line (single-sided buffer styling)

## How It Works

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

**Key insight:** The basemap and all vector layers are projected to the *same target CRS* (default: UTM 49N, EPSG:32649), then converted to pixel coordinates on a single image canvas. This eliminates the common "misaligned layers" problem entirely.

**Why pixel space instead of GIS coordinates?**
Conventional GIS mapping tools render layers in geographic or projected space, which leads to subtle misalignments when combining raster and vector sources. By reprojecting everything into a single pixel grid, every layer shares the exact same coordinate system — no offsets, no resampling gaps.

## Before Using — Data Checklist

The skill needs four things to work. Without these, generating a correct map is impossible:

| # | Requirement | Get it |
|---|-------------|--------|
| 1 | Raster basemap (TIFF + TFW) | Run `scripts/download_basemap.py` |
| 2 | Land border shapefile | Run `scripts/download_land_border.py` |
| 3 | China admin shapefiles (province, city, nine-dash) | [DataV.GeoAtlas](http://datav.aliyun.com/portal/school/atlas/area_selector) or [WebMap](https://www.webmap.cn/) |
| 4 | GDAL/geopandas environment | `pip install geopandas matplotlib numpy Pillow pyproj shapely requests` |

## Quick Start

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

## Configuration Reference

All tunable parameters live at the top of `scripts/map_cities_with_inset.py`. Modify them directly — no config files needed.

### Core Parameters

| Section | Parameter | What it controls |
|---------|-----------|------------------|
| **Paths** | `WORKDIR` | Project root (auto-detected from script location) |
| | `BASEMAP_TIF / TFW` | Local basemap files |
| | `PROVINCE_PATH` etc. | Shapefile locations |
| **Extents** | `MAIN_EXTENT_GEO` | Main map lat/lon bounds `(min_lon, min_lat, max_lon, max_lat)` |
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
| | `NINE_DASH_END_EXTEND` | How much to extend line ends to match black core |
| **Layout** | `INSET_AXES_RECT` | Inset position `[left, bottom, width, height]` |
| | `SCALE_BAR_LENGTH_KM` | Scale bar total length |
| | `LON_TICKS / LAT_TICKS` | Graticule intervals |

## How the AI Assistant Uses This Skill

When you ask an AI coding assistant to make a China map, it reads `SKILL.md` and follows a specific workflow:

### 1. Input Validation (always first)
Before writing any code, the assistant checks:
- Do shapefile paths exist?
- Is the basemap available?
- Are map extents specified?
- Is the target CRS known?

If information is missing, it asks you before proceeding — no blind code generation.

### 2. Maintenance Mode (existing scripts)
If you already have a working script and just want a tweak, the assistant:
- Modifies only the relevant parameter or function
- Preserves your file name, output name, and script structure
- Never rewrites the whole map for a one-line change

### 3. Layer Rendering Order
```
Basemap → Graticule → Province boundaries → Border bands → Border core line
→ Nine-dash bands → Nine-dash line → City polygons → City labels
→ Legend → North arrow → Scale bar → South China Sea inset
```

### 4. Troubleshooting Priority
When something is wrong, fixes are applied in this exact order:
1. File path errors
2. CRS / projection misalignment
3. Missing basemap
4. Missing inset / nine-dash line
5. Styling / cosmetic issues

## Basemap Troubleshooting

If the map appears blank, white, or misaligned:

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Entire map white | TIFF path wrong or file missing | Verify `BASEMAP_TIF` exists |
| Map is solid white | Data read as empty array | Check TIFF is valid, not corrupt |
| Basemap offset from vectors | CRS mismatch | Ensure basemap is reprojected, not just cropped |
| Basemap shows wrong area | Crop bounds incorrect | Check `MAIN_EXTENT_GEO` and padding values |
| Some regions pixelated | Resolution too low | Reduce padding to use more of the source TIFF |

## Architecture Decisions

**No GIS rendering libraries.** The map uses pure matplotlib + numpy. Vector geometries are projected with pyproj/shapely, converted to pixel coordinates, and drawn as matplotlib patches. This gives full control over every pixel without fighting a GIS engine's rendering pipeline.

**No online dependencies at runtime.** Once basemap and shapefiles are downloaded, the script runs entirely offline. No tile servers, no API keys.

**Single script, no framework.** Everything is in one file. Config at the top, functions below, `main()` at the bottom. No class hierarchies, no plugin systems. This makes it trivial for users to modify.

## Anti-Patterns (Avoid)

- Don't style borders before verifying CRS alignment
- Don't use double-sided buffers for nine-dash line (it wraps around, not outward)
- Don't hardcode layout numbers deep inside functions — put them in the config block
- Don't delete the South China Sea inset to "save space"
- Don't regenerate the whole script when only one parameter changed
- Don't write a new output filename when the user has an existing one

## Technology Stack

| Component | Library |
|-----------|---------|
| Vector I/O | `geopandas`, `fiona` |
| Coordinate transforms | `pyproj` |
| Geometry operations | `shapely` |
| Raster handling | `PIL` (Pillow), `numpy` |
| Rendering | `matplotlib` |
| Data download | `requests` |
| Target CRS | EPSG:32649 (UTM Zone 49N, suitable for China) |
