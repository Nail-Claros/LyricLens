const toggleButton =  document.getElementById("btn-toggle");
const modal = document.getElementById('modal');
const closeModal = document.querySelector('.close');
let isListening = false;
let stream;
let songRecongizeTimeout;

function showSongDetails(songName, artistName, albumCoverUrl, lyrics)
{
    document.getElementById('song-name').textContent = songName;
    document.getElementById('artist-name').textContent = artistName;
    document.getElementById('album-cover').src = albumCoverUrl;
    modal.style.display = "block";
}

//replace logic later 
function simulateSongRecongize()
{
    console.log("Start listening for Song");

    songRecongizeTimeout = setTimeout(() =>{
        console.log("Song Recongized!");
        stopListening();
        showSongDetails(
            'Example Song', 
            'Artist Example', 
            'https://via.placeholder.com/80', 
            'Sample native lyrics of the song...'
        );
        alert("Song Recongized!");
    }, 5000);
}

async function startListening()
{
    try {
        stream = await navigator.mediaDevices.getUserMedia({audio: true});
        console.log("Microphone access granted.");
        simulateSongRecongize();
    } catch (error) {
        console.error('Microphone access denied: ', error); 
    }
}

function stopListening()
{
    if(stream){
            const tracks = stream.getTracks();
            tracks.forEach(track => track.stop());
    }
    clearTimeout(songRecongizeTimeout);
    console.log('Stopped listening.');
    toggleButton.classList.remove('active');
    isListening = false;
}

toggleButton.addEventListener('click', () => 
    {
        isListening = !isListening;

        if(isListening)
        {
            toggleButton.classList.add('active');
            startListening();
        }
        else
        {
            toggleButton.classList.remove('active');
            stopListening();
        }
    });


closeModal.addEventListener('click', () =>
    {
        modal.style.display = "none";
    });