# Flash Gen

Flash Gen is a Django web app that turns study material into flashcards. You paste your notes (LaTeX is supported) or upload photos, screenshots or PDFs of them. The app reads uploads with Tesseract OCR and asks OpenAI's GPT-4o to write question-and-answer cards. It then shows the cards with the maths rendered, ready to copy or download for [Anki](https://apps.ankiweb.net/). It can also turn the same input into summary notes and answer follow-up questions about them.

This is a personal project.

## Example

| Text pasted into the input box | Card generated from it |
|---|---|
| ![LaTeX notes pasted as input](static/img/latex%20before.webp) | ![Rendered flashcard with the answer shown](static/img/latex%20after.webp) |

## Features

**Input**

- A text box that accepts plain text and LaTeX.
- Upload one or more images or PDFs. The browser check allows `.jpg`, `.jpeg`, `.png`, `.gif` and `.pdf`.
  - Images go through Tesseract OCR. Large images (over about 1 megapixel and wider than 1024 px) are first scaled down to 1024 px wide.
  - PDFs are converted to page images with pdf2image, then OCR'd page by page. This happens even when the PDF already contains selectable text.
- Text from the box and from every uploaded file is combined into a single request.

**Flashcards** ("Submit to Flashcards")

- GPT-4o is prompted to break the material into single-concept `Question: ... Answer: ...` pairs and to keep the LaTeX. `Flash_App/utils.py` then parses the reply into cards.
- The flashcard page renders LaTeX with MathJax 3. Each answer stays hidden until you click Show Answer, and cards load five at a time as you scroll.
- Export:
  - copy a single card as Markdown
  - tick several cards and copy them as `question;answer` lines for Anki
  - download all cards (`flashcards.txt`) or only the ticked ones (`selected_flashcards.txt`) as semicolon-separated text. The download rewrites `$...$` maths to `\(...\)` for Anki's MathJax and turns line breaks into `<br>`.

**Notes** ("Submit to Notes")

- GPT-4o turns the same input into summary notes in Markdown with LaTeX. The notes appear as raw text in a text area.
- A follow-up box sends the notes and your question to GPT-4, which answers and shows its reasoning. The answer replaces the notes on the page.

**Long input**

- If the input is too long for the model, the app returns an error asking you to shorten it. The home page suggests keeping input under about 3,000 words.

## Tech stack

- Python 3.12, Django 5.0
- OpenAI Python SDK 1.x: `gpt-4o` for flashcards and notes, `gpt-4` for follow-up questions
- Tesseract OCR (via `pytesseract`) and Pillow for images; `pdf2image` with Poppler for PDFs
- `python-dotenv` to load settings from a `.env` file
- Django templates, plain JavaScript, MathJax 3 (from the jsDelivr CDN) and Google Fonts
- SQLite, the Django default. The app has no models of its own, so nothing you submit is stored.

## Project structure

```
flashcard/
├── manage.py
├── FlashCard/                 Django project package
│   ├── settings.py            settings; reads SECRET_KEY, OPENAI_API_KEY and HF_TOKEN from the environment / .env
│   ├── urls.py                URL routes (below)
│   └── wsgi.py, asgi.py       server entry points
├── Flash_App/                 the application
│   ├── views.py               OCR helpers, OpenAI calls and the four views
│   ├── utils.py               parse_questions_answers(): splits the model reply into cards
│   ├── image_ocr.py           duplicate of the OCR helpers in views.py (nothing imports it)
│   ├── temp.py                scratch script that tests Google's Gemma 2B with Transformers (not used by the app)
│   └── models.py, admin.py, tests.py   empty Django scaffolding
├── templates/
│   ├── index.html             home page and input form
│   ├── result.html            flashcard viewer (MathJax, show/hide, select, copy, download)
│   └── notes.html             generated notes and follow-up form
├── static/
│   ├── index.css, index.js    home page styles and upload validation
│   ├── result.css             flashcard page styles
│   ├── result.js              standalone copy of the flashcard script without the select features (no template loads it)
│   └── img/                   before/after example images used on the home page
├── training_data.json         three example records in OpenAI chat fine-tuning format (JSON Lines); not used by the app
├── compressed_image.jpg/.png  two photos of book pages, apparently left over from OCR testing (not used by the app)
└── requirements.txt           full pip freeze of the author's environment (see Getting started)
```

| Route | View | What it does |
|---|---|---|
| `/` | `index` | Input form |
| `/process_text/` | `process_text` | OCR + GPT-4o, then renders the flashcard page (POST only) |
| `/notes/` | `notes` | OCR + GPT-4o, then renders the notes page |
| `/clarify/` | `clarify` | Sends a follow-up question about the notes to GPT-4 |
| `/admin/` | Django admin | Default admin site; Flash_App registers no models |

## Getting started

### Prerequisites

- **Python 3.12.** The project was built on 3.12. Django 5.0.1 supports 3.10 to 3.12, and the pinned Pillow 10.2.0 has no wheels for 3.13.
- **An OpenAI API key** with access to `gpt-4o` and `gpt-4`. Each submission is a paid API call.
- **Tesseract OCR and Poppler.** You only need these to upload images or PDFs. Text pasted into the box works without them.

