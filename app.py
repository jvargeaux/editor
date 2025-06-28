from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import os
import uuid

import bcrypt._bcrypt
from flask import Flask, request, render_template
from flask_cors import CORS
from stripe import StripeClient
import bcrypt



app = Flask(__name__)
cors = CORS(app)
api_key = ''

stripe_client = StripeClient(api_key)
print(stripe_client)

data_directory = Path('data')
users_path = Path(data_directory, 'users.json')
tokens_path = Path(data_directory, 'tokens.json')
MAX_BACKUPS = 10
BACKUP_INTERVAL = 60  # seconds
DATETIME_FORMAT_BACKEND = "%Y_%m_%d_%H_%M_%S"
DATETIME_FORMAT_FRONTEND = "%Y/%m/%d, %H:%M"
NEW_DOCUMENT = "<p>New Document</p>"



def format_datetime_to_frontend(dt: datetime) -> str:
    return dt.strftime(DATETIME_FORMAT_FRONTEND)


def get_all_users() -> dict:
    if not Path.exists(users_path):
        write_users({})
    with users_path.open("r") as file:
        document = json.load(file)
        return document


def get_all_tokens() -> dict:
    if not Path.exists(tokens_path):
        write_tokens({})
    with tokens_path.open("r") as file:
        document = json.load(file)
        return document


def get_user_documents_manifest(user_id: str) -> dict:
    documents_manifest_path = Path(data_directory, user_id, 'documents.json')
    if not Path.exists(documents_manifest_path):
        return {}
    with documents_manifest_path.open('r') as file:
        documents = json.load(file)
        return documents


def write_users(users: dict):
    with users_path.open("w") as file:
        json.dump(users, file, indent='\t')


def write_tokens(tokens: dict):
    with tokens_path.open("w") as file:
        json.dump(tokens, file, indent='\t')


def write_documents_manifest(user_id: str, documents_manifest: dict):
    documents_manifest_path = Path(data_directory, user_id, 'documents.json')
    with documents_manifest_path.open("w") as file:
        json.dump(documents_manifest, file, indent='\t')


def hash_password(password: str):
    salt = bcrypt.gensalt(log_rounds=12)
    hashed = bcrypt.hashpw(password, salt)
    return hashed


def does_password_match(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password, hashed)


def create_new_user(email: str, password: str):
    # Check if email already exists
    users = get_all_users()
    emails = [user['email'] for user in users.values()]
    if email in emails:
        raise NameError

    # Distribute user ID
    new_id = uuid.uuid4()
    while str(new_id) in list(users.keys()):
        print(f'ID {str(new_id)} exists, trying again.')
        new_id = uuid.uuid4()
    print(new_id)

    # Save user
    users[str(new_id)] = {
        'id': str(new_id),
        'email': email, 
        'password_hash': hash_password(password)
    }
    write_users(users)

    # Create user directory
    user_directory = Path(data_directory, str(new_id))
    if not Path.exists(user_directory):
        user_directory.mkdir(parents=True)


def pruned_user_data(user: dict) -> dict:
    pruned_user = user
    del pruned_user['password_hash']
    return pruned_user


def authenticate_user(email: str, password: str) -> str:
    # Check email
    users = get_all_users()
    matching_users = [id for id, user in users.items() if user['email'] == email]
    if len(matching_users) < 1:
        raise NameError
    if len(matching_users) > 1:
        print(f'ERROR: More than one user with email "{email}".')
    user_id = matching_users[0]

    # Check password
    user = users[user_id]
    if not does_password_match(password, user['password_hash']):
        raise ValueError
    
    # Prune all old tokens
    session_tokens = get_all_tokens()
    session_tokens = { token: id for token, id in session_tokens.items() if id != user_id }

    # Distribute new token
    new_token = uuid.uuid4()
    while str(new_token) in list(session_tokens.keys()):
        print(f'Token {str(new_token)} exists, trying again.')
        new_token = uuid.uuid4()
    session_tokens[str(new_token)] = user_id
    write_tokens(session_tokens)
    return str(new_token)


