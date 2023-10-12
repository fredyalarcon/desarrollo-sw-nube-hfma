from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from modelos import db
from sqlalchemy import UniqueConstraint


class Task(db.Model):
    __tablename__ = "task"
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(128))
    input_name_file = db.Column(db.String(128))
    output_name_file = db.Column(db.String(128))
    created_at = db.Column(db.DateTime)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "task",
    }

class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()