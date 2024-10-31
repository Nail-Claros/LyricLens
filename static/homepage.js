const toggleButton =  document.getElementById("btn-toggle");
const modal = document.getElementById('modal');
const closeModal = document.querySelector('.close');
let isListening = false;

toggleButton.addEventListener('click', () => 
    {
        isListening = !isListening;

        if(isListening)
        {
            toggleButton.classList.add('active');
        }
        else
        {
            toggleButton.classList.remove('active');
        }
    });


closeModal.addEventListener('click', () =>
    {
        modal.style.display = "none";
    });
    function disableButton(event) {
        event.preventDefault();  // Prevent form submission
    
        const button = document.getElementById('btn-toggle');
        button.disabled = true;  // Disable the button
        document.querySelector('form').submit();
    
        // Re-enable the button and submit the form after 17 seconds (17000 ms)
        setTimeout(() => {
            button.disabled = false;
        }, 17000);
    }