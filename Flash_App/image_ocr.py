import pytesseract
from PIL import Image
import os

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'






def process_image_for_ocr(image_file):
    # Open the image file
    image = Image.open(image_file)

    # Check for compression need and perform iterative compression
    if image.size[0] * image.size[1] > 1024 * 1024:
        image = compress_image(image)

    # Perform OCR
    text = pytesseract.image_to_string(image)

    return text

def compress_image(image):
    # Try lossless PNG compression first
    image.save("compressed_image.png", optimize=True)
    compressed_image_path = "compressed_image.png"

    # Iterative compression with quality and resizing adjustments
    while os.path.getsize(compressed_image_path) > 200 * 1024:  # Target size of 200kb
        # Attempt JPEG with decreasing quality (prioritize lossless)
        quality = max(50, 10 - (os.path.getsize(compressed_image_path) // (1024 * 50)))  # Adjust quality decrease logic
        image.save(compressed_image_path, format="JPEG", optimize=True, quality=quality)

        # If JPEG doesn't suffice, try resizing with control
        if os.path.getsize(compressed_image_path) > 200 * 1024:
            resize_factor = 0.8  # Initial resize reduction by 20% (adjust as needed)
            while os.path.getsize(compressed_image_path) > 200 * 1024:
                max_width = int(image.width * resize_factor)
                image = image.resize((max_width, image.height * max_width // image.width), Image.LANCZOS)
                resize_factor *= 0.9  # Gradually decrease resize factor (adjust reduction)
                image.save(compressed_image_path, format="JPEG", optimize=True, quality=quality)

            # If resizing still doesn't meet target size, use minimum quality JPEG
            if os.path.getsize(compressed_image_path) > 200 * 1024:
                image.save(compressed_image_path, format="JPEG", optimize=True, quality=50)

    # Reload the compressed image
    compressed_image = Image.open(compressed_image_path)
    return compressed_image
