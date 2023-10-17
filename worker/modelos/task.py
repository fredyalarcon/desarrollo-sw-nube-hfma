from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .modelos import db
from sqlalchemy import func, Enum

class Task(db.Model):
    __tablename__ = "task"
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(Enum('processed', 'uploaded', name='state'), nullable=False)
    input_name_file = db.Column(db.String(128), nullable=False)
    output_name_file = db.Column(db.String(128))
    created_at = db.Column(db.TIMESTAMP, server_default=func.now(), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

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