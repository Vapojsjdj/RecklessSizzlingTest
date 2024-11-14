from flask import Flask, request, render_template_string
import subprocess
import os

app = Flask(__name__)

# معلومات البث (بناءً على تفاصيل Castr التي زودتنا بها)
stream_url = "rtmp://southafrica.castr.io/static"
stream_key = "live_6c2ff400a29a11efb8c229f603a8387e?password=a1868a0b"
video_path = ""  # سيتم تعيينه بعد رفع الفيديو

# قالب HTML للصفحة الرئيسية
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>بث مباشر</title>
</head>
<body>
    <h2>رفع الفيديو للبث</h2>
    <form action="/" method="post" enctype="multipart/form-data">
        <input type="file" name="video" accept="video/*" required>
        <button type="submit">رفع الفيديو</button>
    </form>
    
    {% if video_uploaded %}
        <form action="/start_stream" method="post">
            <button type="submit">بدء البث المباشر</button>
        </form>
    {% endif %}
</body>
</html>
"""

# تشغيل البث باستخدام ffmpeg
def start_stream():
    command = [
        "ffmpeg",
        "-re",
        "-i", video_path,
        "-vcodec", "libx264",
        "-preset", "veryfast",
        "-maxrate", "3000k",
        "-bufsize", "6000k",
        "-pix_fmt", "yuv420p",
        "-g", "50",
        "-f", "flv",
        f"{stream_url}/{stream_key}"
    ]
    # تشغيل الأمر في الخلفية
    process = subprocess.Popen(command)
    process.wait()

# الصفحة الرئيسية
@app.route("/", methods=["GET", "POST"])
def upload_video():
    global video_path
    video_uploaded = False
    
    if request.method == "POST":
        video = request.files["video"]
        if video:
            video_path = os.path.join("uploads", video.filename)
            video.save(video_path)
            video_uploaded = True
            
    return render_template_string(html_template, video_uploaded=video_uploaded)

# بدء البث
@app.route("/start_stream", methods=["POST"])
def start_stream_route():
    if video_path:
        start_stream()
    return "تم بدء البث المباشر!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)