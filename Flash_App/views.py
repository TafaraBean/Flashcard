from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from Flash_App.image_ocr import process_image_for_ocr
from openai import OpenAI
from django.views.decorators.http import require_POST
from .utils import *


client = OpenAI(api_key=settings.OPENAI_API_KEY)

def index(request):
    return render(request, 'index.html')

@require_POST
def process_text(request):
        # Check if text input is provided
        text_input = request.POST.get('text_input', '')
        
        # Check if an image file is uploaded
        if 'image_inputs' in request.FILES:
            image_texts = []
            for image_file in request.FILES.getlist('image_inputs'):
                image_text = process_image_for_ocr(image_file)
                image_texts.append(image_text)
            combined_image_text = '\n'.join(image_texts)
        else:
            combined_image_text=""   
            
            # Process the image for OCR
        combined_text = text_input+"\n"+combined_image_text   
            
          

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






