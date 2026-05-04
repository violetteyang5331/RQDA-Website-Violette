from PIL import Image
import os

gallery_path = "static/images/gallery"

for i in range(52, 56):
    png_path = os.path.join(gallery_path, f"gallery{i}.jpg")
    webp_path = os.path.join(gallery_path, f"gallery{i}.webp")
    
    if os.path.exists(png_path):
        img = Image.open(png_path)
        img.save(webp_path, "webp", quality=80)
        print(f"Converted gallery{i}.jpg → gallery{i}.webp")
    else:
        print(f"Skipped: gallery{i}.jpg not found")

print("Done!")