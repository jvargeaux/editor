from flask import Flask, request, render_template
from pathlib import Path
import json


app = Flask(__name__)
save_directory = Path('documents')
backup_directory = Path('document_backups')


def save_document(id, document):
    file_path = Path(save_directory, f'{id}.html')
    if not Path.exists(save_directory):
        save_directory.mkdir(parents=True)
    with file_path.open("w") as file:
        file.write(document)

def backup_document(id, document):
    file_path = Path(backup_directory, f'{id}.html')
    if not Path.exists(backup_directory):
        backup_directory.mkdir(parents=True)
    with file_path.open("w") as file:
        file.write(document)

def fetch_document(id):
    file_path = Path(save_directory, f'{id}.html')
    if not Path.exists(file_path):
        raise FileNotFoundError(f"Document \"{id}\" not found.")
    with file_path.open("r") as file:
        document = file.read()
        return document


@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/save/<id>", methods=['POST'])
def save(id):
    try:
        document = request.json['document']
        if document is None:
            raise Exception(f"Document \"{id}\" is empty.")
        save_document(id=id, document=document)
        backup_document(id=id, document=document)
        return json.dumps({ "message": "Saved." })
    except Exception as e:
        print(f"ERROR: {e}")
        return json.dumps({ "message": "ERROR: No item \"document\" found." }), 400


@app.route("/fetch/<id>", methods=['POST'])
def fetch(id):
    try:
        document = fetch_document(id=id)
        return json.dumps({
            "message": "Fetched.",
            "document": document
        })
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return json.dumps({ "message": "ERROR: Document not found." }), 404

