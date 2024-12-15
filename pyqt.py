import os
import sys
import tempfile

import moviepy.editor as mp
import speech_recognition as sr
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFileDialog, QWidget, QTextEdit)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
from moviepy.editor import VideoFileClip, concatenate_videoclips, clips_array


class SignLanguageGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.video_path = None
        self.assets_folder = '/home/venkat/Documents/CEG-HACKATHON/CEG-HACKATHON/VB_Sign/assets'

    def initUI(self):
        self.setWindowTitle('Sign Language Video Generator')
        self.setGeometry(100, 100, 800, 600)

        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Video upload section
        upload_layout = QHBoxLayout()
        upload_btn = QPushButton('Upload Video')
        upload_btn.clicked.connect(self.upload_video)
        upload_layout.addWidget(upload_btn)
        main_layout.addLayout(upload_layout)

        # Extracted text display
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        main_layout.addWidget(QLabel('Extracted Text:'))
        main_layout.addWidget(self.text_display)

        # Video display area
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        main_layout.addWidget(self.video_widget)

        # Generate button
        generate_btn = QPushButton('Generate Sign Language Video')
        generate_btn.clicked.connect(self.generate_combined_video)
        main_layout.addWidget(generate_btn)

    def upload_video(self):
        # Open file dialog to select video
        file_dialog = QFileDialog()
        self.video_path, _ = file_dialog.getOpenFileName(self, 'Select Video', '', 'Video Files (*.mp4)')
        
        if self.video_path:
            # Extract text from uploaded video
            try:
                extracted_text = self.extract_audio_as_text(self.video_path)
                self.text_display.setPlainText(extracted_text)
                
                # Play the original video
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_path)))
                self.media_player.play()
            except Exception as e:
                self.text_display.setPlainText(f'Error extracting text: {str(e)}')

    def merge_letter_videos(self, word):
        letter_clips = []

        for letter in word:
            letter_lower = letter.lower()
            letter_video_path = os.path.join(self.assets_folder, f'{letter_lower}.mp4')

            if os.path.isfile(letter_video_path):
                letter_clip = VideoFileClip(letter_video_path)
                letter_clips.append(letter_clip)

        if not letter_clips:
            print(f"No valid videos found for word: {word}")
            return None

        final_clip = concatenate_videoclips(letter_clips)
        return final_clip

    def merge_word_videos(self, words):
        video_clips = []

        for word in words:
            word_lower = word.lower()
            word_video_path = os.path.join(self.assets_folder, f'{word_lower}.mp4')

            if os.path.isfile(word_video_path):
                video_clip = VideoFileClip(word_video_path)
                video_clips.append(video_clip)
            else:
                print(f"No video found for word: {word_lower}")
                letter_video = self.merge_letter_videos(word)
                if letter_video is not None:
                    video_clips.append(letter_video)

        if not video_clips:
            print("No valid videos found.")
            return None

        final_clip = concatenate_videoclips(video_clips)
        return final_clip

    def extract_audio_as_text(self, video_path):
        video = mp.VideoFileClip(video_path)
        audio = video.audio

        temp_audio_path = "temp_audio.wav"
        audio.write_audiofile(temp_audio_path)

        r = sr.Recognizer()

        with sr.AudioFile(temp_audio_path) as source:
            audio_data = r.record(source)
            audio_text = r.recognize_google(audio_data)

        # Clean up temporary audio file
        os.remove(temp_audio_path)
        return audio_text

    def generate_combined_video(self):
        if not self.video_path:
            print("Please upload a video first.")
            return

        extracted_text = self.text_display.toPlainText()
        words = extracted_text.split()

        if not words:
            print("Please extract text from a video first.")
            return

        print(f"Generating combined video for text: {extracted_text}")
        sign_language_video = self.merge_word_videos(words)

        if sign_language_video is not None:
            continuous_video_path = "output_continuous_video.mp4"
            sign_language_video.write_videofile(continuous_video_path, codec="libx264")

            uploaded_video = VideoFileClip(self.video_path)
            uploaded_video = uploaded_video.resize(height=sign_language_video.h)

            final_video = clips_array([[uploaded_video, sign_language_video]])

            final_video_path = "final_combined_video.mp4"
            final_video.write_videofile(final_video_path, codec="libx264")

            # Play the generated video
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(final_video_path)))
            self.media_player.play()

            # Clean up temporary files
            os.remove(continuous_video_path)
            os.remove(final_video_path)


def main():
    app = QApplication(sys.argv)
    main_window = SignLanguageGenerator()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()