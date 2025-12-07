import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from config.db import get_session
from crud.player import get_player_by_puuid
from crud.user import get_user_by_username  
from services.link_service import link_account 

player_routes = Blueprint("players", __name__)
    
@player_routes.route("/link", methods=["POST"])
@jwt_required()
def link_lol_account():
    """
    Vincula cuenta de LoL con usuario autenticado y guarda en DB
    """
    with get_session() as db:
        try:
            # Usuario desde JWT
            username = get_jwt_identity()
            
            data = request.get_json()
            game_name = data.get("game_name")
            tag = data.get("tag")
            platform = data.get("platform")
            
            if not all([game_name, tag, platform]):
                return jsonify({
                    "code": 400,
                    "msg": "Faltan parámetros: game_name, tag, platform"
                }), 400
            
            puuid = link_account(
                db=db,
                username=username,
                game_name=game_name,
                tag=tag,
                platform=platform
            )
            
            return jsonify({
                "code": 200,
                "msg": "Cuenta vinculada exitosamente",
                "puuid": puuid
            }), 200
            
        except ValueError as e:
            return jsonify({
                "code": 404,
                "msg": str(e)
            }), 404
        
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            
            if status_code == 401:
                error_msg = "API Key de Riot inválida o expirada. Regenera tu clave en developer.riotgames.com"
            elif status_code == 403:
                error_msg = "Acceso prohibido. Verifica que tu API Key sea válida"
            elif status_code == 404:
                error_msg = f"Jugador '{game_name}#{tag}' no encontrado en la plataforma {platform}"
            elif status_code == 429:
                error_msg = "Demasiadas peticiones. Límite de rate excedido"
            else:
                error_msg = "Error con API de Riot"
            
            return jsonify({
                "code": status_code,
                "msg": error_msg,
                "detail": e.response.text
            }), status_code
        
        except Exception as e:
            return jsonify({
                "code": 500,
                "msg": "Error interno del servidor",
                "detail": str(e)
            }), 500


@player_routes.route("/db/<puuid>", methods=["GET"])
def get_player_from_db(puuid):
    """Obtiene jugador desde la base de datos"""
    with get_session() as db:
        player = get_player_by_puuid(db, puuid)
        
        if not player:
            return jsonify({
                "code": 404,
                "msg": "Jugador no encontrado en la base de datos"
            }), 404
        
        return jsonify({
            "code": 200,
            "data": {
                "puuid": player.puuid,
                "game_name": player.game_name,
                "tagline": player.tagline,
                "platform": player.platform,
                "player_level": player.player_level,
                "player_icon": player.player_icon,
                "updated_at": player.updated_at.isoformat()
            }
        }), 200


@player_routes.route("/me", methods=["GET"])
@jwt_required()
def get_my_player():
    """Obtiene la cuenta de LoL del usuario autenticado"""
    with get_session() as db:
        username = get_jwt_identity()
        user = get_user_by_username(db, username)
        
        if not user:
            return jsonify({
                "code": 404,
                "msg": "Usuario no encontrado"
            }), 404
        
        if not user.puuid:
            return jsonify({
                "code": 404,
                "msg": "Usuario no tiene cuenta de LoL vinculada"
            }), 404
        
        player = get_player_by_puuid(db, user.puuid)
        
        if not player:
            return jsonify({
                "code": 404,
                "msg": "Datos del jugador no encontrados"
            }), 404
        
        return jsonify({
            "code": 200,
            "data": {
                "puuid": player.puuid,
                "game_name": player.game_name,
                "tagline": player.tagline,
                "platform": player.platform,
                "player_level": player.player_level,
                "player_icon": player.player_icon,
                "updated_at": player.updated_at.isoformat()
            }
        }), 200