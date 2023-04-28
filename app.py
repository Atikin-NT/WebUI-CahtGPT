import os
from flask import Flask, render_template, jsonify, request, make_response, send_from_directory
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


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "uId" not in session:
            return redirect("/")
        else:
            return function(*args, **kwargs)
    return wrapper

@app.route('/sw.js')
def sw():
    response=make_response(
                     send_from_directory('./static', 'sw.js'))
    #change the content header file. Can also omit; flask will handle correctly.
    response.headers['Content-Type'] = 'application/javascript'
    return response

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        return redirect("/")

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID, 
        clock_skew_in_seconds=2
    )

    sub = id_info.get("sub")
    name = id_info.get("name")
    picture = id_info.get("picture")

    user = db_functions.get_uid_by_sub(sub)
    if not user:
        uId = db_functions.add_user(sub, name)
    else:
        uId = user[0][0]
    session["uId"] = uId
    session["name"] = name
    session["picture"] = picture
    return redirect('/chat')


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/chat", methods=['POST', 'GET'], endpoint='chat') #/chat/123 такого нет
@login_is_required
def chat():
    uId = session['uId']
    if request.method == 'POST':
        prompt = request.form['prompt']
        if request.form['conv_id']:
            conv_id = int(request.form['conv_id'])
            author = db_functions.get_author(conv_id)
            if author != uId:
                return jsonify({'answer': 'permission denied'}), 403
            ctx_messages = db_functions.get_messages(conv_id)

            tokens_left = db_functions.tokens_left(uId)
            question, answer, total_tokens_usage, err = aiapi.generateChatResponse(prompt, ctx_messages, tokens_left)
            if total_tokens_usage == 0:
                return jsonify({'answer': err}), 400

        else:
            ctx_messages = []
            
            tokens_left = db_functions.tokens_left(uId)
            question, answer, total_tokens_usage, err = aiapi.generateChatResponse(prompt, ctx_messages, tokens_left)
            if total_tokens_usage == 0:
                return jsonify({'answer': err}), 400
            
            conv_id = db_functions.add_conversation(uId, question['content'])

        db_functions.add_message(question['role'], question['content'], conv_id)
        db_functions.upd_tokens_left(uId, tokens_left - total_tokens_usage)
        
        if not answer:
            return jsonify({'answer': err}), 200
        db_functions.add_message(answer['role'], answer['content'].strip(), conv_id)


        return jsonify({'answer': answer['content'].strip()}), 200
    
    context = {}
    context['username'] = session["name"]
    context['picture'] = session["picture"]
    return render_template('chat.html', context=context)

@app.route("/backend-api/conversations", methods=['GET'], endpoint='conversations')
@login_is_required
def conversations():
    uId = session['uId']
    offset, limit = request.args.get('offset', 0), request.args.get('limit', 20)


    convs = db_functions.conversations(uId, limit, offset)

    # books = [
    #     [1,'About C/C++'],
    #     [2, 'Pascal--'],
    #     [3, 'What is a Yopta Script?'],
    # ]

    res = {
        'items': [{ 'id': conv[0], 'title': conv[1] } for conv in convs],
        'offset': offset,
        'limit': limit,
        'total': len(convs)
    }
    return res

@app.route("/backend-api/conversation/<int:conv_id>", methods=['GET'], endpoint='conversation')
@login_is_required
def conversation(conv_id):
    uId = session['uId'] # does he actually have access?
    msgs = db_functions.get_messages(conv_id)

    # msgs = [
    #     ["system", "You are a helpful assistant."],
    #     ["user", "You are a helpful assistant."],
    # ]

    messages = [{ 'role': msg[0], 'content': msg[1] } for msg in msgs]

    res = {
        'messages': messages
    }

    return res

@app.route("/")
def index():
    return render_template('sing_in.html')
    # return "Hello World <a href='/login'><button>Login</button></a>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
