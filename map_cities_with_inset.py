from pathlib import Path

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MplPath
from pyproj import Transformer
from shapely.geometry import LineString, box
from shapely.ops import transform


matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False


# ====================
# 配置区
# ====================

# 工作目录与底图文件。
WORKDIR = Path(r"E:\Self\Work\hrs")
BASEMAP_DIR = WORKDIR / "HYP_50M_SR_W"
BASEMAP_TIF = BASEMAP_DIR / "HYP_50M_SR_W.tif"
BASEMAP_TFW = BASEMAP_DIR / "HYP_50M_SR_W.tfw"

# 数据路径。
PROVINCE_PATH = Path(
    r"E:\Self\资源\中国省市县2022年初行政区划数据\中国省市县2022年初行政区划数据\2022省级\2022省矢量.shp"
)
COUNTRY_BORDER_PATH = Path(
    r"E:\Self\资源\中国省市县2022年初行政区划数据\中国省市县2022年初行政区划数据\国界陆上边界线\中国陆上边界线.shp"
)
CITY_PATH = Path(
    r"E:\Self\资源\中国省市县2022年初行政区划数据\中国省市县2022年初行政区划数据\2022地级\2022市矢量.shp"
)
NINE_DASH_PATH = Path(
    r"E:\Self\资源\中国省市县2022年初行政区划数据\中国省市县2022年初行政区划数据\九段线\九段线.shp"
)

# 坐标系：源数据用经纬度，最终出图用 UTM 49N。
SOURCE_CRS = "EPSG:4326"
TARGET_CRS = "EPSG:32649"

# 主图和南海插图的经纬度范围。
MAIN_EXTENT_GEO = (80, 16, 136, 51)
INSET_EXTENT_GEO = (105.5, 2.5, 124.5, 25.5)

# 主图底图扩边。
# 这些参数只影响底图额外裁多少，不直接改变矢量范围。
MAIN_BASEMAP_PAD_LEFT_DEG = 14.8
MAIN_BASEMAP_PAD_RIGHT_DEG = 14.0
MAIN_BASEMAP_PAD_BOTTOM_DEG = 4.5
MAIN_BASEMAP_PAD_TOP_DEG = 4.5

# 南海插图底图扩边。
INSET_BASEMAP_PAD_DEG = 2.8

# 需要高亮的城市。
CITY_CODE_TO_LABEL = {
    110000: "Beijing",
    310000: "Shanghai",
    420100: "Wuhan",
    440100: "Guangzhou",
    440300: "Shenzhen",
    510100: "Chengdu",
    610100: "Xi'an",
    620100: "Lanzhou",
}

# 城市填色。
CITY_COLORS = {
    "Beijing": "#ff1493",
    "Shanghai": "#ffd700",
    "Wuhan": "#0057ff",
    "Guangzhou": "#ff7f00",
    "Shenzhen": "#00c853",
    "Chengdu": "#ff1744",
    "Xi'an": "#00b8ff",
    "Lanzhou": "#aa00ff",
}

# 比例尺参数。
SCALE_BAR_LENGTH_KM = 600
SCALE_BAR_LOCATION = (0.18, 0.05)
SCALE_BAR_SEGMENTS = 3

# 南海插图位置：[left, bottom, width, height]。
INSET_AXES_RECT = [0.720, 0.135, 0.30, 0.30]

# 经纬网参数。
LON_TICKS = list(range(75, 136, 10))
LAT_TICKS = list(range(20, 56, 5))
GRATICULE_LON_PAD = 15
GRATICULE_LAT_PAD = 15

# 国界线与九段线紫色色带参数。
BORDER_OUTER_COLOR = "#caa4ff"
BORDER_INNER_COLOR = "#6a0dad"

# BORDER_OUTER_ALPHA: 外层浅紫色带透明度。
# - 值越大：浅紫色越实、越显眼。
# - 值越小：浅紫色越淡、越透明。
# 一般建议范围：0.3 ~ 0.8。
BORDER_OUTER_ALPHA = 0.6

# BORDER_INNER_ALPHA: 内层深紫色带透明度。
# - 值越大：深紫色越明显，国界线的层次感越强。
# - 值越小：深紫色越柔和。
# 通常内层可以比外层稍微更实一点。
BORDER_INNER_ALPHA = 0.7

