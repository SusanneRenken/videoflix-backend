from django.conf import settings
from pathlib import Path
from .models import Video
import subprocess
import shutil
import logging

logger = logging.getLogger(__name__)

MEDIA_ROOT = Path(settings.MEDIA_ROOT)

# feste, saubere ffmpeg-Standards
RESOLUTIONS = {
    "480": "854:480",
    "720": "1280:720",
    "1080": "1920:1080",
}


def convert_video(video_id):
    video = Video.objects.get(id=video_id)

    video.status = "processing"
    video.save(update_fields=["status"])

    prepare_directories(video)

    success = (
        convert_original_to_variants(video)
        and create_thumbnail(video)
    )

    if not success:
        delete_directories(video)
        return

    move_original(video)

    video.status = "ready"
    video.save(update_fields=["status"])


def prepare_directories(video):
    video_root = MEDIA_ROOT / "videos" / f"video_{video.id}"

    (video_root / "original").mkdir(parents=True, exist_ok=True)
    (video_root / "processed" / "480p").mkdir(parents=True, exist_ok=True)
    (video_root / "processed" / "720p").mkdir(parents=True, exist_ok=True)
    (video_root / "processed" / "1080p").mkdir(parents=True, exist_ok=True)
    (video_root / "thumbnails").mkdir(parents=True, exist_ok=True)


def convert_original_to_variants(video):
    for resolution, scale in RESOLUTIONS.items():
        if not convert_resolution(video, resolution, scale):
            return False
    return True


def convert_resolution(video, resolution, scale):
    logger.info("Converting video %s to %sp", video.id, resolution)

    video_root = MEDIA_ROOT / "videos" / f"video_{video.id}"
    target_dir = video_root / "processed" / f"{resolution}p"
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / "index.m3u8"

    cmd = [
        "ffmpeg",
        "-i", video.original_file.path,
        "-vf", f"scale={scale}",
        "-start_number", "0",
        "-hls_time", "10",
        "-hls_list_size", "0",
        "-f", "hls",
        str(target_path),
    ]

    result = subprocess.run(cmd, capture_output=True)

    if result.returncode != 0:
        logger.error("FFmpeg failed for video %s (%sp)", video.id, resolution)
        video.status = "error"
        video.save(update_fields=["status"])
        return False

    return True


def create_thumbnail(video):
    logger.info("Creating thumbnail for video %s", video.id)

    thumbnail_root = MEDIA_ROOT / "videos" / f"video_{video.id}" / "thumbnails"
    thumbnail_root.mkdir(parents=True, exist_ok=True)

    thumbnail_path = thumbnail_root / "thumbnail.jpg"

    cmd = [
        "ffmpeg",
        "-i", video.original_file.path,
        "-vf", "thumbnail=n=100",
        "-frames:v", "1",
        "-q:v", "2",
        str(thumbnail_path),
    ]

    result = subprocess.run(cmd, capture_output=True)

    if result.returncode != 0:
        logger.error("Thumbnail creation failed for video %s", video.id)
        video.status = "error"
        video.save(update_fields=["status"])
        return False

    video.thumbnail.name = f"videos/video_{video.id}/thumbnails/thumbnail.jpg"
    video.save(update_fields=["thumbnail"])

    return True


def delete_directories(video):
    video_root = MEDIA_ROOT / "videos" / f"video_{video.id}"
    if video_root.exists():
        shutil.rmtree(video_root)


def move_original(video):
    source_path = Path(video.original_file.path)

    video_root = MEDIA_ROOT / "videos" / f"video_{video.id}"
    target_dir = video_root / "original"
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / source_path.name

    shutil.copy2(source_path, target_path)
    source_path.unlink()

    video.original_file.name = f"videos/video_{video.id}/original/{source_path.name}"
    video.save(update_fields=["original_file"])
