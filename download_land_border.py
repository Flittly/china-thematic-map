from pathlib import Path
import zipfile

import requests


# Natural Earth 10m 陆上国界线数据。
# 这是国家与国家之间的陆地边界线，不是海岸线。
LAND_BORDER_URL = (
    "https://naciscdn.org/naturalearth/10m/cultural/"
    "ne_10m_admin_0_boundary_lines_land.zip"
)

# 工作目录。
WORKDIR = Path(r"E:\Self\Work\hrs")

# 下载后的压缩包路径。
ZIP_PATH = WORKDIR / "ne_10m_admin_0_boundary_lines_land.zip"

# 解压目录。
EXTRACT_DIR = WORKDIR / "ne_10m_admin_0_boundary_lines_land"


def main():
    WORKDIR.mkdir(parents=True, exist_ok=True)

    print(f"开始下载陆上国界线数据: {LAND_BORDER_URL}")
    response = requests.get(LAND_BORDER_URL, timeout=120)
    response.raise_for_status()
    ZIP_PATH.write_bytes(response.content)
    print(f"压缩包已保存到: {ZIP_PATH}")

    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zf.extractall(EXTRACT_DIR)

    print(f"陆上国界线数据已解压到: {EXTRACT_DIR}")
    print("后续常用文件是:")
    print(EXTRACT_DIR / "ne_10m_admin_0_boundary_lines_land.shp")


if __name__ == "__main__":
    main()
