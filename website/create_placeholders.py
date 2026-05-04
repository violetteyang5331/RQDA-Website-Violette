from PIL import Image
import os

gallery_path = "static/images/gallery"

for i in range(52, 56):
    png_path = os.path.join(gallery_path, f"gallery{i}.webp")
    placeholder_path = os.path.join(gallery_path, f"gallery{i}_placeholder.webp")
    
    if os.path.exists(png_path):
        img = Image.open(png_path)
        img = img.resize((20, 20))  # tiny!
        img.save(placeholder_path, "webp", quality=20)
        print(f"Created placeholder for gallery{i}")

print("Done!")