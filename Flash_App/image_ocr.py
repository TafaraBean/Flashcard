import pytesseract
from PIL import Image,ImageEnhance,ImageOps 
import cv2

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_image_for_ocr(image_file):
    # Open the image file
    image = Image.open(image_file)
    grayscale_image = image.convert('L')
    enhancer = ImageEnhance.Contrast(grayscale_image)
    enhanced_image = enhancer.enhance(1.5)
    thresh = 127
    binary_image = enhanced_image.point(lambda p: 255 if p > thresh else 0)


    #binary_image.save("binarry_image.jpg")
    #deskewed_image = ImageOps.straighten(binary_image)
    # Check for compression need
    # if image.size[0] * image.size[1] > 1024 * 1024:  # Multiply width and height
    #     image = compress_image(image)


    # Perform OCR
    text = pytesseract.image_to_string(binary_image)

    return text

def compress_image(image):
    # Resize image if needed
    max_width = 1024  # Adjust as needed
    if image.width > max_width:
        image_return = image.resize((max_width, image.height * max_width // image.width), Image.LANCZOS)

    # Save as JPEG with quality optimization
    
    return image_return



