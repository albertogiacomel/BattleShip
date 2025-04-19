document.addEventListener('dragstart', function (event) {
  event.preventDefault();
});



document.ready(function () {
    ("#show-options-menu").click(function () {
      $("#options-menu").show();
    });

    ("#hide-options-menu").click(function () {
      ("#options-menu").hide();
    });
});

// Function to show the options menu
function showOptionsMenu() {
    document.getElementById('options-menu').style.display = 'block';
  }
  
  // Function to hide the options menu
  function hideOptionsMenu() {
    document.getElementById('options-menu').style.display = 'none';
  }
  
  // Function to handle cell clicks
  function onCellClick(cell) {
    // Check if the cell has already been fired at
    const cellContent = cell.innerHTML.trim();
    if (cellContent.includes('water.png') || cellContent.includes('fire.png')) {
      // Cell already fired at - show an error message
      showMessage('Hai già sparato in questa posizione!', 'error');
      return;
    }
  
    // Get row and column from the cell's data attributes
    const row = cell.getAttribute('data-row');
    const col = cell.getAttribute('data-col');
    
    // Set the values in the form
    document.getElementById('row').value = row;
    document.getElementById('col').value = col;
    
    // Submit the form
    document.getElementById('fire').click();
  }
  
  // Function to show message to the user
  function showMessage(message, type) {
    // Create or get the message container
    let messageContainer = document.getElementById('message-container');
    if (!messageContainer) {
      messageContainer = document.createElement('div');
      messageContainer.id = 'message-container';
      messageContainer.style.position = 'fixed';
      messageContainer.style.top = '20px';
      messageContainer.style.left = '50%';
      messageContainer.style.transform = 'translateX(-50%)';
      messageContainer.style.padding = '10px 20px';
      messageContainer.style.borderRadius = '5px';
      messageContainer.style.fontWeight = 'bold';
      messageContainer.style.zIndex = '1000';
      document.body.appendChild(messageContainer);
    }
    
    // Set message style based on type
    if (type === 'error') {
      messageContainer.style.backgroundColor = '#f8d7da';
      messageContainer.style.color = '#721c24';
      messageContainer.style.border = '1px solid #f5c6cb';
    } else {
      messageContainer.style.backgroundColor = '#d4edda';
      messageContainer.style.color = '#155724';
      messageContainer.style.border = '1px solid #c3e6cb';
    }
    
    // Set the message text
    messageContainer.textContent = message;
    
    // Show the message
    messageContainer.style.display = 'block';
    
    // Hide the message after 3 seconds
    setTimeout(() => {
      messageContainer.style.display = 'none';
    }, 3000);
  }
  
  // Initialize event listeners when the DOM is loaded
  document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for options buttons
    const showOptionsBtn = document.getElementById('show-options-menu');
    const hideOptionsBtn = document.getElementById('hide-options-menu');
    
    if (showOptionsBtn) {
      showOptionsBtn.addEventListener('click', showOptionsMenu);
    }
    
    if (hideOptionsBtn) {
      hideOptionsBtn.addEventListener('click', hideOptionsMenu);
    }
    
    // Add AJAX form submission to handle errors
    const fireForm = document.querySelector('form[action="/fire"]');
    if (fireForm) {
      fireForm.addEventListener('submit', function(event) {
        // Only intercept regular Fire button clicks, not Random
        if (event.submitter && event.submitter.name === 'Fire') {
          event.preventDefault();
          
          const formData = new FormData(this);
          
          fetch('/fire', {
            method: 'POST',
            body: formData
          })
          .then(response => response.json().catch(() => ({ redirect: true })))
          .then(data => {
            if (data.status === 'error') {
              showMessage(data.message, 'error');
            } else {
              // Redirect to refresh the page - it's a regular form submission response
              window.location.reload();
            }
          })
          .catch(error => {
            console.error('Error:', error);
            window.location.reload(); // Fallback: reload the page
          });
        }
      });
    }
  });

  