from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from moviepy.editor import VideoFileClip, concatenate_videoclips, clips_array
import os
import tempfile
import moviepy.editor as mp
import speech_recognition as sr

app = Flask(__name__)

assets_directory = r'assets'
app.secret_key = "secure_secret_key"

def create_letter_video_sequence(word, assets_directory):
    video_clips = []

    for char in word:
        char_lower = char.lower()
        video_path = os.path.join(assets_directory, f'{char_lower}.mp4')

        if os.path.isfile(video_path):
            video_clip = VideoFileClip(video_path)
            video_clips.append(video_clip)
        else:
            flash(f"No video found for character: {char_lower}", "warning")

    if not video_clips:
        flash("No valid videos found for the word.", "warning")
        return None

    combined_clip = concatenate_videoclips(video_clips)
    return combined_clip

def create_word_video_sequence(phrase, assets_directory):
    video_sequence = []

    for word in phrase:
        word_lower = word.lower()
        word_video_path = os.path.join(assets_directory, f'{word_lower}.mp4')

        if os.path.isfile(word_video_path):
            video_clip = VideoFileClip(word_video_path)
            video_sequence.append(video_clip)
        else:
            flash(f"No video found for word: {word_lower}", "warning")
            flash(f"Attempting to split '{word}' into characters...", "info")
            character_video = create_letter_video_sequence(word, assets_directory)
            if character_video is not None:
                video_sequence.append(character_video)

    if not video_sequence:
        flash("No valid videos found.", "warning")
        return None

    combined_sequence = concatenate_videoclips(video_sequence)
    return combined_sequence

def transcribe_audio_from_video(video_file_path):
    video = mp.VideoFileClip(video_file_path)
    audio = video.audio

    temp_audio_path = "temp_audio.wav"
    audio.write_audiofile(temp_audio_path)

    recognizer = sr.Recognizer()

    with sr.AudioFile(temp_audio_path) as source:
        audio_content = recognizer.record(source)
        transcribed_text = recognizer.recognize_google(audio_content)

    return transcribed_text

def generate_combined_output(transcribed_text, input_video_path):
    words = transcribed_text.split()

    if not words:
        flash("Please enter a sentence.", "warning")
        return redirect(url_for('index'))

    flash(f"Generating combined video for text: {transcribed_text}...", "info")
    combined_video = create_word_video_sequence(words, assets_directory)

    if combined_video is not None:
        flash("Combined video created successfully!", "success")

        output_directory = os.path.join(app.root_path, 'static')
        continuous_output_path = os.path.join(output_directory, "merged_video.mp4")
        combined_video.write_videofile(continuous_output_path, codec="libx264")

        uploaded_clip = VideoFileClip(input_video_path)
        resized_uploaded_clip = uploaded_clip.resize(height=combined_video.h)

        final_combined_output = clips_array([[resized_uploaded_clip, combined_video]])
        final_output_path = os.path.join(output_directory, "final_output.mp4")
        final_combined_output.write_videofile(final_output_path, codec="libx264")

        return os.path.join('static', 'final_output.mp4')

    return None

@app.route("/", methods=["GET", "POST"])
def index():
    generated_video_path = None
    if request.method == "POST":
        uploaded_video = request.files["video_file"]

        if uploaded_video:
            flash("Video uploaded successfully!", "info")

            temp_storage = tempfile.mkdtemp()
            input_video_path = os.path.join(temp_storage, "uploaded_temp_video.mp4")
            uploaded_video.save(input_video_path)

            extracted_text = transcribe_audio_from_video(input_video_path)

            flash("Extracted Text from Uploaded Video:", "success")
            flash(extracted_text, "info")

            generated_video_path = generate_combined_output(extracted_text, input_video_path)

            if not generated_video_path:
                flash("Failed to create the combined video.", "danger")

    return render_template("main.html", video_file=generated_video_path)

if __name__ == "__main__":
    app.run(debug=True)
