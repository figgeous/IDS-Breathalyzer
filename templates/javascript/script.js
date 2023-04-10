// Get the form and button elements
const form = document.querySelector('form');
const button = document.querySelector('#create-account');

// Add an event listener to the button
button.addEventListener('click', (event) => {
  // Prevent the form from submitting
  event.preventDefault();

  // Get the values from the form fields
  const username = form.username.value;
  const password = form.password.value;
  const dob = form.dob.value;

  // Create the user dictionary
  const user = { username, password, dob };

  // Send the user data to the server using AJAX
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/create_account');
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onload = function() {
    if (xhr.status === 200) {
      console.log('User data saved successfully!');
    } else {
      console.error('Error saving user data:', xhr.status);
    }
  };
  xhr.send(JSON.stringify(user));
});