# MAIN_BORDER_INNER_BUFFER: 主图里“内层深紫色带”的宽度，单位是像素。
# - 值越大：主图国界线深紫色带越宽。
# - 值越小：主图国界线深紫色带越窄。
# 这个参数影响主图中国陆上边界线靠近黑色核心线的那一层。
MAIN_BORDER_INNER_BUFFER = 8

# MAIN_BORDER_OUTER_BUFFER: 主图里“外层浅紫色带”的宽度，单位是像素。
# - 值越大：主图国界线浅紫色带越宽，外扩感越明显。
# - 值越小：主图国界线浅紫色带越窄。
# 通常这个值应该大于 MAIN_BORDER_INNER_BUFFER。
MAIN_BORDER_OUTER_BUFFER = 16

# INSET_BORDER_INNER_BUFFER: 南海插图里陆上边界线的深紫色带宽度，单位是像素。
# - 值越大：南海插图里边界线的深紫色带越粗。
# - 值越小：深紫色带越细。
# 一般会比主图的值略小，因为南海插图尺寸更小。
INSET_BORDER_INNER_BUFFER = 8

# INSET_BORDER_OUTER_BUFFER: 南海插图里陆上边界线的浅紫色带宽度，单位是像素。
# - 值越大：南海插图里浅紫色带越宽。
# - 值越小：浅紫色带越窄。
# 通常这个值也应该大于 INSET_BORDER_INNER_BUFFER。
INSET_BORDER_OUTER_BUFFER = 16

# NINE_DASH_INNER_BUFFER: 南海插图里九段线“内层深紫色带”宽度，单位是像素。
# - 值越大：九段线深紫色带越宽。
# - 值越小：九段线深紫色带越窄。
NINE_DASH_INNER_BUFFER = 8.0

# NINE_DASH_OUTER_BUFFER: 南海插图里九段线“外层浅紫色带”宽度，单位是像素。
# - 值越大：九段线浅紫色带越宽，外扩更明显。
# - 值越小：浅紫色带越窄。
# 通常这个值应该大于 NINE_DASH_INNER_BUFFER。
NINE_DASH_OUTER_BUFFER = 16.0

# NINE_DASH_SIDE_SIGN: 九段线单侧缓冲方向。
# 这个值决定紫色色带出现在九段线哪一侧。
# - 1  : 朝一个方向扩
# - -1 : 朝相反方向扩
# 如果你发现九段线色带跑到了不想要的一边，通常只需要把 1 改成 -1，
# 或把 -1 改成 1。
NINE_DASH_SIDE_SIGN = 1

# NINE_DASH_END_EXTEND: 九段线端点延长长度，单位是像素。
# 因为九段线的紫色色带是通过单侧缓冲生成的，默认会在端头看起来比黑色线短。
# 这个参数就是在做缓冲前，先把每段九段线的两端往外延长一点。
# - 值越大：紫色色带在两端会更长，更接近黑色线长度。
# - 值越小：紫色色带端头更容易显得短一截。
NINE_DASH_END_EXTEND = 6.0

# 输出文件。
OUTPUT_PATH = WORKDIR / "china_cities_polygons_map_with_inset.png"


def read_worldfile(path: Path) -> dict:
    """读取世界文件（.tfw）。

    世界文件记录了 TIFF 栅格的像元大小和左上角坐标。
    这里后续会用它把全球底图裁成主图或插图需要的范围。
    """
    values = [
        float(line.strip()) for line in path.read_text(encoding="utf-8").splitlines()
    ]
    return {
        "pixel_x": values[0],
        "pixel_y": values[3],
        "x_center": values[4],
        "y_center": values[5],
    }


def pad_bounds(bounds, pad):
    """按相同数值向四周扩边。"""
    return (bounds[0] - pad, bounds[1] - pad, bounds[2] + pad, bounds[3] + pad)


def pad_bounds_asymmetric(bounds, left, bottom, right, top):
    """按四个方向分别扩边。

    用于主图底图裁切时单独控制左、右、上、下留白。
    """
    return (bounds[0] - left, bounds[1] - bottom, bounds[2] + right, bounds[3] + top)


