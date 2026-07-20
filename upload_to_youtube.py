import os, sys, json, io
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from datetime import datetime

load_dotenv()

YT_CLIENT_ID = os.getenv("YT_CLIENT_ID") or os.getenv("YOUTUBE_CLIENT_ID", "")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET") or os.getenv("YOUTUBE_CLIENT_SECRET", "")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN") or os.getenv("YOUTUBE_REFRESH_TOKEN", "")
CHANNEL_NAME = "DreamDrifter TV"


def get_authenticated_service():
    if not all([YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN]):
        raise ValueError("Missing YouTube credentials")
    creds = Credentials(
        None, refresh_token=YT_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YT_CLIENT_ID, client_secret=YT_CLIENT_SECRET
    )
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def compress_thumbnail(img_path, max_size=2097152):
    img = Image.open(img_path)
    thumb_bytes = io.BytesIO()
    quality = 85
    img.save(thumb_bytes, format="JPEG", quality=quality)
    while thumb_bytes.tell() > max_size and quality > 10:
        quality -= 10
        thumb_bytes = io.BytesIO()
        img.save(thumb_bytes, format="JPEG", quality=quality)
    thumb_bytes.seek(0)
    return thumb_bytes


def generate_thumbnail(image_path: str, output_path: str, screensaver_name: str):
    img = Image.open(image_path).convert("RGBA")
    img = img.resize((1920, 1080), Image.LANCZOS)
    draw = ImageDraw.Draw(img)

    font_paths = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]

    def load_font(paths, size):
        for p in paths:
            if Path(p).exists():
                try: return ImageFont.truetype(p, size)
                except: continue
        return ImageFont.load_default()

    f_brand = load_font(font_paths, 80)
    f_name = load_font(font_paths, 55)
    f_sub = load_font(font_paths, 35)

    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([(0, 0), (1920, 1080)], fill=(0, 0, 0, 60))
    for y in range(200, 500):
        overlay_draw.rectangle([(0, y), (1920, y + 1)], fill=(0, 0, 0, max(0, int(100 * (1 - (y - 200) / 300)))))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    draw.text((960, 280), screensaver_name, fill=(255, 255, 255), font=f_brand, anchor="mm")
    draw.text((960, 380), "4K SCREENSAVER", fill=(255, 255, 255), font=f_name, anchor="mm")
    draw.text((960, 440), "1 HOUR RELAXATION", fill=(200, 200, 200), font=f_sub, anchor="mm")

    bar_y = 920
    bar_height = 80
    draw.rectangle([(0, bar_y), (1920, bar_y + bar_height)], fill=(0, 0, 0, 180))
    draw.text((960, bar_y + bar_height // 2), CHANNEL_NAME, fill=(255, 255, 255), font=f_name, anchor="mm")

    img = img.convert("RGB")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=90, optimize=True)
    print(f"[thumbnail] Created: {output_path}")
    return output_path


def generate_title_description(screensaver_name: str):
    slug = screensaver_name.lower().replace(" ", "-")
    titles = [
        f"1 Hour {screensaver_name} Screensaver - 4K Relaxing Nature Ambience for TV",
        f"{screensaver_name} | 1 Hour 4K Screensaver - Relaxing Nature Video No Music",
        f"{screensaver_name} - 1 Hour 4K Screensaver | Relaxing TV Background",
        f"1 Hour of {screensaver_name} - 4K Screensaver for Relaxation & Ambience",
        f"{screensaver_name} 4K Screensaver TV - 1 Hour Relaxing Visuals No Audio",
    ]

    today = datetime.now().strftime("%B %d, %Y")
    description = f"{screensaver_name} - 1 Hour 4K Screensaver | Relaxing Nature Ambience\n\n"
    description += f"Immerse yourself in 1 hour of stunning {screensaver_name.lower()} in beautiful 4K Ultra HD quality. "
    description += f"This relaxing screensaver is perfect for unwinding, meditation, studying, working, "
    description += f"or as a peaceful background for your TV or monitor.\n\n"
    description += f"No music, no talking - just pure calming visuals to help you relax and focus.\n\n"
    description += f"WHAT YOU WILL GET:\n"
    description += f"- 4K Ultra HD Resolution (3840x2160)\n"
    description += f"- 1 Hour Continuous Playback\n"
    description += f"- No Audio - Pure Visuals Only\n"
    description += f"- Perfect for Sleep, Meditation, Study, Work\n"
    description += f"- Great for TV Screensavers, Digital Displays, Ambience\n\n"
    description += f"Uploaded: {today}\n\n"
    description += f"SUBSCRIBE for a new relaxing screensaver every day!\n"
    description += f"Like if this helps you relax\n"
    description += f"Comment your favorite nature scene\n\n"
    description += f"#Screensaver #Relaxing #Nature #{slug} "
    description += f"#4K #Screensaver #4KScreensaver #Ambience #Relaxation #Calm #Peaceful #Nature #UltraHD\n\n"
    description += f"© {datetime.now().year} {CHANNEL_NAME}"

    return titles, titles[0], description


def update_channel_info(youtube):
    channel_desc = (
        "Welcome to DreamDrifter TV - your daily escape into peaceful, dreamy visuals.\n\n"
        "Every day we upload 1 hour of stunning 4K ambient visuals and relaxing screensavers "
        "to help you unwind, meditate, study, work, or sleep. No music, no talking - "
        "just pure calming nature scenery and beautiful landscapes.\n\n"
        "WHAT WE OFFER:\n"
        "- 1 Hour 4K Ambient Visuals\n"
        "- Relaxing Screensavers for TV\n"
        "- Nature & Scenic Landscapes\n"
        "- No Music - No Audio - Pure Calm\n"
        "- New Video Every Day at 10 AM EST\n\n"
        "PERFECT FOR:\n"
        "- TV Background & Digital Displays\n"
        "- Meditation & Mindfulness\n"
        "- Studying & Working Focus\n"
        "- Sleep Aid & Deep Relaxation\n"
        "- Home Decor Ambience\n"
        "- Yoga & Spa Environments\n\n"
        "Subscribe and drift into a dreamy visual escape every day."
    )
    try:
        channels = youtube.channels().list(part="brandingSettings", mine=True).execute()
        if channels.get("items"):
            cid = channels["items"][0]["id"]
            youtube.channels().update(
                part="brandingSettings",
                body={
                    "id": cid,
                    "brandingSettings": {
                        "channel": {
                            "description": channel_desc,
                            "keywords": "dreamdrifter TV relaxing visuals ambient nature scenery TV background meditation sleep study work calm peaceful",
                        }
                    }
                }
            ).execute()
            print(f"[youtube] Channel description updated", flush=True)
    except Exception as e:
        print(f"[youtube] Channel update skipped: {e}", flush=True)


def upload_to_youtube():
    try:
        meta_path = Path("output") / "latest_video.json"
        if not meta_path.exists():
            print("[youtube] No latest_video.json found")
            return False

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        video_path = Path(meta["video_path"])
        if not video_path.exists():
            print(f"[youtube] Video not found: {video_path}")
            return False

        screensaver_name = meta.get("screensaver_name", "Screensaver")
        image_path = meta.get("image_path", "")

        titles, selected_title, description = generate_title_description(screensaver_name)
        if len(description) > 4900:
            description = description[:4900] + f"\n\n#Screensaver #Relaxing"

        tags = [
            "screensaver", "relaxing screensaver", "4K screensaver", "4K", "nature screensaver",
            "TV screensaver", "background video", "relaxing video", "ambience",
            "1 hour screensaver", "screensaver no music", "calm screensaver",
            "peaceful screensaver", screensaver_name, f"{screensaver_name} screensaver",
            "screensaver for TV", "relaxation", "meditation background",
            "no audio screensaver", "ultra hd", "2160p",
        ]

        print(f"[youtube] Title: {selected_title[:80]}...")
        print(f"[youtube] Video: {video_path}")
        print(f"[youtube] Duration: 1 hour")

        youtube = get_authenticated_service()

        update_channel_info(youtube)

        body = {
            "snippet": {
                "title": selected_title,
                "description": description,
                "tags": tags,
                "categoryId": "27"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            }
        }

        media = MediaFileUpload(str(video_path), chunksize=1024*1024*10, resumable=True)
        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"[youtube] Upload: {int(status.progress() * 100)}%")

        video_id = response["id"]
        print(f"[youtube] Uploaded! ID: {video_id}")
        print(f"[youtube] URL: https://youtube.com/watch?v={video_id}")

        thumbnail_path = Path("output/thumbnail.jpg")
        if image_path and Path(image_path).exists():
            print(f"[youtube] Generating thumbnail...")
            generate_thumbnail(image_path, str(thumbnail_path), screensaver_name)

        if thumbnail_path.exists():
            print(f"[youtube] Thumbnail file found ({thumbnail_path.stat().st_size // 1024}KB)")
            try:
                thumb_bytes = compress_thumbnail(str(thumbnail_path))
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaIoBaseUpload(thumb_bytes, mimetype="image/jpeg", resumable=False)
                ).execute()
                print(f"[youtube] Thumbnail uploaded!")
            except Exception as e:
                print(f"[youtube] Thumbnail upload failed: {e}")
        else:
            print(f"[youtube] Thumbnail NOT FOUND at: {thumbnail_path}")

        result = {
            "video_id": video_id,
            "url": f"https://youtube.com/watch?v={video_id}",
            "title": selected_title,
            "screensaver_name": screensaver_name,
            "uploaded_at": datetime.now().isoformat()
        }
        with open("output/upload_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"[youtube] Success!")
        return True

    except Exception as e:
        print(f"[youtube] Failed: {e}")
        return False


def estimate_upload_time(file_size_gb: float, speed_mbps: float = 10):
    upload_speed = speed_mbps / 8
    seconds = (file_size_gb * 1024) / upload_speed
    return seconds / 60


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=f"{CHANNEL_NAME} YouTube Uploader")
    parser.add_argument("--estimate", action="store_true", help="Estimate upload time")
    args = parser.parse_args()

    if args.estimate:
        video_meta = Path("output/latest_video.json")
        if video_meta.exists():
            with open(video_meta) as f:
                meta = json.load(f)
            vpath = meta.get("video_path", "")
            if vpath and Path(vpath).exists():
                size_mb = Path(vpath).stat().st_size / 1024 / 1024
                print(f"File size: {size_mb:.2f} MB ({size_mb/1024:.2f} GB)")
                print(f"Estimated upload time at 10 Mbps: {estimate_upload_time(size_mb/1024, 10):.1f} min")
                print(f"Estimated upload time at 25 Mbps: {estimate_upload_time(size_mb/1024, 25):.1f} min")
                print(f"Estimated upload time at 50 Mbps: {estimate_upload_time(size_mb/1024, 50):.1f} min")
                print(f"Estimated upload time at 100 Mbps: {estimate_upload_time(size_mb/1024, 100):.1f} min")

    success = upload_to_youtube()
    sys.exit(0 if success else 1)
