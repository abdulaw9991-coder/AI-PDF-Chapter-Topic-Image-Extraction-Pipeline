
from flask import Flask, render_template, request
from pdf_processor import process_pdf
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PDF_DATA = {}
BOOK_NAME = ""


# ------------------ HOME ------------------
# Tell Flask to trigger this function when someone visits the main homepage URL 
@app.route("/")
def home():
    return render_template("index.html")


# ------------------ UPLOAD PDF ------------------
@app.route("/upload", methods=["POST"])
def upload():

    global PDF_DATA, BOOK_NAME
# Grab the uploaded PDF file object sent from the HTML form
    file = request.files["pdf"]

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    data, book_name = process_pdf(path)

    PDF_DATA = data
    BOOK_NAME = book_name

    return render_template(
        "index.html",
        data=PDF_DATA,
        book_name=BOOK_NAME
    )


# ------------------ SEARCH FUNCTION ------------------
@app.route("/search", methods=["POST"])
def search():

    query = request.form["query"].lower()

    results = {}

    for chapter, topics in PDF_DATA.items():

        for topic, content in topics.items():

            if (
                query in chapter.lower()
                or query in topic.lower()
                or query in content["text"].lower()
            ):
                results[f"{chapter} → {topic}"] = content

    return render_template(
        "index.html",
        data=PDF_DATA,
        search_results=results,
        book_name=BOOK_NAME
    )


if __name__ == "__main__":
    app.run(debug=True)