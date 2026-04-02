from pathlib import Path
import zipfile

import requests


# 下载的 Natural Earth 底图压缩包地址。
BASEMAP_URL = "https://naciscdn.org/naturalearth/50m/raster/HYP_50M_SR_W.zip"

# 工作目录。
WORKDIR = Path(r"E:\Self\Work\hrs")

# 下载后的压缩包路径。
ZIP_PATH = WORKDIR / "HYP_50M_SR_W.zip"

# 解压目录。
EXTRACT_DIR = WORKDIR / "HYP_50M_SR_W"


def main():
    WORKDIR.mkdir(parents=True, exist_ok=True)

    print(f"开始下载底图: {BASEMAP_URL}")
    response = requests.get(BASEMAP_URL, timeout=120)
    response.raise_for_status()
    ZIP_PATH.write_bytes(response.content)
    print(f"压缩包已保存到: {ZIP_PATH}")

    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zf.extractall(EXTRACT_DIR)

    print(f"底图已解压到: {EXTRACT_DIR}")
    print("你后续绘图实际会用到的文件通常是:")
    print(EXTRACT_DIR / "HYP_50M_SR_W.tif")
    print(EXTRACT_DIR / "HYP_50M_SR_W.tfw")


if __name__ == "__main__":
    main()
