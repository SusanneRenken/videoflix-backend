from django.conf import settings
from pathlib import Path
from .models import Video
import subprocess

MEDIA_ROOT = Path(settings.MEDIA_ROOT)

def convert_video(video_id):
    video = Video.objects.get(id=video_id)

    video.status = 'processing'
    video.save(update_fields=["status"])

    prepare_directories(video)
    move_original(video)
    convert_original_to_variants(video)
    create_thumbnail(video)

    video.status = 'ready'
    video.save(update_fields=["status"])


def prepare_directories(video):
    video_root = MEDIA_ROOT / "videos" / f"video_{video.id}"

    (video_root / "original").mkdir(parents=True, exist_ok=True)
    (video_root / "processed" / "480p").mkdir(parents=True, exist_ok=True)
    (video_root / "processed" / "720p").mkdir(parents=True, exist_ok=True)
    (video_root / "processed" / "1080p").mkdir(parents=True, exist_ok=True)
    (video_root / "thumbnails").mkdir(parents=True, exist_ok=True)


def move_original(video):
    source_path = Path(video.original_file.path)

    video_root = Path(settings.MEDIA_ROOT) / "videos" / f"video_{video.id}"
    target_dir = video_root / "original"
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / source_path.name

    shutil.copy2(source_path, target_path)

    # 2. Originaldatei löschen
    source_path.unlink()

    # 3. Django-Pfad aktualisieren
    video.original_file.name = f"videos/video_{video.id}/original/{source_path.name}"
    video.save(update_fields=["original_file"])



def convert_original_to_variants(video):
    convert_resolution(video, "480")
    convert_resolution(video, "720")
    convert_resolution(video, "1080")


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


def create_thumbnail(video):
    print("Creating thumbnail...")
    pass