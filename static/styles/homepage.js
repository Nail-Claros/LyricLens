const toggleButton =  document.getElementById("btn-toggle");
let isListening = false;

// Assuming 'toggleButton' is your button element
toggleButton.addEventListener('click', () => {
    isListening = !isListening;

    if (isListening) {
        toggleButton.classList.add('active');
    } else {
        toggleButton.classList.remove('active');
    }
});

// Add touchstart event listener for better mobile responsiveness
toggleButton.addEventListener('touchstart', (event) => {
    isListening = !isListening;

    if (isListening) {
        toggleButton.classList.add('active');
    } else {
        toggleButton.classList.remove('active');
    }
});



function disableButton(event) {
    

    const button = document.getElementById('btn-toggle');
    button.disabled = true;  // Disable the button


    // Re-enable the button and submit the form after 17 seconds (17000 ms)
    setTimeout(() => {
        button.disabled = false;
    }, 17000);
}

function recordAudio() {
    const maxIterations = 3;  // Maximum number of iterations (audio recordings)
    let currentRecord = 0;  // Keep track of the current recording attempt
    let shouldContinue = true; // Flag to control loop continuation


    // Function to record audio
    const recordOne = async () => {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Your browser does not support audio recording.");
            return;
        }


        const audioContext = new AudioContext({ sampleRate: 44100 });
        const stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1 } });
        const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
        const audioChunks = [];


        mediaRecorder.ondataavailable = event => audioChunks.push(event.data);


        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const arrayBuffer = await audioBlob.arrayBuffer();
            const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);


            // Convert audio buffer to WAV (44100Hz, 1 channel, 16-bit PCM)
            const wavBlob = encodeWAV(audioBuffer, 44100, 1); // Ensure it is Mono, 44100Hz
            const formData = new FormData();
            
            // Add the WAV blob to the form data
            formData.append("audio", wavBlob, `recording.wav`);


            // Send the WAV file to Flask server
            const response = await fetch("/upload-audio", {
                method: "POST",
                body: formData
            });


            const responseData = await response.json();


            if (response.ok) {
                console.log(`Audio ${currentRecord + 1} uploaded successfully!`);
                
                // Check if the server response indicates to end the loop and redirect
                if (responseData.endLoop === true) {
                    console.log("Loop broken by server. Redirecting...");


                    // Construct the redirect URL with the returned song_key
                    const redirectUrl = `/detected?key=${responseData.key}`;


                    // Redirect to the constructed URL
                    window.location.href = redirectUrl;
                    return; // Stop further code execution
                }
            } else {
                console.error(`Error uploading audio ${currentRecord + 1}:`, responseData.error);
            }


            stream.getTracks().forEach(track => track.stop());


            if (shouldContinue && currentRecord < maxIterations - 1) {
                currentRecord++;
                setTimeout(() => recordOne(), 1000);
            } else {
                console.log("Reached maximum iterations or loop stopped by server.");
            }
        };


        mediaRecorder.start();
        setTimeout(() => mediaRecorder.stop(), 3500);  // Each recording lasts 3.5 seconds
    };


    // Start the first recording
    recordOne();
}

function encodeWAV(audioBuffer, sampleRate, numChannels) {
    const bitDepth = 16;
    const format = 1; // 1 for PCM (Linear Pulse Code Modulation)
    
    const resultBuffer = new ArrayBuffer(44 + audioBuffer.length * numChannels * (bitDepth / 8));
    const view = new DataView(resultBuffer);

    // Write WAV file header
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + audioBuffer.length * numChannels * (bitDepth / 8), true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true); // Subchunk1Size (16 for PCM)
    view.setUint16(20, format, true); // AudioFormat (1 for PCM)
    view.setUint16(22, numChannels, true); // NumChannels (1 for Mono)
    view.setUint32(24, sampleRate, true); // SampleRate (44100)
    view.setUint32(28, sampleRate * numChannels * (bitDepth / 8), true); // ByteRate
    view.setUint16(32, numChannels * (bitDepth / 8), true); // BlockAlign
    view.setUint16(34, bitDepth, true); // BitsPerSample
    writeString(view, 36, 'data');
    view.setUint32(40, audioBuffer.length * numChannels * (bitDepth / 8), true); // Subchunk2Size

    // Write audio samples (Mono channel data)
    let offset = 44;
    for (let i = 0; i < audioBuffer.length; i++) {
        const sample = Math.max(-1, Math.min(1, audioBuffer.getChannelData(0)[i]));
        view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
        offset += 2;
    }

    return new Blob([view], { type: 'audio/wav' });
}

function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}