def authenticate_session_token(token: str) -> dict:
    session_tokens = get_all_tokens()
    if token not in list(session_tokens.keys()):
        raise NameError
    return session_tokens[token]


def does_document_id_exist(user_id: str, document_id: str) -> bool:
    user_directory = Path(data_directory, user_id, 'documents')
    user_backup_directory = Path(data_directory, user_id, 'document_backups')

    document_ids = [item.stem for item in list(user_directory.glob('*.html'))]
    backup_ids = [item.stem for item in list(user_backup_directory.glob('*/'))]
    all_document_ids = set(document_ids + backup_ids)

    return str(document_id) in all_document_ids


def get_user_documents(user_id: str) -> list:
    # user_directory = Path(data_directory, user_id, 'documents')
    # if not Path.exists(user_directory):
    #     return []
    
    # files = list(sorted(user_directory.glob('*.html')))
    # return [file.stem for file in files]

    documents = get_user_documents_manifest(user_id)
    return documents


def get_last_backup_datetime(user_id: str, document_id: str) -> datetime:
    save_directory = Path(data_directory, user_id, 'document_backups', document_id)
    if not Path.exists(save_directory):
        raise FileNotFoundError

    # Take filename from most recent file
    files = list(sorted(save_directory.glob('*.html')))
    timestamp = str(files[-1]).split(".html")[0]

    timestamp = timestamp[-19:]  # Ex: 2025_03_20_22_35_25
    assert len(timestamp) == 19

    return datetime.strptime(timestamp, DATETIME_FORMAT_BACKEND)


def should_backup_document(user_id: str, document_id: str):
    try:
        date = get_last_backup_datetime(user_id=user_id, document_id=document_id)
        seconds_elapsed = (datetime.now() - date).total_seconds()
        return seconds_elapsed > BACKUP_INTERVAL
    except AssertionError:
        return True
    except FileNotFoundError:
        return True


def get_title_from_document(document: str) -> str:
    # Get text between first tags
    # If find returns -1, find+1 will be 0, and document[find+1] will return the entire string
    title = document[document.find('<')+1:]
    return title[title.find('>')+1:title.find('<')]


def save_document(user_id: str, document_id: str, document: str):
    save_directory = Path(data_directory, user_id, 'documents')
    file_path = Path(save_directory, f'{document_id}.html')
    if not Path.exists(save_directory):
        save_directory.mkdir(parents=True)
    with file_path.open("w") as file:
        file.write(document)
    
    documents = get_user_documents_manifest(user_id=user_id)
    documents[document_id] = {
        'id': document_id,
        'title': get_title_from_document(document),
        'last_updated': 'idk'
    }
    write_documents_manifest(user_id=user_id, documents_manifest=documents)



def backup_document(user_id: str, document_id: str, document: str):
    now = datetime.now(tz=timezone(timedelta(hours=+9))).strftime(DATETIME_FORMAT_BACKEND)

    save_directory = Path(data_directory, user_id, 'document_backups', document_id)
    file_path = Path(save_directory, f'{document_id}_{now}.html')
    if not Path.exists(save_directory):
        save_directory.mkdir(parents=True)
    with file_path.open("w") as file:
        file.write(document)

    # Delete oldest file if max limit is exceeded
    files = list(sorted(save_directory.glob('*.html')))
    if len(files) > MAX_BACKUPS:
        try:
            os.remove(files[0])
        except OSError as error:
            print(error)


def fetch_document(user_id: str, document_id: str):
    file_path = Path(data_directory, user_id, 'documents', f'{document_id}.html')
    if not Path.exists(file_path):
        raise FileNotFoundError
    
    last_saved = None
    try:
        last_saved = get_last_backup_datetime(user_id=user_id, document_id=document_id)
    except FileNotFoundError:
        last_saved = datetime.now()
    
    with file_path.open("r") as file:
        document = file.read()
        return document, last_saved