| OS | Install Tesseract and Poppler |
|---|---|
| Windows | Install Tesseract to the default `C:\Program Files\Tesseract-OCR\`, which is the path `views.py` expects. Download Poppler for Windows and add its `bin` folder to `PATH`. |
| macOS | `brew install tesseract poppler` |
| Ubuntu / Debian | `sudo apt install tesseract-ocr poppler-utils` |

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/TafaraBean/flashcard.git
cd flashcard
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 2. Install the Python packages

```bash
pip install Django==5.0.1 openai==1.10.0 httpx==0.26.0 python-dotenv==1.0.1 pytesseract==0.3.10 pillow==10.2.0 pdf2image==1.17.0 pdfplumber==0.11.4
```

These are the packages that `settings.py` and `views.py` import, at the versions pinned in `requirements.txt`. `httpx` is pinned because `openai` 1.10 does not work with httpx 0.28 or newer.

About `requirements.txt`: it is a `pip freeze` of the author's whole Windows environment. It lists about 170 packages, including PyTorch, Transformers, spaCy, Streamlit and Qt bindings that the web app does not use. `pip install -r requirements.txt` currently fails for two reasons:

- `huggingface-cli==0.1` is not available on PyPI.
- `pywin32` and `pypiwin32` install only on Windows.

Use the command above instead.

### 3. Set environment variables

Create a `.env` file in the project root, next to `manage.py`. `settings.py` loads it with python-dotenv, and `.env` is already in `.gitignore`.

```dotenv
SECRET_KEY=<a long random string>
OPENAI_API_KEY=<your OpenAI API key>
```

| Variable | Required | Purpose |
|---|---|---|
| `SECRET_KEY` | Yes | Django's signing key. Django will not serve requests while it is empty. Generate one with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `OPENAI_API_KEY` | Yes | All AI calls. `views.py` creates the OpenAI client as soon as it is imported, so `manage.py migrate` and `runserver` fail with an OpenAI error if the key is missing. |
| `HF_TOKEN` | No | `settings.py` reads it, but only the scratch script `Flash_App/temp.py` uses it. The web app does not. |

### 4. Adjust settings for local development

`FlashCard/settings.py` and `views.py` are set up for the author's own machines. The settings target an Ubuntu server, and the Tesseract path targets a Windows PC. Make these local changes and don't commit them:

- **`DEBUG = False`.** With debug off, `runserver` doesn't serve CSS, JavaScript or images. Pages appear unstyled and the upload check in `index.js` doesn't run. You have two options:
  - Set `DEBUG = True` locally. You also get full tracebacks instead of a generic error page.
  - Leave it and start the server with `--insecure` (see step 5), which serves static files while `DEBUG` is off.
- **`STATIC_ROOT = '/home/ubuntu/Flashcard/staticfiles/'`.** This is an absolute path on the author's server and only `collectstatic` uses it, so you can ignore it locally. To deploy somewhere else, point it at a folder on that machine first, for example `BASE_DIR / 'staticfiles'`.
- **`ALLOWED_HOSTS = ['*']`.** Fine for local use. In production, limit it to your own domain.
- **The Tesseract path.** `Flash_App/views.py` sets `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`. On macOS or Linux, either comment out that line so pytesseract finds `tesseract` on your `PATH`, or set it to the output of `which tesseract`. On Windows, change it only if you installed Tesseract somewhere else. A wrong path makes every image upload end in a server error, and PDF uploads come back with no text.

### 5. Run

```bash
python manage.py migrate
python manage.py runserver              # if you set DEBUG = True
python manage.py runserver --insecure   # if you left DEBUG = False
```

Then open <http://127.0.0.1:8000/>.

`migrate` only creates tables for Django's built-in apps (admin, auth, sessions), because Flash_App has no models.

## Notes and limitations

- **Nothing is saved.** Cards and notes exist only in the page you are viewing. Refreshing the results page sends the form again and creates a new set.
- **All input goes to OpenAI in one request.** Very long input fails, and every submission costs API credit.
- **Card parsing is strict.** It relies on the model answering in the exact `Question:` / `Answer:` format. If any question has no `Answer:` (or more than one), the whole request fails with "Error processing text."
- **Errors are raw JSON.** When the OpenAI call or the card parsing fails, the browser shows a bare JSON response instead of an error page.
- **Notes are not rendered.** Their Markdown and LaTeX show as source text.
- **Follow-ups forget the original notes.** Each follow-up sends only the text currently on the page. After the first one, that is the previous answer, not the notes.
- **OCR quality depends on Tesseract.** Clear screenshots of PDF pages work best. Equations in images are not converted to LaTeX; the home page points to MathPix for that.
- **The pages load Google AdSense.** `templates/index.html` and `templates/result.html` include an AdSense script with the author's publisher ID. Remove it if you host your own copy.
- **There are no automated tests.** `Flash_App/tests.py` is empty.