def crop_basemap(bounds_geo):
    """先在经纬度空间裁切全球底图。

    返回值：
    1. 裁出来的 RGB 图像数组
    2. 裁切后图像对应的经纬度边界
    """
    meta = read_worldfile(BASEMAP_TFW)
    arr = np.array(Image.open(BASEMAP_TIF).convert("RGB"))
    height, width = arr.shape[:2]

    pixel_x = meta["pixel_x"]
    pixel_y = meta["pixel_y"]
    x_min = meta["x_center"] - pixel_x / 2
    y_max = meta["y_center"] - pixel_y / 2

    left = max(0, int(round((bounds_geo[0] - x_min) / pixel_x)))
    right = min(width, int(round((bounds_geo[2] - x_min) / pixel_x)))
    top = max(0, int(round((y_max - bounds_geo[3]) / abs(pixel_y))))
    bottom = min(height, int(round((y_max - bounds_geo[1]) / abs(pixel_y))))

    cropped_bounds = (
        x_min + left * pixel_x,
        y_max - bottom * abs(pixel_y),
        x_min + right * pixel_x,
        y_max - top * abs(pixel_y),
    )
    return arr[top:bottom, left:right], cropped_bounds


def project_bounds(bounds_geo, transformer):
    """将经纬度矩形范围投影到目标投影坐标系中。"""
    xs = [bounds_geo[0], bounds_geo[0], bounds_geo[2], bounds_geo[2]]
    ys = [bounds_geo[1], bounds_geo[3], bounds_geo[1], bounds_geo[3]]
    tx, ty = transformer.transform(xs, ys)
    return min(tx), min(ty), max(tx), max(ty)


def reproject_basemap_to_target(
    src_arr, src_bounds_geo, dst_bounds_proj, inv_transformer
):
    """将经纬度栅格重采样到目标投影网格。

    这里不用 GIS 栅格库，而是用像元中心反查经纬度方式做一个近似重投影。
    这样底图和已经投影后的矢量层才能对齐。
    """
    src_h, src_w = src_arr.shape[:2]
    src_minx, src_miny, src_maxx, src_maxy = src_bounds_geo
    dst_minx, dst_miny, dst_maxx, dst_maxy = dst_bounds_proj

    dst_w = src_w
    aspect = (dst_maxy - dst_miny) / max(dst_maxx - dst_minx, 1e-9)
    dst_h = max(1, int(round(dst_w * aspect)))

    xs = (
        np.linspace(dst_minx, dst_maxx, dst_w, endpoint=False)
        + (dst_maxx - dst_minx) / dst_w / 2
    )
    ys = (
        np.linspace(dst_maxy, dst_miny, dst_h, endpoint=False)
        - (dst_maxy - dst_miny) / dst_h / 2
    )
    grid_x, grid_y = np.meshgrid(xs, ys)
    lon, lat = inv_transformer.transform(grid_x, grid_y)

    src_px = ((lon - src_minx) / (src_maxx - src_minx) * src_w).astype(int)
    src_py = ((src_maxy - lat) / (src_maxy - src_miny) * src_h).astype(int)

    valid = (src_px >= 0) & (src_px < src_w) & (src_py >= 0) & (src_py < src_h)
    dst = np.full((dst_h, dst_w, 3), 255, dtype=np.uint8)
    dst[valid] = src_arr[src_py[valid], src_px[valid]]
    return dst


def geometry_to_pixel_gdf(gdf, bounds_proj, image_shape):
    """把投影坐标下的几何映射到像素坐标空间。

    这样矢量层就能和已经重投影好的栅格底图在同一画布坐标下绘制。
    """
    height, width = image_shape[:2]
    minx, miny, maxx, maxy = bounds_proj

    def project(x, y, z=None):
        xp = (np.asarray(x) - minx) / (maxx - minx) * width
        yp = (maxy - np.asarray(y)) / (maxy - miny) * height
        return xp, yp

    projected = gdf.copy()
    projected["geometry"] = projected.geometry.apply(
        lambda geom: transform(project, geom)
    )
    return projected


def projected_point_to_pixel(x, y, bounds_proj, image_shape):
    """将投影坐标点换算成像素坐标点。"""
    height, width = image_shape[:2]
    minx, miny, maxx, maxy = bounds_proj
    xp = (np.asarray(x) - minx) / (maxx - minx) * width
    yp = (maxy - np.asarray(y)) / (maxy - miny) * height
    return xp, yp


