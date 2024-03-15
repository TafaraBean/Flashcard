import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_image_for_ocr(image_file):
    # Open the image file
    image = Image.open(image_file)

    # Check for compression need
    if image.size[0] * image.size[1] > 1024 * 1024:  # Multiply width and height
        image = compress_image(image)


    # Perform OCR
    text = pytesseract.image_to_string(image)

    return text

def compress_image(image):
    # Resize image if needed
    max_width = 1024  # Adjust as needed
    if image.width > max_width:
        image = image.resize((max_width, image.height * max_width // image.width), Image.LANCZOS)

    # Save as JPEG with quality optimization
    image.save("compressed_image.jpg", optimize=True, quality=85)

    # Reload the compressed image
    compressed_image = Image.open("compressed_image.jpg")
    return compressed_image
