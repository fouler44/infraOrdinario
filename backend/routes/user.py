from datetime import datetime
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

from crud.user import update_user_puuid

bcrypt = Bcrypt()

user_routes = Blueprint("user", __name__)

@user_routes.route("/", methods=["GET"])
@jwt_required()
def get_authenticated_user():
    username = get_jwt_identity()

    conn = SessionLocal()
    try:
        user = conn.scalars(
            select(AppUser).filter_by(username=username).limit(1)
        ).first()
    finally:
        conn.close()

    if not user:
        code = 404
        return jsonify({
            "code": code,
            "msg": "El usuario proporcionado no existe"
        }), code

    code = 200
    return jsonify({
        "code": code,
        "user": user.data()
    }), code



@user_routes.route("/create", methods=["POST"])
def signup():
    """
    Crea un nuevo usuario (registro).
    """
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        code = 400
        return jsonify({
            "code": code,
            "msg": "Se requiere username y password"
        }), code

    conn = SessionLocal()
    try:
        existing = conn.scalars(
            select(AppUser).filter_by(username=username).limit(1)
        ).first()

        if existing:
            code = 409
            return jsonify({
                "code": code,
                "msg": f"El usuario {username} ya existe"
            }), code

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = AppUser(
            username=username,
            hashed_password=hashed_password,
        )
        conn.add(new_user)
        conn.commit()
    finally:
        conn.close()

    code = 201
    return jsonify({
        "code": code,
        "msg": f"Usuario {username} creado correctamente",
        "created_at": datetime.now().isoformat()
    }), code


@user_routes.route("/edit/pwd", methods=["PUT", "PATCH"])
@jwt_required()
def change_pwd():
    username = get_jwt_identity()
    data = request.get_json() or {}

    current_password = data.get("password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        code = 400
        return jsonify({
            "code": code,
            "msg": "Se requieren 'password' y 'new_password'"
        }), code

    conn = SessionLocal()
    try:
        user = conn.scalars(
            select(AppUser).filter_by(username=username).limit(1)
        ).first()

        if not user:
            code = 404
            return jsonify({
                "code": code,
                "msg": "El usuario proporcionado no existe"
            }), code

        if not bcrypt.check_password_hash(user.data()["hashed_password"], current_password):
            code = 401
            return jsonify({
                "code": code,
                "msg": "Credenciales incorrectas"
            }), code

        hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        user.hashed_password = hashed_password
        conn.add(user)
        conn.commit()
    finally:
        conn.close()

    code = 200
    return jsonify({
        "code": code,
        "msg": "Contraseña actualizada correctamente"
    }), code


@user_routes.route("/edit/puuid", methods=["PUT", "PATCH"])
@jwt_required()
def change_puuid():
    username = get_jwt_identity()
    data = request.get_json() or {}

    puuid = data.get("puuid")
    if not puuid:
        code = 400
        return jsonify({
            "code": code,
            "msg": "Se requiere el parámetro 'puuid'"
        }), code

    conn = SessionLocal()
    try:
        user = conn.scalars(
            select(AppUser).filter_by(username=username).limit(1)
        ).first()

        if not user:
            code = 404
            return jsonify({
                "code": code,
                "msg": "El usuario proporcionado no existe"
            }), code

        update_user_puuid(conn, user.data()["user_id"], puuid)
        conn.commit()
    finally:
        conn.close()

    code = 200
    return jsonify({
        "code": code,
        "msg": f"PUUID del usuario {username} actualizada: {puuid}"
    }), code
    
@user_routes.route("/delete", methods=["DELETE"])
@jwt_required()
def delete_user():
    username = get_jwt_identity()
    data = request.get_json() or {}
    password = data.get("password")

    if not password:
        code = 400
        return jsonify({
            "code": code,
            "msg": "Se requiere 'password' para eliminar la cuenta"
        }), code

    conn = SessionLocal()
    try:
        user = conn.scalars(
            select(AppUser).filter_by(username=username).limit(1)
        ).first()

        if not user:
            code = 404
            return jsonify({
                "code": code,
                "msg": "El usuario proporcionado no existe"
            }), code

        if not bcrypt.check_password_hash(user.data()["hashed_password"], password):
            code = 401
            return jsonify({
                "code": code,
                "msg": "Credenciales incorrectas"
            }), code

        conn.delete(user)
        conn.commit()
    finally:
        conn.close()

    code = 200
    return jsonify({
        "code": code,
        "msg": f"Usuario {username} eliminado"
    }), code