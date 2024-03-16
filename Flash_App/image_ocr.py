import pytesseract
from PIL import Image
from texify.inference import batch_inference
from texify.model.model import load_model
from texify.model.processor import load_processor
#from pix2tex.cli import LatexOCR

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_image_for_ocr(image_file):
    # Open the image file
    model = load_model()
    processor = load_processor()
    image = Image.open(image_file)

    # Check for compression need
    #if image.size[0] * image.size[1] > 1024 * 1024:  # Multiply width and height
       #image = compress_image(image)

    #model = LatexOCR()
    #text = print(model(image))

    # Perform OCR
    #text = pytesseract.image_to_string(image)
    results = batch_inference([image],model,processor)

    return results

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


