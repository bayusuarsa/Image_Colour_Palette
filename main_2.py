from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FileField
from flask_uploads import configure_uploads, IMAGES, UploadSet
from PIL import Image
import numpy as np
import pandas as pd


app = Flask(__name__)
app.config["SECRET_KEY"] = "my little secret"
app.config["UPLOADED_IMAGES_DEST"] = 'static/images'

images = UploadSet('images', IMAGES)
configure_uploads(app, images)


class Myform(FlaskForm):
    image = FileField('image')


def top_10_color(img):
    """To get color from image that's already uploaded"""
    img_array = np.array(img)
    img_array = img_array.reshape(-1,3)
    df_img = pd.DataFrame(img_array, columns=["R", "G", "B"])
    df_color = df_img.groupby(["R", "G", "B"], as_index=False).size()
    df_color.sort_values(by="size", ascending=False, inplace=True)
    top_10_df_color = df_color[:10].apply(pd.to_numeric)
    top_10_df_color_list = top_10_df_color.values.tolist()
    return top_10_df_color_list


@app.route("/", methods=["POST", "GET"])
def page():
    form = Myform()
    if form.validate_on_submit():
        filename = images.save(form.image.data)
        img = Image.open(f"static/images/{filename}", "r").convert("RGB")
        palette = top_10_color(img)
        print(palette)
        return render_template("color.html", filename=filename, palette=palette)
    return render_template("main.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)