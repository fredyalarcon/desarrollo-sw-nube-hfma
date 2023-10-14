from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from modelos import db

class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    tasks = db.relationship('Task', cascade='all, delete, delete-orphan')
    __table_args__ = (db.UniqueConstraint('username', name='username_unique'),db.UniqueConstraint('email', name='email_unique'))


class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True
        
    id = fields.String()