from pydub import AudioSegment
import os
import glob

def split_audio(file_path, output_folder, clip_duration=2):

    # Load the audio file
    audio = AudioSegment.from_wav(file_path)
    
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Calculate number of clips
    total_length = len(audio)  # in milliseconds
    clip_length = clip_duration * 1000  # convert seconds to milliseconds
    clips = total_length // clip_length

    # Create clips
    for i in range(clips):
        start_time = i * clip_length
        end_time = start_time + clip_length
        clip = audio[start_time:end_time]
        
        # Save the clip
        clip_file_name = os.path.join(output_folder, f'clip_{i + 1}.wav')
        clip.export(clip_file_name, format='wav')
        print(f'Saved: {clip_file_name}')

    # Handle any remaining audio (for example, if total_length is not perfectly divisible)
    if total_length % clip_length != 0:
        remaining_clip = audio[clips * clip_length:]
        clip_file_name = os.path.join(output_folder, f'clip_{clips + 1}.wav')
        remaining_clip.export(clip_file_name, format='wav')
        print(f'Saved: {clip_file_name}')

def auto_split():
    ##This allows us to clear the clips container
    files = glob.glob('audio_stream/clips/*')
    for f in files:
        os.remove(f)
    #I used this to test the flow of splitter and ensuring the clips
    #folder was indeed cleared properly
    import time
    time.sleep(1)
    split_audio('audio_stream/audio.wav', 'audio_stream/clips', clip_duration=3)



