// Assume flashcardsData is already defined or obtained from another source

MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true,
    processEnvironments: true,
    processRefs: true,
  },
  options: {
    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
    ignoreHtmlClass: 'tex2jax_ignore',
    processHtmlClass: 'tex2jax_process',
  },
  startup: {
    typeset: true,
    pageReady: function() {
    
      var batchSize = 5; // Number of flashcards to load at a time
      var startIndex = 0; // Index to track the starting point for loading
      
      // Function to load a batch of flashcards
      function loadFlashcards() {
        for (var i = startIndex; i < startIndex + batchSize && i < flashcardsData.length; i++) {
          var flashcardElement = createFlashcardElement(flashcardsData[i]);
          flashcardsContainer.appendChild(flashcardElement);
        }
  
        startIndex += batchSize;
      }
  
      // Load the initial batch of flashcards
      loadFlashcards();
  
      // Event listener for scrolling
      window.addEventListener('scroll', function() {
        // Check if the user has scrolled to the bottom of the page
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
          // Load more flashcards
          loadFlashcards();
        }
      });
  
      // Typeset all flashcards after the DOM is loaded
      MathJax.typesetPromise().then(function() {
        // Load the initial batch of flashcards
        loadFlashcards();
      });
    }
  }
};
var flashcardsContainer = document.getElementById('flashcards-container');
// Your other functions and code go here
// Function to create a flashcard element (similar to your existing implementation)
function createFlashcardElement(flashcard) {
  var flashcardElement = document.createElement('div');
  flashcardElement.className = 'flashcard';

  var questionElement = document.createElement('h2');
  questionElement.textContent = 'Question:';

  var questionContent = document.createElement('p');
  questionContent.innerHTML = flashcard.question;

  var toggleAnswerElement = document.createElement('h2');
  toggleAnswerElement.className = 'toggle-answer';
  toggleAnswerElement.textContent = 'Show Answer';
  toggleAnswerElement.onclick = function() {
      toggleAnswer(toggleAnswerElement);
  };

  var answerElement = document.createElement('div');
  answerElement.className = 'answer';
  answerElement.style.display = 'none'; // Ensure it starts hidden

  var answerContent = document.createElement('p');
  answerContent.innerHTML = flashcard.answer;
  answerContent.style.display = 'none'; // Ensure it starts hidden

  var copyMarkdownBtn = document.createElement('button');
  copyMarkdownBtn.className = 'copy-button';
  copyMarkdownBtn.textContent = 'Copy Flashcard as Markdown';
  copyMarkdownBtn.onclick = function() {
      copyFlashcardAsMarkdown(flashcard);
  };

  flashcardElement.appendChild(questionElement);
  flashcardElement.appendChild(questionContent);
  flashcardElement.appendChild(toggleAnswerElement);
  flashcardElement.appendChild(answerElement);
  flashcardElement.appendChild(answerContent);
  flashcardElement.appendChild(copyMarkdownBtn);

  // Use MathJax to typeset the content after it's added to the DOM
  MathJax.typesetPromise([questionContent, answerContent]).then(function() {
      // Once MathJax has finished typesetting, do nothing
  });

  return flashcardElement;
}

// Function to copy all flashcards as Markdown
function copyAllFlashcardsMarkdown() {
  var markdownContent = generateMarkdownAll();

  // Create a textarea element to hold the Markdown content
  var textarea = document.createElement('textarea');
  textarea.value = markdownContent;
  document.body.appendChild(textarea);

  // Select and copy the content to the clipboard
  textarea.select();
  document.execCommand('copy');

  // Remove the textarea
  document.body.removeChild(textarea);

  alert('All Flashcards copied as Markdown to clipboard!');
}

// Function to copy a single flashcard as Markdown
function copyFlashcardAsMarkdown(flashcard) {
  var markdownContent = `**Question:**\n${flashcard.question}\n\n**Answer:**\n${flashcard.answer}`;

  // Create a textarea element to hold the Markdown content
  var textarea = document.createElement('textarea');
  textarea.value = markdownContent;
  document.body.appendChild(textarea);

  // Select and copy the content to the clipboard
  textarea.select();
  document.execCommand('copy');

  // Remove the textarea
  document.body.removeChild(textarea);

  alert('Flashcard copied as Markdown to clipboard!');
}

// Function to generate Markdown for all flashcards
function generateMarkdownAll() {
  var markdownContent = '';

  flashcardsData.forEach(function(flashcard) {
      markdownContent += `**Question:**\n${flashcard.question}\n\n**Answer:**\n${flashcard.answer}\n\n---\n\n`;
  });

  return markdownContent;
}

// Variable to keep track of index and batch size
var startIndex = 0;
var batchSize = 5;

// Function to toggle answer visibility
function toggleAnswer(button) {
  var answerSection = button.nextElementSibling;
  var answerContent = answerSection.nextElementSibling;
  answerSection.style.display = (answerSection.style.display === 'none' || answerSection.style.display === '') ? 'block' : 'none';
  answerContent.style.display = (answerContent.style.display === 'none' || answerContent.style.display === '') ? 'block' : 'none';

  button.textContent = (answerSection.style.display === 'none') ? 'Show Answer' : 'Hide Answer';
}

// Function to download flashcards as a text file
function downloadFlashcards() {
  var flashcardsText = generateFlashcardsText(flashcardsData);
  var filename = 'flashcards.txt'; // Set the filename for the downloaded file

  // Create a Blob containing the flashcards text
  var blob = new Blob([flashcardsText], {
      type: 'text/plain'
  });

  // Create a temporary anchor element
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;

  // Programmatically trigger a click event on the anchor element
  a.click();

  // Clean up
  URL.revokeObjectURL(a.href);
}

// Function to generate text for all flashcards
function generateFlashcardsText(flashcardsData) {
  var flashcardsText = '';

  // Generate text content for each flashcard
  flashcardsData.forEach(function(flashcard) {
      flashcardsText += `${flashcard.question}:${flashcard.answer}\n\n`;
  });

  return flashcardsText;
}

