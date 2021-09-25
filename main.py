import imghdr
from flask import Flask, render_template, flash, request, redirect, url_for, abort, send_from_directory
from werkzeug.utils import secure_filename
import os
import numpy as np
import pandas as pd

app = Flask(__name__)
app.config["SECRET_KEY"] = "THIS IS MY SECRET KEY"
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif','.jpeg']
app.config['UPLOAD_PATH'] = 'static/images'


def top_10_color(img):
    """To get color from image that's already uploaded"""
    img_array = np.array(img)
    df_img = pd.DataFrame(img_array, columns=["Red", "Green", "Blue"])
    df_color = df_img.groupby(["Red", "Green", "Blue"], as_index=False).size()
    df_color.sort_values(by="size", ascending=False, inplace=True)
    top_10_df_color = df_color[:10].apply(pd.to_numeric)
    top_10_df_color_list = top_10_df_color.values.tolist()
    return top_10_df_color_list


def validate_image(stream):
    """To validate the image prefix"""
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != "bif" else "jpeg")


@app.route("/")
def home():
    files = os.listdir(app.config["UPLOAD_PATH"])
    return render_template("index.html", files=files)


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != "":
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or file_ext != validate_image(uploaded_file.stream):
                abort(404)
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            return redirect(url_for('home'))
    # return render_template("index.html", filename=filename)


@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config["UPLOAD_PATH"], filename)


if __name__ == "__main__":
    app.run(debug=True)