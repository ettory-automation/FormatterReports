from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename
from datetime import date
import os, base64, io

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "screenshots")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def img_to_base64(path):
    with open(path, "rb") as f:
        ext = os.path.splitext(path)[1][1:]
        data = base64.b64encode(f.read()).decode()
        return f"data:image/{ext};base64,{data}"

def render_report_html(title, exec_date, analyst_name, content_data, hide_download_btn=False):
    return render_template(
        "report.html",
        title=title,
        exec_date=exec_date,
        analyst_name=analyst_name,
        analysis=content_data["analysis"]["text"],
        analysis_prints=content_data["analysis"]["prints"],
        actions=content_data["actions"]["text"],
        actions_prints=content_data["actions"]["prints"],
        tests=content_data["tests"]["text"],
        tests_prints=content_data["tests"]["prints"],
        obs=content_data["obs"]["text"],
        obs_prints=content_data["obs"]["prints"],
        final_analysis=content_data["final_analysis"]["text"],
        final_analysis_prints=content_data["final_analysis"]["prints"],
        hide_download_btn=hide_download_btn
    )

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form.get("title", "relatorio")
        exec_date_val = request.form.get("exec_date", str(date.today()))
        analyst_name = request.form.get("analyst_name", "")

        sections = ["analysis", "actions", "tests", "obs", "final_analysis"]
        sections_files = {
            "analysis": "analysis_files",
            "actions": "actions_files",
            "tests": "tests_files",
            "obs": "obs_files",
            "final_analysis": "final_analysis_files"
        }

        content_data = {}
        for sec in sections:
            text = request.form.get(sec, "")
            files_b64 = []

            uploaded_files = request.files.getlist(sections_files[sec])
            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    save_path = os.path.join(UPLOAD_DIR, filename)

                    counter = 1
                    original_save_path = save_path
                    while os.path.exists(save_path):
                        name, ext = os.path.splitext(original_save_path)
                        save_path = f"{name}_{counter}{ext}"
                        counter += 1

                    file.save(save_path)
                    files_b64.append(img_to_base64(save_path))

            content_data[sec] = {"text": text, "prints": files_b64}

        html_content = render_report_html(title, exec_date_val, analyst_name, content_data)

        return html_content

    return render_template("form.html", today=str(date.today()))

@app.route("/download_html", methods=["POST"])
def download_html():
    title = request.form.get("title", "relatorio")
    exec_date_val = request.form.get("exec_date", str(date.today()))
    analyst_name = request.form.get("analyst_name", "")

    sections = ["analysis", "actions", "tests", "obs", "final_analysis"]
    content_data = {}
    for sec in sections:
        text = request.form.get(sec, "")
        prints = request.form.getlist(f"{sec}_prints")
        content_data[sec] = {"text": text, "prints": prints}

    html_content = render_report_html(title, exec_date_val, analyst_name, content_data, hide_download_btn=True)

    buffer = io.BytesIO()
    buffer.write(html_content.encode("utf-8"))
    buffer.seek(0)

    filename = secure_filename(title) or "relatorio"
    return Response(
        buffer,
        mimetype="text/html",
        headers={"Content-Disposition": f"attachment; filename={filename}.html"}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
