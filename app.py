from flask import Flask, render_template, request, send_from_directory
import os

app = Flask(__name__)

VIDEO_FOLDER = os.path.join(os.getcwd(), 'assets')
RECORDS_FOLDER = os.path.join(os.getcwd(), 'records')

# Make sure the records folder exists
os.makedirs(RECORDS_FOLDER, exist_ok=True)

@app.route('/')
def index():
    videos = [os.path.splitext(f)[0] for f in os.listdir(VIDEO_FOLDER) if os.path.isfile(os.path.join(VIDEO_FOLDER, f))]
    return render_template('index.html', videos=videos)

@app.route('/assets/<video_name>')
def get_video(video_name):
    video_path = os.path.join(VIDEO_FOLDER, f"{video_name}.mp4")
    if os.path.exists(video_path):
        return send_from_directory(VIDEO_FOLDER, f"{video_name}.mp4")
    else:
        return "Video not found", 404

@app.route('/upload', methods=['POST'])
def upload_video():
    video = request.files.get('video')
    if video:
        video_name = video.filename
        save_path = os.path.join(RECORDS_FOLDER, video_name)
        video.save(save_path)
        return 'Video uploaded successfully!', 200
    else:
        return 'No video file received', 400

if __name__ == '__main__':
    app.run(debug=True)