def draw_polygon_geometry(ax, geometry, facecolor, edgecolor, linewidth, alpha, zorder):
    """绘制面对象，支持带内洞的 Polygon / MultiPolygon。"""
    if geometry.is_empty:
        return
    if geometry.geom_type == "Polygon":
        vertices = []
        codes = []

        exterior = np.asarray(geometry.exterior.coords)
        vertices.extend(exterior.tolist())
        codes.extend(
            [MplPath.MOVETO]
            + [MplPath.LINETO] * (len(exterior) - 2)
            + [MplPath.CLOSEPOLY]
        )

        for interior in geometry.interiors:
            ring = np.asarray(interior.coords)
            vertices.extend(ring.tolist())
            codes.extend(
                [MplPath.MOVETO]
                + [MplPath.LINETO] * (len(ring) - 2)
                + [MplPath.CLOSEPOLY]
            )

        ax.add_patch(
            PathPatch(
                MplPath(vertices, codes),
                facecolor=facecolor,
                edgecolor=edgecolor,
                linewidth=linewidth,
                alpha=alpha,
                joinstyle="round",
                fill=True,
                zorder=zorder,
            )
        )
    elif geometry.geom_type == "MultiPolygon":
        for part in geometry.geoms:
            draw_polygon_geometry(
                ax, part, facecolor, edgecolor, linewidth, alpha, zorder
            )


def draw_line_geometry(ax, geometry, color, linewidth, zorder):
    """绘制线对象，支持 LineString / MultiLineString。"""
    if geometry.is_empty:
        return
    if geometry.geom_type == "LineString":
        coords = np.asarray(geometry.coords)
        ax.plot(
            coords[:, 0], coords[:, 1], color=color, linewidth=linewidth, zorder=zorder
        )
    elif geometry.geom_type == "MultiLineString":
        for part in geometry.geoms:
            draw_line_geometry(ax, part, color, linewidth, zorder)


def draw_boundary_gdf(ax, gdf, color, linewidth, zorder):
    """绘制 GeoDataFrame 中每个面对象的边界线。"""
    for geom in gdf.geometry:
        draw_line_geometry(ax, geom.boundary, color, linewidth, zorder)


def build_line_exterior_bands(
    line_gdf, fill_gdf, bounds_proj, image_shape, inner_buffer_px, outer_buffer_px
):
    """根据边界线生成“外侧色带”。

    逻辑：
    1. 先把线和中国主体面都转到像素空间
    2. 对边界线做缓冲
    3. 再减去中国主体内部区域
    4. 只保留外侧的浅紫/深紫带
    """
    projected_lines = geometry_to_pixel_gdf(line_gdf, bounds_proj, image_shape)
    projected_fill = geometry_to_pixel_gdf(fill_gdf, bounds_proj, image_shape)

    line_union = projected_lines.union_all()
    fill_union = projected_fill.union_all()

    outer_band = line_union.buffer(outer_buffer_px).difference(fill_union)
    inner_band = line_union.buffer(inner_buffer_px).difference(fill_union)
    return outer_band, inner_band


def build_single_sided_line_bands(
    line_gdf, inner_buffer_px, outer_buffer_px, side_sign=1, end_extend_px=0.0
):
    """为九段线生成单侧色带。

    九段线没有像陆上国界线那样明确的“中国内侧面”可裁切，
    所以这里改用 single_sided buffer，只在一侧做外扩。
    end_extend_px 用来延长每段线的端点，避免紫色带长度看起来比黑线短。
    """
    outer_parts = []
    inner_parts = []

    def extend_linestring_ends(linestring, extend_px):
        coords = np.asarray(linestring.coords)
        if len(coords) < 2 or extend_px <= 0:
            return linestring

        start = coords[0]
        next_pt = coords[1]
        end = coords[-1]
        prev_pt = coords[-2]

        start_vec = start - next_pt
        end_vec = end - prev_pt

        start_norm = np.linalg.norm(start_vec)
        end_norm = np.linalg.norm(end_vec)
        if start_norm > 0:
            start = start + start_vec / start_norm * extend_px
        if end_norm > 0:
            end = end + end_vec / end_norm * extend_px

        new_coords = coords.copy()
        new_coords[0] = start
        new_coords[-1] = end
        return LineString(new_coords)

    def collect_single_sided(geom):
        if geom.is_empty:
            return
        if geom.geom_type == "LineString":
            geom = extend_linestring_ends(geom, end_extend_px)
            outer_parts.append(
                geom.buffer(side_sign * outer_buffer_px, single_sided=True)
            )
            inner_parts.append(
                geom.buffer(side_sign * inner_buffer_px, single_sided=True)
            )
        elif geom.geom_type == "MultiLineString":
            for part in geom.geoms:
                collect_single_sided(part)

    for geom in line_gdf.geometry:
        collect_single_sided(geom)

    if not outer_parts:
        return None, None

    outer_union = outer_parts[0]
    for geom in outer_parts[1:]:
        outer_union = outer_union.union(geom)

    inner_union = inner_parts[0]
    for geom in inner_parts[1:]:
        inner_union = inner_union.union(geom)

    return outer_union, inner_union


