#!/usr/bin/env python3
"""
Flask application for user authentication service
"""
from flask import Flask, jsonify, request, abort, redirect
from auth import Auth

app = Flask(__name__)
AUTH = Auth()


@app.route("/", methods=["GET"])
def index():
    """Home endpoint
    
    Returns:
        JSON payload with welcome message
    """
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=["POST"])
def users():
    """Register a user
    
    Expected form data:
        - email: User's email
        - password: User's password
        
    Returns:
        JSON payload with user info or error message
    """
    email = request.form.get("email")
    password = request.form.get("password")
    
    try:
        user = AUTH.register_user(email, password)
        return jsonify({"email": user.email, "message": "user created"}), 200
    except ValueError:
        return jsonify({"message": "email already registered"}), 400


@app.route("/sessions", methods=["POST"])
def login():
    """Login endpoint
    
    Expected form data:
        - email: User's email
        - password: User's password
        
    Returns:
        JSON payload with user info and session cookie
    """
    email = request.form.get("email")
    password = request.form.get("password")
    
    if not AUTH.valid_login(email, password):
        abort(401)
    
    session_id = AUTH.create_session(email)
    response = jsonify({"email": email, "message": "logged in"})
    response.set_cookie("session_id", session_id)
    return response, 200


@app.route("/sessions", methods=["DELETE"])
def logout():
    """Logout endpoint
    
    Expected:
        - session_id cookie
        
    Returns:
        Redirect to index or 403 error
    """
    session_id = request.cookies.get("session_id")
    user = AUTH.get_user_from_session_id(session_id)
    
    if user is None:
        abort(403)
    
    AUTH.destroy_session(user.id)
    return redirect("/", code=302)


@app.route("/profile", methods=["GET"])
def profile():
    """User profile endpoint
    
    Expected:
        - session_id cookie
        
    Returns:
        JSON payload with user email or 403 error
    """
    session_id = request.cookies.get("session_id")
    user = AUTH.get_user_from_session_id(session_id)
    
    if user is None:
        abort(403)
    
    return jsonify({"email": user.email}), 200


@app.route("/reset_password", methods=["POST"])
def get_reset_password_token():
    """Get reset password token endpoint
    
    Expected form data:
        - email: User's email
        
    Returns:
        JSON payload with email and reset token or 403 error
    """
    email = request.form.get("email")
    
    try:
        reset_token = AUTH.get_reset_password_token(email)
        return jsonify({"email": email, "reset_token": reset_token}), 200
    except ValueError:
        abort(403)


@app.route("/reset_password", methods=["PUT"])
def update_password():
    """Update password endpoint
    
    Expected form data:
        - email: User's email
        - reset_token: Reset token
        - new_password: New password
        
    Returns:
        JSON payload with updated info or 403 error
    """
    email = request.form.get("email")
    reset_token = request.form.get("reset_token")
    new_password = request.form.get("new_password")
    
    try:
        AUTH.update_password(reset_token, new_password)
        return jsonify({"email": email, "message": "Password updated"}), 200
    except ValueError:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
