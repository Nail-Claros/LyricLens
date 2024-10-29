const toggleButton =  document.getElementById("btn-toggle");
const modal = document.getElementById('modal');
const closeModal = document.querySelector('.close');
let isListening = false;
let stream;
let songRecongizeTimeout;

function showSongDetails()
{
    
    modal.style.display = "block";
}

//replace logic later 
function simulateSongRecongize()
{
    console.log("Start listening for Song");

    songRecongizeTimeout = setTimeout(() =>{
        console.log("Song Recongized!");
        showSongDetails();
    }, 3000);
}

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