def draw_graticule(ax, bounds_geo, transformer, bounds_proj, image_shape):
    """绘制主图经纬网和边框经纬度标注。"""
    for lon in LON_TICKS:
        lats = np.linspace(
            bounds_geo[1] - GRATICULE_LAT_PAD, bounds_geo[3] + GRATICULE_LAT_PAD, 300
        )
        lons = np.full_like(lats, lon, dtype=float)
        xs, ys = transformer.transform(lons, lats)
        px, py = projected_point_to_pixel(
            np.asarray(xs), np.asarray(ys), bounds_proj, image_shape
        )
        ax.plot(
            px, py, linestyle=":", linewidth=1.0, color="#000000", alpha=0.8, zorder=1.5
        )

    for lat in LAT_TICKS:
        lons = np.linspace(
            bounds_geo[0] - GRATICULE_LON_PAD, bounds_geo[2] + GRATICULE_LON_PAD, 380
        )
        lats = np.full_like(lons, lat, dtype=float)
        xs, ys = transformer.transform(lons, lats)
        px, py = projected_point_to_pixel(
            np.asarray(xs), np.asarray(ys), bounds_proj, image_shape
        )
        ax.plot(
            px,
            py,
            linestyle=":",
            linewidth=0.85,
            color="#000000",
            alpha=0.6,
            zorder=1.5,
        )

    width = image_shape[1]
    height = image_shape[0]
    for lon in LON_TICKS:
        x_proj, y_proj = transformer.transform(lon, bounds_geo[1])
        px, _ = projected_point_to_pixel(x_proj, y_proj, bounds_proj, image_shape)
        if 0 <= px <= width:
            ax.text(
                px,
                height + 28,
                f"{lon}°E",
                ha="center",
                va="top",
                fontsize=10,
                color="#333333",
            )

    for lat in LAT_TICKS:
        lons = np.linspace(
            bounds_geo[0] - GRATICULE_LON_PAD, bounds_geo[2] + GRATICULE_LON_PAD, 380
        )
        lats = np.full_like(lons, lat, dtype=float)
        xs, ys = transformer.transform(lons, lats)
        px, py = projected_point_to_pixel(
            np.asarray(xs), np.asarray(ys), bounds_proj, image_shape
        )
        visible = np.where((px >= 0) & (px <= width))[0]
        if visible.size:
            label_y = py[visible[0]]
            if 0 <= label_y <= height:
                ax.text(
                    -18,
                    label_y,
                    f"{lat}°N",
                    ha="right",
                    va="center",
                    fontsize=10,
                    color="#333333",
                )


def add_north_arrow(ax, x=0.955, y=0.955, size=0.07):
    """绘制指北针。"""
    ax.text(
        x,
        y,
        "N",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=14,
        fontweight="bold",
        color="black",
        zorder=55,
    )
    ax.add_patch(
        plt.Polygon(
            [
                (x, y - size * 0.05),
                (x - size * 0.18, y - size * 0.55),
                (x, y - size),
                (x + size * 0.18, y - size * 0.55),
            ],
            closed=True,
            facecolor="black",
            edgecolor="black",
            transform=ax.transAxes,
            zorder=55,
        )
    )


