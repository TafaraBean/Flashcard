from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
import json
from openai import OpenAI
from django.views.decorators.http import require_POST
from .utils import *
from io import BytesIO
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import pdfplumber



client = OpenAI(api_key=settings.OPENAI_API_KEY)

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

    return image




def extract_text_from_pdf(pdf_file):
    try:
        # Convert InMemoryUploadedFile to BytesIO
        pdf_bytes = BytesIO(pdf_file.read())
        
        # Initialize text storage
        text = ""
        text_found = False
        
        # Attempt to extract text with pdfplumber from the first 3 pages
        with pdfplumber.open(pdf_bytes) as pdf:
            num_pages = min(len(pdf.pages), 3)  # Limit to first 3 pages
            for page_num in range(num_pages):
                page = pdf.pages[page_num]
                page_text = page.extract_text()
                if page_text.strip():
                    text_found = True
                text += page_text or ""
                text += "\n"
                print(f"Extracted text from page {page_num + 1}: {page_text}")

        if text_found:  # If any text was found, process the entire document
            pdf_bytes.seek(0)  # Reset file pointer to start
            with pdfplumber.open(pdf_bytes) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    text += page_text or ""
                    text += "\n"
            return text
        
        # If no text is extracted from the first 3 pages, use OCR
        print("No text extracted from the first 3 pages. Using OCR...")
        
        pdf_bytes.seek(0)  # Reset file pointer to start
        images = convert_from_bytes(pdf_bytes.read())
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"
        
        print("Text after OCR: " + text)
        return text
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""



def index(request):
    return render(request, 'index.html')

@require_POST
def process_text(request):
    text_input = request.POST.get('text_input', '')

    # Check if an image file or PDF is uploaded
    if 'image_inputs' in request.FILES:
        image_texts = []
        for file in request.FILES.getlist('image_inputs'):
            if file.name.lower().endswith('.pdf'):
                # Extract text from the PDF
                pdf_text = extract_text_from_pdf(file)
                image_texts.append(pdf_text)
            else:
                # Process the image for OCR
                image_text = process_image_for_ocr(file)
                image_texts.append(image_text)

        combined_image_text = '\n'.join(image_texts)
    else:
        combined_image_text = ""

    combined_text = text_input + "\n" + combined_image_text

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant, skilled in taking all the text that is given to you and then creating flashcards from it. include mathjax/LaTeX code in your response (there is code in the backend that will render it for you) .understand all the text. all the text should be used, don't be lazy. You will generate a question for each answer and display them together. the answers should be concise. The questions should not include the answer. Break down information into single concepts. Emphasize key terms within each concept.Maintain a consistent format across all flashcards.Formulate questions that require active thinking. Encourage remembering, not just recognizing information. Start with fundamental concepts and gradually increase complexity. Connect new information to previously learned material. for example: the format of your response should be as follows'Question: (the question you generate)?Answer: (the answer to the question).'. for every question there must be an answer. 'Answer:' and 'Question:' will act as crucial delimiters "},
                {"role": "user", "content": combined_text}
            ]
        )
        print(completion.choices[0].message.content)

        # Extract questions and answers from the completion
        flashcards = parse_questions_answers(completion.choices[0].message.content)
        flashcards_json = json.dumps(flashcards)

        return render(request, 'result.html', {'flashcards_json': flashcards_json})

    except Exception as e:
        error_message = str(e)
        if 'context_length_exceeded' in error_message:
            return JsonResponse({'error': 'Text exceeds token limit. Please reduce the text size.'}, status=400)
        else:
            return JsonResponse({'error': 'Error processing text.'}, status=500)
            

def notes(request):
    text_input = request.POST.get('text_input', '')
    combined_image_text = ''

    # Check if an image file or PDF is uploaded
    # Check if an image file or PDF is uploaded
    if 'image_inputs' in request.FILES:
        image_texts = []
        for file in request.FILES.getlist('image_inputs'):
            if file.name.lower().endswith('.pdf'):
                # Extract text from the PDF
                pdf_text = extract_text_from_pdf(file)
                image_texts.append(pdf_text)
            else:
                # Process the image for OCR
                image_text = process_image_for_ocr(file)
                image_texts.append(image_text)

        combined_image_text = '\n'.join(image_texts)
    else:
        combined_image_text = ""

    combined_text = text_input + "\n" + combined_image_text    
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant skilled at making notes. the notes should summarize the content without losing the meaning of the content.take note of all definitions and their meanings."},
                {"role": "user", "content": combined_text}
            ]
        )
        #print(completion.choices[0].message.content)
        response  = completion.choices[0].message.content
        return render(request, 'notes.html', {'response': response})
       
    except Exception as e:
        error_message = str(e)
        if 'context_length_exceeded' in error_message:
            return JsonResponse({'error': 'Text exceeds token limit. Please reduce the text size.'}, status=400)
        else:
            return JsonResponse({'error': 'Error processing text.'}, status=500)  
    
    
        
def clarify(request):
    clarification_input = request.POST.get('clarification_input', '')
    previous_response = request.POST.get('previous_response', '')

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": " You are a helpful assistant skilled at creating notes. If you are posed with a question, asnwer it while documenting your reasoning steps. don't convert/render any latex code."},
                {"role": "user", "content": previous_response + "\nClarification: " + clarification_input}
            ]
        )
        response = completion.choices[0].message.content
        return render(request, 'notes.html', {'response': response})

    except Exception as e:
        error_message = str(e)
        if 'context_length_exceeded' in error_message:
            return JsonResponse({'error': 'Text exceeds token limit. Please reduce the text size.'}, status=400)
        else:
            return JsonResponse({'error': 'Error processing text.'}, status=500)