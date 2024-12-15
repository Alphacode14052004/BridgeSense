import moviepy.editor as mp
import speech_recognition as sr
from moviepy.editor import VideoFileClip, concatenate_videoclips, clips_array
import os
import tempfile
import vosk
import cv2
def merge_letter_videos(word, assets_folder):
    letter_clips = []
    for letter in word:
        letter_lower = letter.lower()
        letter_video_path = os.path.join(assets_folder, f'{letter_lower}.mp4')
        if os.path.isfile(letter_video_path):
            letter_clip = VideoFileClip(letter_video_path)
            letter_clips.append(letter_clip)
        else:
            print(f"No video found for letter: {letter_lower}")
    if not letter_clips:
        print("No valid videos found for the word.")
        return None
    final_clip = concatenate_videoclips(letter_clips)
    return final_clip
def display_video(video_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if the video opened successfully
    if not cap.isOpened():
        print("Error: Unable to open video file.")
        return

    # Create a window to display the video
    cv2.namedWindow("Combined Video", cv2.WINDOW_NORMAL)

    # Loop through the video frames
    while True:
        # Read a frame from the video
        ret, frame = cap.read()

        # Check if the frame was read successfully
        if not ret:
            # If not, break the loop (end of video)
            break

        # Display the frame in the window
        cv2.imshow("Combined Video", frame)

        # Wait for a key press; waitKey() returns the ASCII value of the key pressed
        key = cv2.waitKey(25) & 0xFF

        # Check if the 'q' key was pressed to exit the loop
        if key == ord('q'):
            break

    # Release the VideoCapture object and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
def extract_audio_as_text(video_path):
    # Initialize Vosk recognizer
    model = vosk.Model(r"C:\Users\jimve\Documents\CEG-HACKATHON\vosk-model-small-en-us-0.15")

    # Create a temporary directory to store audio files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_audio_path = os.path.join(temp_dir, "temp_audio.wav")

        # Extract audio from the video
        video = mp.VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(temp_audio_path)

        # Initialize Vosk recognizer
        recognizer = vosk.KaldiRecognizer(model, audio.samplerate)

        # Transcribe audio using Vosk
        with open(temp_audio_path, "rb") as audio_file:
            while True:
                data = audio_file.read(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    pass

            # Get the final result of transcription
            result = recognizer.FinalResult()
            audio_text = result["text"]

    return audio_text
def merge_word_videos(words, assets_folder):
    video_clips = []
    for word in words:
        word_lower = word.lower()
        word_video_path = os.path.join(assets_folder, f'{word_lower}.mp4')
        if os.path.isfile(word_video_path):
            video_clip = VideoFileClip(word_video_path)
            video_clips.append(video_clip)
        else:
            print(f"No video found for word: {word_lower}")
            print(f"Splitting '{word}' into letters...")
            letter_video = merge_letter_videos(word, assets_folder)
            if letter_video is not None:
                video_clips.append(letter_video)
    if not video_clips:
        print("No valid videos found.")
        return None
    final_clip = concatenate_videoclips(video_clips)
    return final_clip

def extract_audio_as_text(video_path):
    video = mp.VideoFileClip(video_path)
    audio = video.audio
    temp_audio_path = "temp_audio.wav"
    audio.write_audiofile(temp_audio_path)
    r = sr.Recognizer()
    with sr.AudioFile(temp_audio_path) as source:
        audio_data = r.record(source)
        audio_text = r.recognize_google(audio_data)
    return audio_text

def generate_combined_video(extracted_text, video_path):
    words = extracted_text.split()
    assets_folder = 'assets'
    if not words:
        print("Please enter a sentence.")
    else:
        print(f"Generating combined video for text: {extracted_text}...")
        video = merge_word_videos(words, assets_folder)
        if video is not None:
            print("Combined video generated successfully!")
            continuous_video_path = "output_continuous_video.mp4"
            video.write_videofile(continuous_video_path, codec="libx264")
            uploaded_video = VideoFileClip(video_path)
            uploaded_video = uploaded_video.resize(height=video.h)
            final_video = clips_array([[uploaded_video, video]])
            final_video_path = "final_combined_video.mp4"
            final_video.write_videofile(final_video_path, codec="libx264")
            os.remove(continuous_video_path)
            os.remove(video_path)

def main():
    video_path = r"C:\Users\jimve\Documents\CEG-HACKATHON\paithyam.mp4"  # Provide the path to your video
    extracted_text = extract_audio_as_text(video_path)
    print("Extracted Text from Uploaded Video:")
    print(extracted_text)
    generate_combined_video(extracted_text, video_path)
    combined_video_path = "final_combined_video.mp4"

    # Display the combined video in a window
    display_video(combined_video_path)

if __name__ == '__main__':
    main()