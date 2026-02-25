from flask import Flask, redirect, render_template, request, make_response, jsonify

from mongo_db import (
    add_user,
    get_full_name,
    validate_password,
    get_completed_topics,
    set_topic_completion,
)

import uuid
import os

app = Flask(__name__)

sessions = {} # {session_id: email}
TOTAL_TOPICS = 14


def get_logged_in_email() -> str | None:
    session = request.cookies.get("session")
    if not session:
        return None
    return sessions.get(session)


@app.route('/')
def index():
    session = request.cookies.get("session")
    if not session or not sessions.get(session):
        return redirect("/login")
    return render_template("index.html")


@app.route('/login', methods=['GET'])
def login_get_handler():
    session = request.cookies.get("session")
    if session in sessions:
        return redirect('/')
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login_post_handler():
    form = request.form
    print(form)
    _type = form.get("type")
    if _type == "si":
        email = form.get("email")
        password = form.get("password")
        if not email or not password:
            return render_template("error.html")
        if validate_password(email, password):
            session = str(uuid.uuid4())
            sessions[session] = email
            resp = make_response(redirect('/'))
            resp.set_cookie('session', session)
            return resp
        return render_template("error.html", message="Invalid Credentials.")
    elif _type == "su":
        full_name = form.get("fullname")
        email = form.get("email")
        password = form.get("password")
        if not email or not password or not full_name:
            return "Error", 404
        if get_full_name(email):
            return render_template("error.html", message="User Already Exists.")
        add_user(email, password, full_name)
        session = str(uuid.uuid4())
        sessions[session] = email
        resp = make_response(redirect('/'))
        resp.set_cookie('session', session)
        return resp
    return render_template("error.html")


@app.route('/logout')
def logout_handler():
    session = request.cookies.get("session")
    if session in sessions:
        del sessions[session]
    return redirect("/login")


@app.route('/about')
def about_handler():
    session = request.cookies.get("session")
    if not session or not sessions.get(session):
        return redirect("/login")
    return render_template("about.html")


@app.route('/topics')
def topics_handler():
    if not get_logged_in_email():
        return redirect("/login")
    return render_template("topics.html")


@app.route('/api/topics/progress', methods=['GET'])
def topics_progress_get_handler():
    email = get_logged_in_email()
    if not email:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'completed_topics': get_completed_topics(email)}), 200


@app.route('/api/topics/progress', methods=['POST'])
def topics_progress_post_handler():
    email = get_logged_in_email()
    if not email:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json(silent=True) or {}
    topic_id = data.get('topic_id')
    completed = data.get('completed')

    if not isinstance(topic_id, str) or not topic_id.strip():
        return jsonify({'error': 'Invalid topic_id'}), 400
    if not isinstance(completed, bool):
        return jsonify({'error': 'Invalid completed flag'}), 400

    set_topic_completion(email, topic_id.strip(), completed)
    return jsonify({'ok': True}), 200


@app.route('/api/profile', methods=['GET'])
def profile_handler():
    email = get_logged_in_email()
    if not email:
        return jsonify({'error': 'Unauthorized'}), 401

    completed_topics = get_completed_topics(email)
    return jsonify({
        'full_name': get_full_name(email) or 'Student',
        'email': email,
        'completed_topics_count': len(completed_topics),
        'total_topics': TOTAL_TOPICS
    }), 200


@app.route('/testimonials')
def testimonals_handler():
    session = request.cookies.get("session")
    if not session or not sessions.get(session):
        return redirect("/login")
    return render_template("testimonials.html")


@app.route('/contact')
def contact_handler():
    session = request.cookies.get("session")
    if not session or not sessions.get(session):
        return redirect("/login")
    return render_template("contact.html")

@app.route('/profile')
def profile_handler_page():
    if not get_logged_in_email():
        return redirect("/login")
    return render_template("profile.html")

@app.route('/support')
def support_handler():
    return render_template("support.html")


@app.errorhandler(404)
def errorhandler(e):
    return redirect('/')


if __name__ == "__main__":
    port = int(os.getenv("PORT", 6969))
    app.run(host="0.0.0.0", port=port, debug=True)
