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
        clip = VideoFileClip(filepath).resize(height=360)
        short_clip = clip.subclip(0, min(10, clip.duration))
        rear_clip_path = os.path.splitext(filepath)[0] + "_rear.mp4"

        short_clip.write_videofile(
            rear_clip_path,
            codec="libx264",
            audio=False,
            preset="ultrafast",
            bitrate="300k",
            threads=1,
            verbose=False,
            logger=None
        )

        os.remove(filepath)
        return send_file(rear_clip_path, as_attachment=True)

    except Exception as e:
        return f"Error processing video: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
