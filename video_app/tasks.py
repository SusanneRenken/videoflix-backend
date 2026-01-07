from django.conf import settings
from pathlib import Path
from .models import Video
import subprocess
import shutil

MEDIA_ROOT = Path(settings.MEDIA_ROOT)

def convert_video(video_id):
    success = True

    video = Video.objects.get(id=video_id)

    video.status = 'processing'
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

    video.status = 'ready'
    video.save(update_fields=["status"])


def prepare_directories(video):
    video_root = MEDIA_ROOT / "videos" / f"video_{video.id}"

    (video_root / "original").mkdir(parents=True, exist_ok=True)
    (video_root / "processed" / "480p").mkdir(parents=True, exist_ok=True)
    (video_root / "processed" / "720p").mkdir(parents=True, exist_ok=True)
    (video_root / "processed" / "1080p").mkdir(parents=True, exist_ok=True)
    (video_root / "thumbnails").mkdir(parents=True, exist_ok=True)


def convert_original_to_variants(video):
    for resolution in ["480", "720", "1080"]:
        success = convert_resolution(video, resolution)
        if not success:
            return False
    return True


def convert_resolution(video, resolution):
    print(f"Converting to {resolution}p...")

    video_root = MEDIA_ROOT / "videos" / f"video_{video.id}"
    target_dir = video_root / "processed" / f"{resolution}p"
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / "index.m3u8"

    cmd = 'ffmpeg -i "{}" -s hd{} -start_number 0 -hls_time 10 -hls_list_size 0 -f hls "{}"'.format(video.original_file.path, resolution, target_path)

    result = subprocess.run(cmd, capture_output=True, shell=True)

    if result.returncode != 0:
        video.status = 'error'
        video.save(update_fields=["status"])
        return False

    return True


def create_thumbnail(video):
    print("Creating thumbnail...")
    
    thumbnail_root = MEDIA_ROOT / "videos" / f"video_{video.id}" / "thumbnails"
    thumbnail_root.mkdir(parents=True, exist_ok=True)

    cmd = 'ffmpeg -i "{}" -vf thumbnail=n=100 -frames:v 1 -q:v 2 "{}"'.format(video.original_file.path, thumbnail_root / "thumbnail.jpg")

    result = subprocess.run(cmd, capture_output=True, shell=True)

    if result.returncode != 0:
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

    video_root = Path(settings.MEDIA_ROOT) / "videos" / f"video_{video.id}"
    target_dir = video_root / "original"
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / source_path.name

    shutil.copy2(source_path, target_path)
    source_path.unlink()

    video.original_file.name = f"videos/video_{video.id}/original/{source_path.name}"
    video.save(update_fields=["original_file"])