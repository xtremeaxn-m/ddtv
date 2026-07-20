import os, io, random, json, requests, sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

POLLINATIONS_KEY = os.getenv("POLLINATIONS_API_KEY", "sk_K98O2j1UlpALX9TBAoAuEdqxL1hpB7zh")
IMAGE_WIDTH = 3840
IMAGE_HEIGHT = 2160

TIMES_OF_DAY = ["sunrise", "golden hour", "midday", "sunset", "dusk", "twilight", "night", "dawn"]
SEASONS = ["spring", "summer", "autumn", "winter"]
WEATHERS = ["clear sky", "soft clouds", "misty", "gentle rain", "sunbeams", "foggy", "dramatic clouds", "light breeze"]
COLORS = ["warm golden", "cool blue", "soft pink", "vibrant green", "purple haze", "pastel", "deep amber", "silver gray"]
MOODS = ["peaceful", "serene", "dreamy", "calm", "tranquil", "gentle", "soothing", "ethereal"]

CATEGORIES = [
    ("Nature", "landscape, nature, wilderness"),
    ("Fantasy", "fantasy art, magical, whimsical"),
    ("Water", "ocean, lake, river, water scenery"),
    ("Forest", "forest, trees, woodland, jungle"),
    ("Mountains", "mountain range, alpine, peaks"),
    ("Night Sky", "night sky, stars, aurora, moonlight"),
    ("Tropical", "tropical paradise, island, beach"),
    ("Seasonal", "seasonal scenery, weather"),
]

SCREENSAVERS = [
    ("Spirited Meadow", "Nature", "magical meadow with glowing fireflies, rolling green hills, wildflowers, soft warm light"),
    ("Forest Spirit's Home", "Fantasy", "enchanted forest with giant ancient trees, tiny floating lights, mossy ground, magical atmosphere"),
    ("Howl's Floating Garden", "Fantasy", "floating garden in the sky, colorful flowers cascading down, soft clouds all around"),
    ("Secret Beach Cove", "Tropical", "secret beach cove, crystal clear turquoise water, white sand, tropical flowers, gentle waves"),
    ("Mountain Village Sunrise", "Mountains", "mountain village at sunrise, cozy houses, misty valleys, warm orange sky, terraced hills"),
    ("Whispering Bamboo Grove", "Forest", "bamboo forest, soft green light filtering through, gentle breeze, mossy stone path"),
    ("Ocean of Stars", "Night Sky", "night sky reflecting on calm ocean, bioluminescent waves, starry sky, milky way, moonlight"),
    ("Coastal Paradise", "Water", "scenic coastal cliffs with wildflowers, turquoise ocean, gentle waves, soft clouds"),
    ("Rainy Forest Retreat", "Forest", "lush green forest in soft rain, giant trees, raindrops on leaves, misty deep greens"),
    ("Lavender Hills at Dusk", "Seasonal", "endless lavender fields on rolling hills at dusk, purple and orange sky, soft warm glow"),
    ("Crystal Lake Morning", "Water", "crystal clear mountain lake reflecting snowy peaks, pine forest shore, mist rising"),
    ("Floating Islands Dream", "Fantasy", "floating islands in the sky with waterfalls cascading into clouds, golden light"),
    ("Aurora Over Snow", "Night Sky", "aurora borealis over snowy mountains, green and purple lights, starry night"),
    ("Autumn Path", "Seasonal", "forest path covered in golden and red autumn leaves, warm sunlight filtering through"),
    ("Hidden Waterfall Glen", "Nature", "hidden waterfall in a lush glen, rainbow in the mist, ancient mossy trees"),
    ("Desert Canyon Sunset", "Mountains", "dramatic desert canyon at sunset, warm orange and red rock formations, long shadows"),
    ("Cherry Blossom River", "Seasonal", "cherry blossom trees over a calm river, pink petals floating on water, soft spring light"),
    ("Snowy Mountain Peak", "Mountains", "snow-covered mountain peak at sunrise, alpine glow, pink and orange sky, dramatic"),
    ("Tropical Waterfall", "Tropical", "tropical jungle waterfall, exotic flowers, vibrant green, sunbeams through canopy"),
    ("Starlit Meadow Night", "Night Sky", "open meadow under a star-filled sky, fireflies, soft moonlight, peaceful night"),
    ("Coastal Sunset", "Water", "sunset over the ocean, warm golden and pink sky, gentle waves, silhouetted palm trees"),
    ("Enchanted Crystal Cave", "Fantasy", "glowing crystal cave with bioluminescent minerals, underground pool, magical blue light"),
    ("Misty Alpine Lake", "Mountains", "still alpine lake with mist rising at dawn, pine forest, mountain reflection"),
    ("Wildflower Meadow", "Nature", "endless wildflower meadow in spring, colorful blooms, green hills, blue sky"),
    ("Snowy Forest Path", "Forest", "snow-covered forest path, fresh snow on pine branches, soft winter light"),
]

def generate_via_pollinations(style_prompt: str, output_path: str, category: str = "") -> bool:
    try:
        seed = random.randint(10000, 99999)
        time = random.choice(TIMES_OF_DAY)
        season = random.choice(SEASONS)
        weather = random.choice(WEATHERS)
        color = random.choice(COLORS)
        mood = random.choice(MOODS)
        uid = datetime.now().strftime("%H%M%S")

        full_prompt = (
            f"Masterpiece 4K screensaver wallpaper, {category} theme. {style_prompt}, "
            f"{time}, {season}, {weather}, {color} tones, {mood} atmosphere, "
            f"16:9 landscape, highly detailed, smooth gradients, vibrant colors, "
            f"no text, no watermark, no logo, professional quality, cinematic. [{uid}]"
        )

        url = (
            f"https://gen.pollinations.ai/image/{requests.utils.quote(full_prompt)}"
            f"?model=gptimage-large&width=3840&height=2160"
            f"&seed={seed}&key={POLLINATIONS_KEY}"
        )

        print(f"[image] Seed: {seed} | {time} | {season} | {weather}", flush=True)
        resp = requests.get(url, timeout=180)
        print(f"[image] Response: {resp.status_code}, {len(resp.content)} bytes", flush=True)

        if resp.status_code == 200 and len(resp.content) > 1000:
            from PIL import Image, ImageFilter, ImageEnhance
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
    name, category, style = random.choice(SCREENSAVERS)
    print(f"[image] Generating: {name} [{category}]", flush=True)

    if generate_via_pollinations(style, output_path, category):
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
