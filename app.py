from flask import Flask, request, send_file, render_template, redirect, url_for, flash
import os
import uuid
from moviepy.editor import VideoFileClip

app = Flask(__name__)
app.secret_key = "secret-key"

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "ts"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("No file part")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Unsupported file type.")
        return redirect(url_for("index"))

    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        clip = VideoFileClip(filepath)

        # 영상 처리 (여기서는 단순 복사, 필요 시 후방 추출 로직 추가)
        rear_clip = clip
        rear_clip_path = os.path.splitext(filepath)[0] + "_rear.mp4"

        rear_clip.write_videofile(
            rear_clip_path,
            codec="libx264",
            audio=False,
            preset="ultrafast",
            bitrate="500k",
            verbose=False,
            logger=None
        )

        os.remove(filepath)  # 원본 삭제
        return send_file(rear_clip_path, as_attachment=True)

    except Exception as e:
        return f"Error processing video: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
