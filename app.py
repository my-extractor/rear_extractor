from flask import Flask, request, send_file
import os
import uuid
from moviepy import editor as mp

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return "Rear extractor is running."

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    clip = mp.VideoFileClip(filepath)
    if len(clip.reader.infos["video_streams"]) < 2:
        return "Error: No second stream found.", 400

    rear_clip = clip.fl(lambda gf, t: gf(t), apply_to=["mask"])
    rear_clip_path = filepath.replace(".mp4", "_rear.mp4").replace(".avi", "_rear.mp4")
    rear_clip.write_videofile(rear_clip_path, codec="libx264")

    os.remove(filepath)  # 원본 삭제

    return send_file(rear_clip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
