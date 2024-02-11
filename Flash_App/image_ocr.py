# Flash_App/image_ocr.py
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_image_for_ocr(image_file):
    # Open the image file using PIL (Python Imaging Library)
    image = Image.open(image_file)
    
    # Use pytesseract to perform OCR on the image and extract text
    text = pytesseract.image_to_string(image)
    # Return the extracted text
    return text
