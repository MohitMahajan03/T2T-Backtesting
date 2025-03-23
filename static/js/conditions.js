// select elements for attribute setting
var entry_criteria = document.querySelectorAll("#entry_criteria");
var exit_criteria = document.querySelectorAll("#exit_criteria");
var msl = document.querySelectorAll("#msl");
var tsl1 = document.querySelectorAll("#tsl1");
var tsl2 = document.querySelectorAll("#tsl2");
var days = document.querySelectorAll("#days");


var stopLossInputs = document.querySelectorAll(".stop-loss-group");
var criteriaInputs = document.querySelectorAll(".criteria-group");

var note = document.querySelectorAll(".note");

note.forEach(function(input) {
  input.style.display = "none";
});
// Show no stop loss inputs
stopLossInputs.forEach(function(input) {
  input.style.display = "none";
});

criteriaInputs.forEach(function(input) {
  input.style.display = "none";
});

document.getElementById("system").addEventListener("change", function() {
  var selectedSystem = this.value;



  // Show specific stop loss inputs based on the selected system
  if (selectedSystem === "0") {

      criteriaInputs.forEach(function(input) {
        input.style.display = "none";

    }, this);
      
      // Show no stop loss inputs
      stopLossInputs.forEach(function(input) {
        input.style.display = "none";

    });

  } else if (selectedSystem === "1") {
      msl[0].removeAttribute('required');
      tsl1[0].setAttribute('required', '');
      tsl2[0].setAttribute('required', '');
      days[0].removeAttribute('required');
      entry_criteria[0].removeAttribute('required');
      exit_criteria[0].removeAttribute('required');

      // Show the required inputs for system 1
      criteriaInputs[0].style.display = "none";
      criteriaInputs[1].style.display = "none";

      stopLossInputs[0].style.display = "none";
      stopLossInputs[1].style.display = "block";
      stopLossInputs[2].style.display = "block";
      stopLossInputs[3].style.display = "none";
      stopLossInputs[4].style.display = "block";
      stopLossInputs[5].style.display = "none";
      note[0].style.display = "none";

  // } else if (selectedSystem === "2") {
  //     msl[0].setAttribute('required', '');
  //     tsl1[0].removeAttribute('required');
  //     tsl2[0].removeAttribute('required');
  //     days[0].setAttribute('required', '');
  //     entry_criteria[0].removeAttribute('required');
  //     exit_criteria[0].removeAttribute('required');
  //     // Show the required inputs for system 2
  //     criteriaInputs[0].style.display = "none";
  //     criteriaInputs[1].style.display = "none";

  //     stopLossInputs[0].style.display = "block";
  //     stopLossInputs[1].style.display = "none";
  //     stopLossInputs[2].style.display = "none";
  //     stopLossInputs[3].style.display = "block";
  //     stopLossInputs[4].style.display = "none";
  //     stopLossInputs[5].style.display = "block";
  //     note[0].style.display = "block";
  } else if (selectedSystem === "2") {
    msl[0].setAttribute('required', '');
    tsl1[0].removeAttribute('required');
    tsl2[0].removeAttribute('required');
    days[0].removeAttribute('required');

    entry_criteria[0].removeAttribute('required');
    exit_criteria[0].removeAttribute('required');
    // Show the required inputs for system 3
    criteriaInputs[0].style.display = "none";
    criteriaInputs[1].style.display = "none";

    stopLossInputs[0].style.display = "block";
    stopLossInputs[1].style.display = "none";
    stopLossInputs[2].style.display = "none";
    stopLossInputs[3].style.display = "none";
    stopLossInputs[4].style.display = "none";
    stopLossInputs[5].style.display = "block";
    note[0].style.display = "none";

  } else if (selectedSystem === "3") {
      msl[0].setAttribute('required', '');
      tsl1[0].removeAttribute('required');
      tsl2[0].removeAttribute('required');
      days[0].removeAttribute('required');

      entry_criteria[0].setAttribute('required', '');
      exit_criteria[0].setAttribute('required', '');
      // Show the required inputs for system 3
      criteriaInputs[0].style.display = "block";
      criteriaInputs[1].style.display = "block";

      stopLossInputs[0].style.display = "block";
      stopLossInputs[1].style.display = "none";
      stopLossInputs[2].style.display = "none";
      stopLossInputs[3].style.display = "none";
      stopLossInputs[4].style.display = "none";
      stopLossInputs[5].style.display = "block";
      note[0].style.display = "none";
  }
  // Add more conditions for other system options if needed
});

// set max date input to current date
const today = new Date().toISOString().split('T')[0];
document.getElementById("start_date").setAttribute("max", today);
document.getElementById("end_date").setAttribute("max", today);

// set min date input to start date
document.getElementById("start_date").addEventListener("change", function() {
  var start_date = document.getElementById("start_date").value;
  document.getElementById("end_date").setAttribute("min", start_date);
});

// ----------------------------------------------------- function to get suggestions from the server for scripcode
function getSuggestions(input) {
  // Get the suggestions box element
  var suggestionsBox = document.getElementById("suggestions-box");

  // Hide the suggestions box if the input is empty
  if (input.trim() === '') {
      suggestionsBox.style.display = "none";
      return;
  }
  
  // Make an AJAX request to the server with the user input
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/getSuggestions?input=" + input, true);
  xhr.onreadystatechange = function() {
      if (xhr.readyState == 4 && xhr.status == 200) {
          // Parse the JSON response from the server
          var suggestions = JSON.parse(xhr.responseText);
          
          // Clear previous suggestions
          suggestionsBox.innerHTML = "";
          
          // Populate the suggestions box with new suggestions
          suggestions.forEach(function(suggestion) {
              var suggestionItem = document.createElement("div");
              suggestionItem.textContent = suggestion;
              suggestionItem.classList.add("suggestion-item");
              
              // Handle suggestion item click (optional)
              suggestionItem.addEventListener("click", function() {
                  document.getElementById("scripcode").value = suggestion;
                  suggestionsBox.style.display = "none";
              });
              
              suggestionsBox.appendChild(suggestionItem);
          });
          
          // Show the suggestions box
          suggestionsBox.style.display = "block";
      }
  };
  xhr.send();
}


//--------------------------------------------------------- Download the CSV file
var filename = document.getElementById("filename").value;
// Add event listener to the download button
document.getElementById("download").addEventListener("click", function(event) {
  // Prevent default behavior of the anchor tag
  event.preventDefault();

  // Create a new anchor element
  var downloadLink = document.createElement("a");
  
  // Set the href attribute to the download endpoint URL
  downloadLink.href =  `/getPlotCSV/${filename}`;
  
  
  // Append the anchor element to the body
  document.body.appendChild(downloadLink);
  
  // Programmatically trigger a click event on the anchor element
  downloadLink.click();
  
  // Remove the anchor element from the DOM
  document.body.removeChild(downloadLink);
  
  setTimeout(function() {
    // Make an asynchronous request to the deleteFile route
    fetch(`/deleteFile/${filename}`)
    .then((response) => response.text())
    .then((message) => console.log(message))
    .catch((error) => console.error("Error:", error));
    
    // Reload the page after the download is initiated
    location.reload();
  }, 1000);

});
  

//---------------------------------------- Check if the page was loaded from a form submission
if (window.history.replaceState) {
  // Prevent form resubmission and perform a hard refresh
  window.history.replaceState(null, null, window.location.href);
} else {
  // If window.history.replaceState is not supported, fallback to a regular reload
  window.location.href = window.location.href;
}
