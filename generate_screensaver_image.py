import os, io, random, json, requests, sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

POLLINATIONS_KEY = os.getenv("POLLINATIONS_API_KEY", "sk_K98O2j1UlpALX9TBAoAuEdqxL1hpB7zh")
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

SCREENSAVERS = [
    ("Spirited Meadow", "Studio Ghibli style magical meadow with glowing fireflies, rolling green hills, whimsical flowers, soft warm sunset light, anime painting style, vibrant colors, dreamy atmosphere, highly detailed, no text"),
    ("Forest Spirit's Home", "Studio Ghibli style enchanted forest with giant ancient trees, soft sunbeams filtering through canopy, tiny forest spirits glowing, mossy ground, magical atmosphere, anime painting, cinematic 4K quality"),
    ("Howl's Floating Garden", "Studio Ghibli style floating garden in the sky, colorful flowers cascading down, soft clouds all around, warm golden hour light, whimsical and dreamy, anime watercolor style, highly detailed"),
    ("Secret Beach Cove", "Studio Ghibli style secret beach cove with crystal clear turquoise water, white sand, tropical flowers, gentle waves, warm golden sunset light, anime painting, peaceful serene atmosphere, ultra detailed"),
    ("Mountain Village Sunrise", "Studio Ghibli style mountain village at sunrise, cozy houses on hillside, misty valleys, warm orange sky, cherry blossom trees, lush green terraced fields, anime landscape painting"),
    ("Whispering Bamboo Grove", "Studio Ghibli style bamboo forest with soft green light filtering through, gentle breeze, tiny glowing spirits among bamboo stalks, mossy stone path, magical serene atmosphere, anime art style"),
    ("Ocean of Stars", "Studio Ghibli style night sky reflecting on calm ocean, bioluminescent plankton glowing in waves, starry sky with milky way, soft moonlight, dreamy magical atmosphere, anime painting, ultra detailed"),
    ("Kiki's Coastal Path", "Studio Ghibli style scenic coastal path with wildflowers, overlooking turquoise ocean, gentle breeze, fluffy white clouds, warm sunlight, green hills meeting the sea, anime watercolor landscape"),
    ("Totoro's Rainy Forest", "Studio Ghibli style lush green forest in soft rain, giant camphor tree, raindrops on leaves, misty atmosphere, deep greens, magical woodland feel, anime painting, cinematic, highly detailed"),
    ("Lavender Hills at Dusk", "Studio Ghibli style endless lavender fields on rolling hills at dusk, purple and orange sky, soft warm glow, gentle breeze, butterflies, dreamy romantic atmosphere, anime landscape art"),
]

def generate_via_pollinations(prompt: str, output_path: str) -> bool:
    try:
        print(f"[image] Pollinations API call...", flush=True)
        full_prompt = f"4K screensaver wallpaper. {prompt} 16:9 landscape, highly detailed, smooth gradients, no text, no watermark, no logo, professional ambient screensaver, peaceful and relaxing composition."
        url = f"https://gen.pollinations.ai/image/{requests.utils.quote(full_prompt)}?model=gptimage-large&width=1920&height=1080&key={POLLINATIONS_KEY}"
        resp = requests.get(url, timeout=180)
        print(f"[image] Response: {resp.status_code}, {len(resp.content)} bytes", flush=True)
        if resp.status_code == 200 and len(resp.content) > 1000:
            from PIL import Image
            img = Image.open(io.BytesIO(resp.content)).convert("RGB")
            img_ratio = img.width / img.height
            target_ratio = IMAGE_WIDTH / IMAGE_HEIGHT
            if img_ratio > target_ratio:
                new_h = IMAGE_HEIGHT
                new_w = int(new_h * img_ratio)
            else:
                new_w = IMAGE_WIDTH
                new_h = int(new_w / img_ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - IMAGE_WIDTH) // 2
            top = (new_h - IMAGE_HEIGHT) // 2
            img = img.crop((left, top, left + IMAGE_WIDTH, top + IMAGE_HEIGHT))
            from PIL import ImageFilter, ImageEnhance
            img = img.filter(ImageFilter.MedianFilter(size=3))
            img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=80, threshold=2))
            img = ImageEnhance.Contrast(img).enhance(1.1)
            img = ImageEnhance.Color(img).enhance(1.05)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path, format="JPEG", quality=95)
            print(f"[image] Saved: {os.path.getsize(output_path)} bytes", flush=True)
            return True
    except Exception as e:
        print(f"[image] Failed: {str(e)[:80]}", flush=True)
    return False

def generate_fallback_gradient(output_path: str):
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT))
    draw = ImageDraw.Draw(img)
    gradient_colors = [
        [(10, 10, 40), (40, 20, 80)],
        [(20, 40, 60), (60, 80, 100)],
        [(40, 20, 60), (80, 40, 100)],
        [(10, 30, 50), (50, 70, 90)],
    ]
    top_color, bottom_color = random.choice(gradient_colors)
    for y in range(IMAGE_HEIGHT):
        ratio = y / IMAGE_HEIGHT
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        draw.rectangle([(0, y), (IMAGE_WIDTH, y + 1)], fill=(r, g, b))
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="JPEG", quality=95)
    print(f"[image] Fallback gradient screensaver saved", flush=True)

def generate_screensaver_image(output_path: str):
    name, style = random.choice(SCREENSAVERS)
    print(f"[image] Generating: {name}", flush=True)
    print(f"[image] Style: {style[:80]}...", flush=True)

    if generate_via_pollinations(style, output_path):
        return output_path, name

    print("[image] Pollinations failed, using gradient fallback", flush=True)
    generate_fallback_gradient(output_path)
    return output_path, f"Screensaver {datetime.now().strftime('%Y-%m-%d')}"

if __name__ == "__main__":
    output_dir = Path("output/images")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(output_dir / "screensaver.jpg")
    image_path, name = generate_screensaver_image(output_path)
    meta = {"image_path": image_path, "name": name, "generated_at": datetime.now().isoformat()}
    with open(Path("output") / "latest_image.json", "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Image saved: {image_path}", flush=True)
    print(f"Name: {name}", flush=True)
