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