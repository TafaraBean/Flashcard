document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("flashcard-form").addEventListener("submit", function(event) {
      var textInput = document.getElementById("text_input").value.trim();
      var imageInput = document.getElementById("image_input").value.trim();

      if (textInput === "" && imageInput === "") {
          event.preventDefault(); // Prevent form submission
          alert("Please enter text or upload an image/pdf.");
      }

      // Check if an image is uploaded and validate its format
      if (imageInput !== "") {
          var allowedFormats = ["jpg", "jpeg", "png", "gif", "pdf"]; // Add more formats if needed
          var extension = imageInput.split('.').pop().toLowerCase();
          if (!allowedFormats.includes(extension)) {
              event.preventDefault(); // Prevent form submission
              alert("Please upload an image in JPG, JPEG, PNG, GIF or PDF format.");
          }
      }
  });
});