def add_scale_bar(
    ax,
    bounds_proj,
    image_shape,
    length_km=SCALE_BAR_LENGTH_KM,
    location=SCALE_BAR_LOCATION,
    segments=SCALE_BAR_SEGMENTS,
):
    """绘制比例尺。"""
    width = image_shape[1]
    height = image_shape[0]
    length_m = length_km * 1000.0
    length_px = length_m / (bounds_proj[2] - bounds_proj[0]) * width
    x = width * location[0] - length_px / 2
    y = height * (1 - location[1])
    bar_h = height * 0.014
    segment_px = length_px / segments
    segment_km = length_km / segments

    for i in range(segments):
        ax.add_patch(
            Rectangle(
                (x + i * segment_px, y),
                segment_px,
                bar_h,
                facecolor="black" if i % 2 == 0 else "white",
                edgecolor="black",
                linewidth=1.0,
                zorder=50,
            )
        )
    ax.add_patch(
        Rectangle(
            (x, y),
            length_px,
            bar_h,
            fill=False,
            edgecolor="black",
            linewidth=1.0,
            zorder=51,
        )
    )

    for i in range(segments + 1):
        xpos = x + i * segment_px
        ax.plot(
            [xpos, xpos], [y, y - bar_h * 0.35], color="black", linewidth=1.0, zorder=51
        )
        ax.text(
            xpos,
            y - bar_h * 1.5,
            f"{int(i * segment_km)}",
            ha="center",
            va="top",
            fontsize=9,
        )
    ax.text(
        x + length_px + segment_px * 0.18,
        y + bar_h / 2,
        "km",
        ha="left",
        va="center",
        fontsize=8.5,
    )


def load_vector_data():
    """读取并投影所有矢量数据。"""
    provinces = gpd.read_file(PROVINCE_PATH).to_crs(TARGET_CRS)
    country_border = gpd.read_file(COUNTRY_BORDER_PATH).to_crs(TARGET_CRS)
    cities = gpd.read_file(CITY_PATH, encoding="utf-8")
    cities = (
        cities.set_crs(SOURCE_CRS) if cities.crs is None else cities.to_crs(SOURCE_CRS)
    )
    cities = cities.to_crs(TARGET_CRS)
    nine_dash = gpd.read_file(NINE_DASH_PATH).to_crs(TARGET_CRS)

    city_polygons = cities[cities["code"].isin(CITY_CODE_TO_LABEL)].copy()
    city_polygons["city_label"] = city_polygons["code"].map(CITY_CODE_TO_LABEL)
    city_polygons["city_color"] = city_polygons["city_label"].map(CITY_COLORS)
    city_polygons = city_polygons.sort_values("code")
    return provinces, country_border, city_polygons, nine_dash


def prepare_basemap_images(transformer, inverse_transformer):
    """准备主图和南海插图的底图。

    返回重投影后的 RGB 数组，以及对应的投影坐标范围。
    """
    main_geo_padded = pad_bounds_asymmetric(
        MAIN_EXTENT_GEO,
        MAIN_BASEMAP_PAD_LEFT_DEG,
        MAIN_BASEMAP_PAD_BOTTOM_DEG,
        MAIN_BASEMAP_PAD_RIGHT_DEG,
        MAIN_BASEMAP_PAD_TOP_DEG,
    )
    inset_geo_padded = pad_bounds(INSET_EXTENT_GEO, INSET_BASEMAP_PAD_DEG)

    main_basemap_geo, main_basemap_geo_bounds = crop_basemap(main_geo_padded)
    inset_basemap_geo, inset_basemap_geo_bounds = crop_basemap(inset_geo_padded)

    main_bounds_proj = project_bounds(MAIN_EXTENT_GEO, transformer)
    inset_bounds_proj = project_bounds(INSET_EXTENT_GEO, transformer)

    main_basemap = reproject_basemap_to_target(
        main_basemap_geo, main_basemap_geo_bounds, main_bounds_proj, inverse_transformer
    )
    inset_basemap = reproject_basemap_to_target(
        inset_basemap_geo,
        inset_basemap_geo_bounds,
        inset_bounds_proj,
        inverse_transformer,
    )
    return main_basemap, inset_basemap, main_bounds_proj, inset_bounds_proj


