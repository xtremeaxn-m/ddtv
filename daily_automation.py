import os, sys, json, subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"

for d in [OUTPUT_DIR, OUTPUT_DIR / "images", OUTPUT_DIR / "videos"]:
    d.mkdir(exist_ok=True)


def run_step(step_name: str, script: str, args: list = None):
    print(f"\n{'='*70}")
    print(f"  STEP: {step_name}")
    print(f"{'='*70}\n")

    cmd = [sys.executable, str(BASE_DIR / script)]
    if args:
        cmd.extend(args)

    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode == 0


def estimate_upload_time(file_size_gb: float, speed_mbps: float = 10):
    upload_speed = speed_mbps / 8
    seconds = (file_size_gb * 1024) / upload_speed
    return seconds / 60


def main():
    print(f"\n{'='*70}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  KREGGSART TV - Daily Screensaver Automation")
    print(f"{'='*70}\n")

    steps = [
        ("Generate Screensaver Image", "generate_screensaver_image.py"),
        ("Create 4K Video (1 Hour)", "create_4k_video.py"),
        ("Upload to YouTube", "upload_to_youtube.py"),
    ]

    for i, (step_name, script) in enumerate(steps, 1):
        print(f"\n[{i}/{len(steps)}] {step_name}")
        success = run_step(step_name, script)
        if not success:
            print(f"[ERROR] Step '{step_name}' FAILED!")
            sys.exit(1)

    video_meta_path = OUTPUT_DIR / "latest_video.json"
    if video_meta_path.exists():
        with open(video_meta_path) as f:
            meta = json.load(f)
        vpath = meta.get("video_path", "")
        if vpath and Path(vpath).exists():
            size_mb = Path(vpath).stat().st_size / 1024 / 1024
            print(f"\n{'='*70}")
            print(f"  VIDEO STATS")
            print(f"{'='*70}")
            print(f"  File size: {size_mb:.2f} MB ({size_mb/1024:.2f} GB)")
            print(f"  Duration: 1 hour")
            print(f"  Resolution: HD (1920x1080)")
            print(f"  Format: 16:9")
            for speed in [10, 25, 50, 100]:
                est = estimate_upload_time(size_mb/1024, speed)
                print(f"  Est. upload @ {speed} Mbps: {est:.1f} min")

    print(f"\n{'='*70}")
    print(f"  DAILY AUTOMATION COMPLETE!")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
