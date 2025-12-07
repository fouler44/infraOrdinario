import datetime
from flask import Blueprint, request, jsonify, redirect

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from flask_bcrypt import Bcrypt

from config.db import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from models.user import AppUser

bcrypt = Bcrypt()

base_routes = Blueprint("base", __name__)

@base_routes.route("/", methods=["GET"])
def landing():
    code = 200
    return jsonify({
        "code": code,
        "msg": "OK"
    }), code

@base_routes.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        code = 400
        return jsonify({
            "code": code,
            "msg": "Username and password required"
        }), code

    conn = SessionLocal()
    try:
        user = conn.scalars(
            select(AppUser).filter_by(username=username).limit(1)
        ).first()
    finally:
        conn.close()

    if not user or not bcrypt.check_password_hash(user.data()["hashed_password"], password):
        code = 401
        return jsonify({
            "code": code,
            "msg": "Invalid credentials"
        }), code

    access_token = create_access_token(
        identity=username,
        expires_delta=datetime.timedelta(minutes=60)
    )

    code = 200
    return jsonify(access_token=access_token), code

@base_routes.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    user = get_jwt_identity()
    code = 200
    return jsonify({
        "code": code,
        "msg": f"Logged in as {user}"
    }), code