def prepare_pixel_layers(
    provinces,
    country_border,
    city_polygons,
    nine_dash,
    main_bounds_proj,
    inset_bounds_proj,
    main_basemap_shape,
    inset_basemap_shape,
):
    """把主图和插图需要的矢量层全部转换到像素空间。"""
    provinces_main = geometry_to_pixel_gdf(
        provinces, main_bounds_proj, main_basemap_shape
    )
    country_border_main = geometry_to_pixel_gdf(
        country_border, main_bounds_proj, main_basemap_shape
    )
    city_polygons_main = geometry_to_pixel_gdf(
        city_polygons, main_bounds_proj, main_basemap_shape
    )

    provinces_inset_src = provinces.clip(box(*inset_bounds_proj))
    country_border_inset_src = country_border.clip(box(*inset_bounds_proj))

    nine_dash_inset = geometry_to_pixel_gdf(
        nine_dash, inset_bounds_proj, inset_basemap_shape
    )
    provinces_inset = geometry_to_pixel_gdf(
        provinces_inset_src, inset_bounds_proj, inset_basemap_shape
    )
    country_border_inset = geometry_to_pixel_gdf(
        country_border_inset_src, inset_bounds_proj, inset_basemap_shape
    )

    country_outer_ring, country_inner_ring = build_line_exterior_bands(
        country_border,
        provinces,
        main_bounds_proj,
        main_basemap_shape,
        inner_buffer_px=8,
        outer_buffer_px=16,
    )
    country_outer_ring_inset, country_inner_ring_inset = build_line_exterior_bands(
        country_border_inset_src,
        provinces_inset_src,
        inset_bounds_proj,
        inset_basemap_shape,
        inner_buffer_px=8,
        outer_buffer_px=16,
    )
    nine_dash_outer_band, nine_dash_inner_band = build_single_sided_line_bands(
        nine_dash_inset,
        inner_buffer_px=NINE_DASH_INNER_BUFFER,
        outer_buffer_px=NINE_DASH_OUTER_BUFFER,
        side_sign=NINE_DASH_SIDE_SIGN,
        end_extend_px=NINE_DASH_END_EXTEND,
    )

    return {
        "provinces_main": provinces_main,
        "country_border_main": country_border_main,
        "city_polygons_main": city_polygons_main,
        "nine_dash_inset": nine_dash_inset,
        "provinces_inset": provinces_inset,
        "country_border_inset": country_border_inset,
        "country_outer_ring": country_outer_ring,
        "country_inner_ring": country_inner_ring,
        "country_outer_ring_inset": country_outer_ring_inset,
        "country_inner_ring_inset": country_inner_ring_inset,
        "nine_dash_outer_band": nine_dash_outer_band,
        "nine_dash_inner_band": nine_dash_inner_band,
    }


def draw_main_map(ax, main_basemap, main_bounds_proj, pixel_layers, transformer):
    """绘制主图：底图、省界、国界、城市面、图例、比例尺、指北针。"""
    ax.imshow(main_basemap, origin="upper", zorder=0)
    ax.set_xlim(0, main_basemap.shape[1])
    ax.set_ylim(main_basemap.shape[0], 0)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_linewidth(1.1)
        spine.set_color("black")

    draw_graticule(
        ax, MAIN_EXTENT_GEO, transformer, main_bounds_proj, main_basemap.shape
    )
    draw_boundary_gdf(
        ax, pixel_layers["provinces_main"], color="#202020", linewidth=1.0, zorder=2
    )

    draw_polygon_geometry(
        ax,
        pixel_layers["country_outer_ring"],
        facecolor=BORDER_OUTER_COLOR,
        edgecolor="none",
        linewidth=0,
        alpha=BORDER_OUTER_ALPHA,
        zorder=2.22,
    )
    draw_polygon_geometry(
        ax,
        pixel_layers["country_inner_ring"],
        facecolor=BORDER_INNER_COLOR,
        edgecolor="none",
        linewidth=0,
        alpha=BORDER_INNER_ALPHA,
        zorder=2.24,
    )
    draw_boundary_gdf(
        ax,
        pixel_layers["country_border_main"],
        color="#000000",
        linewidth=1.35,
        zorder=2.3,
    )

    for _, row in pixel_layers["city_polygons_main"].iterrows():
        draw_polygon_geometry(
            ax,
            row.geometry,
            facecolor=row["city_color"],
            edgecolor="#000000",
            linewidth=0.75,
            alpha=1.0,
            zorder=3,
        )
        centroid = row.geometry.representative_point()
        ax.annotate(
            row["city_label"],
            (centroid.x, centroid.y),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=11,
            fontweight="bold",
            color="black",
            bbox=dict(
                boxstyle="round,pad=0.15", facecolor=(1, 1, 1, 0.6), edgecolor="none"
            ),
            zorder=10,
        )

    ax.set_title(
        "Geographical Location of the Study Area", fontsize=17, fontweight="bold"
    )

    legend_handles = [
        Patch(facecolor=CITY_COLORS[city], edgecolor="#000000", alpha=1.0, label=city)
        for city in CITY_CODE_TO_LABEL.values()
    ]
    ax.legend(
        handles=legend_handles,
        title="Legend",
        loc="lower left",
        bbox_to_anchor=(0.015, 0.03),
        frameon=True,
        framealpha=0.97,
        facecolor="white",
        edgecolor="black",
        fontsize=9,
        title_fontsize=10,
    )

    add_north_arrow(ax)
    add_scale_bar(ax, main_bounds_proj, main_basemap.shape)


