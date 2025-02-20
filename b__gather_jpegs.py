# /// script
# requires-python = "~=3.12.0"
# dependencies = [
#    "httpx",
# ]
# ///

"""
Gathers HH018977 / AFL-CIO org jpgs, at 25% of their full size.

Usage:
$ uv run ./a__gather_org_pids.py
"""

import json
import logging
import pprint
import sys
from pathlib import Path

import httpx

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


PROJECT_DIR_NAME = 'ml_hhoag_image_clustering_project'
SAVED_IMAGES_DIR_PATH = '../output_data/the_images/'
SAVED_IMAGES_JSON_PATH = '../output_data/b__afl_cio_HH018977_image_paths.json'


## define  type of the image entry
ImageEntry = dict[str, str]

## sample data
image_entries: list[ImageEntry] = [
    {'mods_id_bdr_pid_ssim': 'HH018977_0003', 'pid': 'bdr:7gfwfrsp'},
    {'mods_id_bdr_pid_ssim': 'HH018977_0004', 'pid': 'bdr:9mk2xybw'},
]


def check_cwd() -> None:
    cwd = Path.cwd()
    log.info(f'cwd: ``{cwd}``')
    if not cwd.name == PROJECT_DIR_NAME:
        print(f"ERROR: cd into the project directory; you're at:: ``{cwd}``")
        sys.exit(1)
    return


def download_images(entries: list[ImageEntry], images_dir_path_string: str) -> list[Path]:
    images_dir_path = Path(images_dir_path_string).resolve()
    log.info(f'images_dir_path: ``{images_dir_path}``')
    images_dir_path.mkdir(parents=True, exist_ok=True)  # create the directory if needed

    downloaded_image_paths: list[Path] = []
    for entry in entries:
        mods_id: str = entry['mods_id_bdr_pid_ssim']
        pid: str = entry['pid']
        ## construct iiif-url ---------------------------------------
        url: str = f'https://repository.library.brown.edu/iiif/image/{pid}/full/pct:25/0/default.jpg'
        try:
            response: httpx.Response = httpx.get(url)
            response.raise_for_status()
        except httpx.HTTPError as e:
            log.exception(f'Error downloading image for {mods_id}: {e}')
            continue

        ## replace colon in pid with underscore for file naming -----
        pid_for_filename: str = pid.replace(':', '_')
        file_name: str = f'{mods_id}__{pid_for_filename}.jpg'
        file_path: Path = images_dir_path / file_name
        file_path = file_path.resolve()
        file_path.write_bytes(response.content)
        downloaded_image_paths.append(str(file_path))
        log.info(f'Downloaded {file_name} from {url}')
    return downloaded_image_paths


def export_json(pids_and_IDs: list) -> None:
    save_path = Path(SAVED_IMAGES_JSON_PATH).resolve()
    save_path.parent.mkdir(parents=True, exist_ok=True)  # create parent dirs if needed
    log.info(f'save_path: ``{save_path}``')
    with open(save_path, 'w') as f:
        json.dump(pids_and_IDs, f, sort_keys=True, indent=2)
    return


def main() -> None:
    check_cwd()
    downloaded_paths: list[Path] = download_images(image_entries, SAVED_IMAGES_DIR_PATH)
    log.info('Downloaded image paths.')
    log.info(f'downloaded_paths: ``{pprint.pformat(downloaded_paths)}``')
    export_json(downloaded_paths)
    return


if __name__ == '__main__':
    main()
