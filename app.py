import os
from flask import Flask, render_template, jsonify, request
import config
import aiapi
import json
import pathlib
import requests
from flask import Flask, session, abort, redirect
import psycopg2
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import db_functions


app = Flask("Chat GPT")
app.secret_key = "123456789"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

with open("client_secret.json", "r") as file:
    src = json.load(file)
GOOGLE_CLIENT_ID = src["web"]["client_id"]
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='chat_db',
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return "error", 501
        else:
            return function(*args, **kwargs)
    return wrapper


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/chat")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/chat", methods=['POST', 'GET'], endpoint='chat') #/chat/123 такого нет
@login_is_required
def chat():
    uId = 1
    if request.method == 'POST':
        prompt = request.form['prompt']
        conv_id = int(request.form['conv_id']) if request.form['conv_id'] else db_functions.add_conversation(uId)
        print(conv_id)
        res = {'answer': aiapi.generateChatResponse(uId, conv_id, prompt)}
        return jsonify(res), 200
    context = {}
    context['username'] = session["name"]
    return render_template('chat.html', context=context)

@app.route("/backend-api/conversations", methods=['GET'], endpoint='conversations')
@login_is_required
def conversations():
    uId = 1
    offset, limit = request.args.get('offset'), request.args.get('limit')

    if (limit is None or offset is None):
        abort(400)

    convs = db_functions.conversations(uId, limit, offset)

    # books = [
    #     [1,'About C/C++'],
    #     [2, 'Pascal--'],
    #     [3, 'What is a Yopta Script?'],
    # ]

    res = {
        'items': [{ 'id': conv[0] } for conv in convs],
        'offset': offset,
        'limit': limit,
        'total': len(convs)
    }
    return res

@app.route("/backend-api/conversation/<int:conv_id>", methods=['GET'], endpoint='conversation')
@login_is_required
def conversation(conv_id):

    msgs = db_functions.get_messages(conv_id)

    # msgs = [
    #     ["system", "You are a helpful assistant."],
    #     ["user", "You are a helpful assistant."],
    # ]

    title = 'C++' # from front-end
    messages = [{ 'role': msg[0], 'content': msg[1] } for msg in msgs]

    res = {
        'title': title,
        'messages': messages
    }

    return res

@app.route("/")
def index():
    return render_template('sing_in.html')
    # return "Hello World <a href='/login'><button>Login</button></a>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
