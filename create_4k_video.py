import subprocess, json, sys, os, shutil
from pathlib import Path
from datetime import datetime

VIDEO_WIDTH = 3840
VIDEO_HEIGHT = 2160
FPS = 30
TARGET_DURATION_SECONDS = 3600
SEGMENT_DURATION = 60


def get_encoder_list():
    encoders = [
        ("h264_nvenc", ["-preset", "p1", "-tune", "hq", "-rc", "vbr", "-cq", "23", "-b:v", "0"]),
        ("h264_amf", ["-quality", "speed", "-rc", "cbr", "-b:v", "20M"]),
        ("h264_qsv", ["-preset", "veryfast", "-global_quality", "23"]),
        ("h264_mf", []),
    ]
    test = subprocess.run(["ffmpeg", "-encoders"], capture_output=True, text=True)
    available = [e for e, _ in encoders if e in test.stdout]
    return available


def create_segment(image_path: str, segment_path: str) -> bool:
    encoders = get_encoder_list()
    attempts = encoders + ["libx264"]
    tried = []

    for enc_name in attempts:
        if enc_name == "h264_nvenc":
            params = ["-preset", "p1", "-tune", "hq", "-rc", "vbr", "-cq", "23", "-b:v", "0"]
        elif enc_name == "h264_amf":
            params = ["-quality", "speed", "-rc", "cbr", "-b:v", "20M"]
        elif enc_name == "h264_qsv":
            params = ["-preset", "veryfast", "-global_quality", "23"]
        elif enc_name == "h264_mf":
            params = []
        else:
            params = ["-preset", "ultrafast", "-crf", "23"]

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(image_path),
            "-c:v", enc_name,
            "-t", str(SEGMENT_DURATION),
            "-r", str(FPS),
            "-pix_fmt", "yuv420p",
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
            *params,
            "-profile:v", "high",
            "-level", "5.1",
            "-an",
            str(segment_path)
        ]
        tried.append(enc_name)
        print(f"[video] Trying encoder: {enc_name}...", flush=True)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            size = segment_path.stat().st_size
            print(f"[video] Segment done: {size / 1024 / 1024:.2f} MB ({enc_name})", flush=True)
            return True
        err_preview = result.stderr.replace('\n', ' | ')[:200]
        print(f"[video] {enc_name} failed: {err_preview}", flush=True)

    print(f"[video] All encoders failed: {', '.join(tried)}", flush=True)
    return False


def concat_segments(segment_path: str, output_path: str):
    count = TARGET_DURATION_SECONDS // SEGMENT_DURATION
    print(f"[video] Looping segment {count}x to make {count * SEGMENT_DURATION // 60} min video...", flush=True)

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", str(count - 1),
        "-i", str(segment_path),
        "-c", "copy",
        "-t", str(TARGET_DURATION_SECONDS),
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[video] Loop failed, trying alternative...", flush=True)
        concat_file = segment_path.parent / "concat.txt"
        copies_dir = segment_path.parent / "copies"
        copies_dir.mkdir(exist_ok=True)
        with open(concat_file, "w") as f:
            for i in range(count):
                copy_path = copies_dir / f"seg_{i:04d}.mp4"
                if not copy_path.exists():
                    import shutil
                    shutil.copy2(segment_path, copy_path)
                f.write(f"file '{copy_path}'\n")
        cmd2 = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(output_path)]
        result2 = subprocess.run(cmd2, capture_output=True, text=True)
        concat_file.unlink(missing_ok=True)
        shutil.rmtree(copies_dir, ignore_errors=True)
        if result2.returncode != 0:
            print(f"[video] All concat methods failed", flush=True)
            return False
    return True


def create_4k_screensaver_video(image_path: str, output_path: str):
    if not Path(image_path).exists():
        print(f"Error: Image not found at {image_path}")
        return None

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = output_path.parent / "temp_segments"
    temp_dir.mkdir(exist_ok=True)
    segment_path = temp_dir / "segment.mp4"

    print(f"[video] 4K Screensaver Video Generator", flush=True)
    print(f"[video] Image: {image_path}", flush=True)
    print(f"[video] Method: 1 encode ({SEGMENT_DURATION}s) + concat copy ({TARGET_DURATION_SECONDS // SEGMENT_DURATION}x)", flush=True)
    print(f"[video] Final: {TARGET_DURATION_SECONDS}s ({TARGET_DURATION_SECONDS//60} min)", flush=True)

    if not create_segment(image_path, segment_path):
        return None

    if not concat_segments(segment_path, output_path):
        return None

    shutil.rmtree(temp_dir, ignore_errors=True)

    duration = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(output_path)],
        capture_output=True, text=True
    ).stdout.strip() or 0)
    file_size = output_path.stat().st_size

    print(f"[video] Done!", flush=True)
    print(f"[video] Duration: {duration:.0f}s ({duration/60:.0f} min)", flush=True)
    print(f"[video] Size: {file_size / 1024 / 1024:.2f} MB", flush=True)
    print(f"[video] Path: {output_path}", flush=True)

    return str(output_path)


if __name__ == "__main__":
    meta_path = Path("output") / "latest_image.json"
    if not meta_path.exists():
        print("No latest_image.json found. Run generate_screensaver_image.py first.")
        sys.exit(1)

    with open(meta_path, "r") as f:
        meta = json.load(f)

    image_path = meta.get("image_path")
    if not image_path or not Path(image_path).exists():
        print(f"Image not found: {image_path}")
        sys.exit(1)

    video_dir = Path("output/videos")
    video_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = video_dir / f"screensaver_{timestamp}.mp4"

    result = create_4k_screensaver_video(image_path, str(output_path))

    if result:
        video_meta = {
            "video_path": result,
            "image_path": image_path,
            "screensaver_name": meta.get("name", "Screensaver"),
            "duration_seconds": TARGET_DURATION_SECONDS,
            "duration_minutes": TARGET_DURATION_SECONDS / 60,
            "resolution": f"{VIDEO_WIDTH}x{VIDEO_HEIGHT}",
            "generated_at": datetime.now().isoformat(),
        }
        with open(Path("output") / "latest_video.json", "w") as f:
            json.dump(video_meta, f, indent=2)
        print(f"\nVideo metadata saved to output/latest_video.json", flush=True)
    else:
        print("Failed to create video")
        sys.exit(1)
