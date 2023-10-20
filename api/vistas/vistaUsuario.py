from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy import func
from flask import jsonify, request
from datetime import datetime, timedelta
import pika 
import json

from api.modelos import db, Usuario, UsuarioSchema

class VistaSignup(Resource):
    
    def post(self):
        # Crea un usuario
        userName = request.json["username"]
        password1 = request.json["password1"]
        password2 = request.json["password2"]
        email = request.json["email"]
        usuario = Usuario.query.filter_by(username=userName).all()
        if usuario:
            return {'mensaje': f'El usuario {userName} ya existe en el sistema'}, 402
        usuario = Usuario.query.filter_by(email=email).all()
        if usuario:
            return {'mensaje': f'El email {email} ya existe en el sistema'}, 402
        if(password1 != password2):
            return {'mensaje':'El password1 es diferente del password2'}, 402
        if not self.validaPassword(password1):
            return {'mensaje':'El password no es válido debe tener mínimo 8 caracteres, una letra mayúscula, una letra minúscula, un número y un carácter especial.'}, 402
        
        nuevo_usuario = Usuario(username=userName, password=password1, email=email)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return {'mensaje':'La cuenta fue creada correctamente'}, 200
    
    def validaPassword(self, password):
        # Valida que el password tenga al menos 8 caracteres
        if len(password) < 8:
            return False

        # Valida que el password contenga al menos una letra minúscula
        if not any(char.islower() for char in password):
            return False

        # Valida que el password contenga al menos una letra mayúscula
        if not any(char.isupper() for char in password):
            return False
        
        # Valida que el password contenga al menos un número
        if not any(char.isdigit() for char in password):
            return False

        # Valida que el password  contenga al menos un carácter especial
        special_characters = "@$!%*?&"
        if not any(char in special_characters for char in password):
            return False

        return True
    
class VistaLogin(Resource):
    
    def post(self):
        # Crea un token con información de usuario y tiempo de expiración
        userName = request.json["username"]
        password = request.json["password"]
        usuario = Usuario.query.filter_by(username=userName, password=password).first()
        if  (usuario):
            expires = timedelta(minutes=30)
            access_token = create_access_token(identity=str(usuario.id), expires_delta=expires)
            return jsonify(access_token=access_token)   
        else:
            return {'mensaje':'Nombre de usuario o contraseña incorrectos'}, 402