def draw_inset_map(ax_inset, inset_basemap, pixel_layers):
    """绘制南海插图：底图、省界、陆上国界、九段线。"""
    ax_inset.imshow(inset_basemap, origin="upper", zorder=0)
    ax_inset.set_xlim(0, inset_basemap.shape[1])
    ax_inset.set_ylim(inset_basemap.shape[0], 0)

    draw_boundary_gdf(
        ax_inset,
        pixel_layers["provinces_inset"],
        color="#202020",
        linewidth=0.45,
        zorder=1,
    )
    draw_polygon_geometry(
        ax_inset,
        pixel_layers["country_outer_ring_inset"],
        facecolor=BORDER_OUTER_COLOR,
        edgecolor="none",
        linewidth=0,
        alpha=BORDER_OUTER_ALPHA,
        zorder=1.22,
    )
    draw_polygon_geometry(
        ax_inset,
        pixel_layers["country_inner_ring_inset"],
        facecolor=BORDER_INNER_COLOR,
        edgecolor="none",
        linewidth=0,
        alpha=BORDER_INNER_ALPHA,
        zorder=1.24,
    )
    draw_boundary_gdf(
        ax_inset,
        pixel_layers["country_border_inset"],
        color="#000000",
        linewidth=0.8,
        zorder=1.3,
    )

    if pixel_layers["nine_dash_outer_band"] is not None:
        draw_polygon_geometry(
            ax_inset,
            pixel_layers["nine_dash_outer_band"],
            facecolor=BORDER_OUTER_COLOR,
            edgecolor="none",
            linewidth=0,
            alpha=BORDER_OUTER_ALPHA,
            zorder=1.85,
        )
        draw_polygon_geometry(
            ax_inset,
            pixel_layers["nine_dash_inner_band"],
            facecolor=BORDER_INNER_COLOR,
            edgecolor="none",
            linewidth=0,
            alpha=BORDER_INNER_ALPHA,
            zorder=1.9,
        )

    for geom in pixel_layers["nine_dash_inset"].geometry:
        draw_line_geometry(ax_inset, geom, color="black", linewidth=1.1, zorder=2)

    ax_inset.set_xticks([])
    ax_inset.set_yticks([])
    for spine in ax_inset.spines.values():
        spine.set_visible(True)
        spine.set_color("black")
        spine.set_linewidth(1.0)


def main():
    """主入口：准备数据、绘制主图与南海插图、输出 PNG。"""
    transformer = Transformer.from_crs(SOURCE_CRS, TARGET_CRS, always_xy=True)
    inverse_transformer = Transformer.from_crs(TARGET_CRS, SOURCE_CRS, always_xy=True)

    provinces, country_border, city_polygons, nine_dash = load_vector_data()
    main_basemap, inset_basemap, main_bounds_proj, inset_bounds_proj = (
        prepare_basemap_images(transformer, inverse_transformer)
    )
    pixel_layers = prepare_pixel_layers(
        provinces,
        country_border,
        city_polygons,
        nine_dash,
        main_bounds_proj,
        inset_bounds_proj,
        main_basemap.shape,
        inset_basemap.shape,
    )

    fig, ax = plt.subplots(figsize=(13, 10))
    fig.subplots_adjust(left=0.06, right=0.97, top=0.94, bottom=0.09)
    draw_main_map(ax, main_basemap, main_bounds_proj, pixel_layers, transformer)

    ax_inset = fig.add_axes(INSET_AXES_RECT)
    draw_inset_map(ax_inset, inset_basemap, pixel_layers)

    plt.savefig(
        OUTPUT_PATH, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none"
    )
    print(f"Saved map to: {OUTPUT_PATH}")
    plt.close(fig)


if __name__ == "__main__":
    main()