@app.before_request
def authenticate():
    # Only POST requests need authentication
    if request.method == 'GET' or request.endpoint == 'login' or request.endpoint == 'stripe_webhook':
        return

    token = request.headers.get('authorization')
    if token is None:
        return json.dumps({ "message": "ERROR: No auth token provided." }), 403
    try:
        user_id = authenticate_session_token(token)
        request.user_id = user_id
        print(user_id)
    except NameError:
        print(f'ERROR: Unauthorized token "{token}".')
        return json.dumps({ "message": "ERROR: Unauthorized token." }), 403


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/login/", methods=['POST'])
def login():
    body = request.json
    email = body['email']
    password = body['password']
    try:
        token = authenticate_user(email=email, password=password)
        print(token)
        return json.dumps({
            "message": "Login success.",
            "token": token
        }), 200
    except NameError:
        print(f'User with email "{email}" not found.')
        return json.dumps({ "message": "User not found." }), 400
    except ValueError:
        print(f'Password incorrect.')
        return json.dumps({ "message": "Password incorrect." }), 400


@app.route("/fetch_all", methods=['POST'])
def fetch_all():
    documents = get_user_documents(user_id=request.user_id)
    return json.dumps({
        "message": "Fetched.",
        "documents": documents
    }), 200


@app.route("/fetch/<id>", methods=['POST'])
def fetch(id):
    try:
        document, last_saved = fetch_document(user_id=request.user_id, document_id=id)
        return json.dumps({
            "message": "Fetched.",
            "document": document,
            "last_saved": format_datetime_to_frontend(last_saved)
        }), 200
    except FileNotFoundError:
        print(f"ERROR: Document \"{id}\" not found.")
        return json.dumps({ "message": "ERROR: Document not found." }), 404


@app.route("/save/<id>", methods=['POST'])
def save(id):
    try:
        document = request.json['document']
        if document is None:
            raise Exception(f"Document \"{id}\" is empty.")
        
        save_document(user_id=request.user_id, document_id=id, document=document)
        message = "Saved."
        if should_backup_document(user_id=request.user_id, document_id=id):
            message += " Backed up."
            backup_document(user_id=request.user_id, document_id=id, document=document)
        
        return json.dumps({
            "message": message,
            "last_saved": format_datetime_to_frontend(datetime.now())
        }), 200
    except Exception as e:
        print(f"ERROR: {e}")
        return json.dumps({ "message": "ERROR: No item \"document\" found." }), 400


@app.route("/new", methods=['POST'])
def new():
    new_id = uuid.uuid4()
    while does_document_id_exist(user_id=request.user_id, document_id=new_id):
        print(f'ID {str(new_id)} exists, trying again.')
        new_id = uuid.uuid4()
    print(new_id)

    save_document(user_id=request.user_id, document_id=new_id, document=NEW_DOCUMENT)

    return json.dumps({
        "message": "Saved new document.",
        "id": str(new_id),
        "last_saved": format_datetime_to_frontend(datetime.now())
    }), 200


@app.route("/stripe_webhook", methods=['POST'])
def stripe_webhook():
    print('stripe')
    pass


@app.route("/test/", methods=['POST'])
def test():
    print('Test')

    email = 'jvargeaux@gmail.com'
    password = 'asdf'

    # try:
    #     create_new_user(email=email, password=password)
    # except NameError:
    #     print(f'User with email "{email} already exists. Create user aborted."')
    
    # try:
    #     token = authenticate_user(email=email, password=password)
    #     print(token)
    # except NameError:
    #     print(f'User with email "{email}" not found.')
    # except ValueError:
    #     print(f'Password incorrect.')
    
    return json.dumps({}), 200


if __name__ == '__main__':
    pass
